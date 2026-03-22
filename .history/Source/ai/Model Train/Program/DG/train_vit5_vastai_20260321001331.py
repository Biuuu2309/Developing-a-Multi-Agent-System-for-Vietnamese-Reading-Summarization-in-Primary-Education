# ================================================================
# ViT5 Vietnamese Summarization — Optuna HPO + Final Training
# Optimized for vast.ai RTX 3090 (24GB VRAM), budget < $0.5/hr
# Features: checkpoint/resume, anti-hallucination, OOM-safe
# ================================================================

import os, gc, json, logging, signal, sys
import numpy as np
import pandas as pd
import torch
import optuna
import evaluate
from pathlib import Path
from datasets import Dataset
from transformers import (
    AutoTokenizer, AutoModelForSeq2SeqLM,
    Seq2SeqTrainer, Seq2SeqTrainingArguments,
    DataCollatorForSeq2Seq, EarlyStoppingCallback,
    GenerationConfig,
)

# ────────────────────────────────────────────────────────────────
# HELPER: VRAM monitor + cleanup
# ────────────────────────────────────────────────────────────────
def log_vram(tag: str = ""):
    if torch.cuda.is_available():
        alloc  = torch.cuda.memory_allocated() / 1e9
        reserv = torch.cuda.memory_reserved()  / 1e9
        log.info(f"   VRAM [{tag}] allocated={alloc:.2f}GB | reserved={reserv:.2f}GB")

def aggressive_cleanup(trainer=None, model=None, data_collator=None):
    if trainer is not None:
        trainer.model            = None
        trainer.optimizer        = None
        trainer.lr_scheduler     = None
        trainer.callback_handler = None
        trainer._past            = None
        del trainer
    if model is not None:
        model.cpu()
        del model
    if data_collator is not None:
        del data_collator
    for _ in range(3):
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
    gc.collect()
    gc.collect()

# ────────────────────────────────────────────────────────────────
# 0. LOGGING
# ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("/workspace/training.log"),
    ],
)
log = logging.getLogger(__name__)

# ────────────────────────────────────────────────────────────────
# 1. CONFIG
# ────────────────────────────────────────────────────────────────
CFG = {
    "data_path"      : "/workspace/DATA_DG_work.xlsx",
    "output_dir"     : "/workspace/outputs",
    "study_db"       : "/workspace/optuna_study.db",
    "best_params_fp" : "/workspace/outputs/best_params.json",
    "final_model_dir": "/workspace/outputs/final_model",
    "model_name"     : "VietAI/vit5-base-vietnews-summarization",
    "seed"           : 42,
    "n_trials"       : 18,
    "max_input_len"  : 768,
    "test_size"      : 0.1,
}

os.makedirs(CFG["output_dir"], exist_ok=True)
torch.manual_seed(CFG["seed"])
np.random.seed(CFG["seed"])

# ────────────────────────────────────────────────────────────────
# 2. GRACEFUL SHUTDOWN
# ────────────────────────────────────────────────────────────────
_study_ref = None

def _handle_signal(sig, frame):
    log.warning(f"Received signal {sig}. Exiting gracefully...")
    if _study_ref is not None:
        try:
            trials_done = len([t for t in _study_ref.trials if t.state.is_finished()])
            log.info(f"   Trials saved: {trials_done}/{CFG['n_trials']}")
            log.info(f"   Re-run script to RESUME from trial {trials_done}")
        except Exception:
            pass
    sys.exit(0)

signal.signal(signal.SIGTERM, _handle_signal)
signal.signal(signal.SIGINT,  _handle_signal)

# ────────────────────────────────────────────────────────────────
# 3. LOAD & VALIDATE DATA
# ────────────────────────────────────────────────────────────────
log.info("Loading data...")
df = pd.read_excel(CFG["data_path"], engine="openpyxl")
assert {"content", "summary", "grade"}.issubset(df.columns), \
    "Excel phai co du 3 cot: content, summary, grade"

# Chi dropna tren 3 cot can thiet — tranh mat data vi cot khac NaN
df = df.dropna(subset=["content", "summary", "grade"]).reset_index(drop=True)
df["content_len"] = df["content"].str.split().str.len()
df["summary_len"]  = df["summary"].str.split().str.len()

log.info(f"   [Truoc loc] {len(df)} rows")
log.info(f"   content_len - min: {df['content_len'].min()}, "
         f"mean: {df['content_len'].mean():.0f}, "
         f"p95: {df['content_len'].quantile(0.95):.0f}, "
         f"max: {df['content_len'].max()}")
log.info(f"   summary_len - min: {df['summary_len'].min()}, "
         f"mean: {df['summary_len'].mean():.0f}, "
         f"p95: {df['summary_len'].quantile(0.95):.0f}, "
         f"max: {df['summary_len'].max()}")

# Chi loc content duoi 250 tu
df = df[df["content_len"] >= 250].reset_index(drop=True)
log.info(f"Dataset: {len(df)} rows sau khi loc content < 250 tu")

_p95_summary_words    = df["summary_len"].quantile(0.95)
_suggested_max_target = min(512, int(_p95_summary_words * 1.5))
log.info(f"   p95 summary = {_p95_summary_words:.0f} tu "
         f"-> goi y max_target_len ~ {_suggested_max_target} tokens")

df = df.drop(columns=["content_len", "summary_len"])

# ────────────────────────────────────────────────────────────────
# 4. TOKENIZER
# ────────────────────────────────────────────────────────────────
log.info(f"Loading tokenizer: {CFG['model_name']}")
tokenizer = AutoTokenizer.from_pretrained(CFG["model_name"], use_fast=False)

# ────────────────────────────────────────────────────────────────
# 5. PREPROCESSING
# ────────────────────────────────────────────────────────────────
def make_prompt(content: str, grade) -> str:
    return (
        f"Tom tat va dien giai van ban sau day danh cho hoc sinh lop {grade}. "
        f"Dung ngon ngu don gian, ro rang, phu hop lua tuoi. "
        f"Khong them thong tin ngoai van ban goc:\n{content}"
    )

def preprocess(examples, max_target_len: int):
    prompts = [make_prompt(c, g) for c, g in zip(examples["content"], examples["grade"])]
    model_inputs = tokenizer(
        prompts,
        truncation=True,
        max_length=CFG["max_input_len"],
        padding=False,
    )
    # Dung text_target thay vi as_target_tokenizer (deprecated)
    labels = tokenizer(
        text_target=examples["summary"],
        truncation=True,
        max_length=max_target_len,
        padding=False,
    )
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

raw_ds = Dataset.from_pandas(df)
split   = raw_ds.train_test_split(test_size=CFG["test_size"], seed=CFG["seed"])

_tok_cache: dict = {}

def get_datasets(max_target_len: int) -> dict:
    if max_target_len not in _tok_cache:
        log.info(f"   Tokenizing (max_target_len={max_target_len})...")
        fn = lambda x: preprocess(x, max_target_len)
        _tok_cache[max_target_len] = {
            k: v.map(fn, batched=True, remove_columns=v.column_names)
            for k, v in split.items()
        }
    return _tok_cache[max_target_len]

# ────────────────────────────────────────────────────────────────
# 6. METRICS
# ────────────────────────────────────────────────────────────────
rouge = evaluate.load("rouge")

def compute_metrics(eval_pred):
    preds, labels = eval_pred

    # Fix 1: neu la tuple lay phan tu dau
    if isinstance(preds, tuple):
        preds = preds[0]

    # Fix 2: neu la logits (3D) thi lay argmax
    if preds.ndim == 3:
        preds = preds.argmax(axis=-1)

    # Fix 3: replace -100 trong labels
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)

    # Fix 4: clip preds tranh out of range
    preds = np.clip(preds, 0, tokenizer.vocab_size - 1)

    decoded_preds  = tokenizer.batch_decode(preds, skip_special_tokens=True)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
    decoded_preds  = [p.strip() for p in decoded_preds]
    decoded_labels = [l.strip() for l in decoded_labels]

    r = rouge.compute(predictions=decoded_preds, references=decoded_labels, use_stemmer=True)
    r["avg_rouge"] = (r["rouge1"] + r["rouge2"] + r["rougeL"]) / 3
    return r

# ────────────────────────────────────────────────────────────────
# 7. OPTUNA OBJECTIVE
# ────────────────────────────────────────────────────────────────
def objective(trial: optuna.Trial) -> float:

    max_target_len  = trial.suggest_categorical("max_target_len", [192, 256])
    learning_rate   = trial.suggest_float("learning_rate", 5e-5, 2e-4, log=True)
    batch_size      = trial.suggest_categorical("batch_size", [8, 16])
    grad_acc        = trial.suggest_categorical("grad_acc", [1, 2])
    num_epochs      = trial.suggest_int("num_train_epochs", 3, 5)
    weight_decay    = trial.suggest_float("weight_decay", 1e-3, 3e-2, log=True)
    warmup_ratio    = trial.suggest_categorical("warmup_ratio", [0.05, 0.10, 0.15])
    label_smoothing = trial.suggest_categorical("label_smoothing", [0.0, 0.05, 0.10])

    ds        = get_datasets(max_target_len)
    trial_dir = os.path.join(CFG["output_dir"], f"trial_{trial.number}")

    args = Seq2SeqTrainingArguments(
        output_dir=trial_dir,

        evaluation_strategy="epoch",
        save_strategy="epoch",
        logging_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="eval_avg_rouge",
        greater_is_better=True,
        save_total_limit=1,

        learning_rate=learning_rate,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=8,
        gradient_accumulation_steps=grad_acc,
        num_train_epochs=num_epochs,

        weight_decay=weight_decay,
        warmup_ratio=warmup_ratio,
        lr_scheduler_type="cosine",

        label_smoothing_factor=label_smoothing,
        max_grad_norm=1.0,

        fp16=True,
        gradient_checkpointing=True,
        optim="adafactor",

        # Seq2Seq specific — predict bang generate thay vi logits
        predict_with_generate=True,
        generation_max_length=max_target_len,
        generation_num_beams=1,      # beam=1 khi Optuna de eval nhanh

        dataloader_num_workers=4,
        dataloader_pin_memory=True,
        report_to="none",
        seed=CFG["seed"],
        disable_tqdm=False,
    )

    log_vram(f"start trial {trial.number}")
    model = AutoModelForSeq2SeqLM.from_pretrained(CFG["model_name"])
    model.config.use_cache = False

    data_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer, model=model,
        padding=True, pad_to_multiple_of=8,
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=args,
        train_dataset=ds["train"],
        eval_dataset=ds["test"],
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
    )

    trainer.train()

    eval_logs  = [l for l in trainer.state.log_history if "eval_avg_rouge" in l]
    best_score = max((l["eval_avg_rouge"] for l in eval_logs), default=0.0)
    log.info(f"   Trial {trial.number} best avg_rouge = {best_score:.4f}")

    log_vram(f"before cleanup trial {trial.number}")
    aggressive_cleanup(trainer=trainer, model=model, data_collator=data_collator)
    log_vram(f"after cleanup trial {trial.number}")

    return best_score


def _trial_callback(study: optuna.Study, trial: optuna.Trial):
    done = len([t for t in study.trials if t.state.is_finished()])
    log.info(
        f"\n{'='*55}\n"
        f"  Trial #{trial.number:02d}/{CFG['n_trials']} | "
        f"Score: {trial.value:.4f} | Best: {study.best_value:.4f}\n"
        f"  Params: {trial.params}\n"
        f"  Progress: {done}/{CFG['n_trials']} trials\n"
        f"{'='*55}"
    )

# ────────────────────────────────────────────────────────────────
# 8. RUN OPTUNA
# ────────────────────────────────────────────────────────────────
log.info(f"Starting Optuna ({CFG['n_trials']} trials)...")
log.info(f"   DB: {CFG['study_db']} <- resume tu dong khi chay lai")

study = optuna.create_study(
    direction="maximize",
    study_name="vit5_summarization_v2",
    storage=f"sqlite:///{CFG['study_db']}",
    load_if_exists=True,
)
_study_ref = study

already_done = len([t for t in study.trials if t.state.is_finished()])
remaining    = max(0, CFG["n_trials"] - already_done)
log.info(f"   Completed: {already_done} | Remaining: {remaining}")

if remaining > 0:
    study.optimize(
        objective,
        n_trials=remaining,
        callbacks=[_trial_callback],
        show_progress_bar=True,
        gc_after_trial=True,
    )
else:
    log.info("All trials done. Skipping Optuna.")

best_params = study.best_params
log.info(f"Best avg_rouge : {study.best_value:.4f}")
log.info(f"Best params    :\n{json.dumps(best_params, indent=2, ensure_ascii=False)}")

with open(CFG["best_params_fp"], "w", encoding="utf-8") as f:
    json.dump({**best_params, "best_avg_rouge": study.best_value}, f, indent=2, ensure_ascii=False)
log.info(f"   Saved -> {CFG['best_params_fp']}")

# ────────────────────────────────────────────────────────────────
# 9. FINAL TRAINING
# ────────────────────────────────────────────────────────────────
log.info("Starting final training with best hyperparameters...")

if Path(CFG["final_model_dir"]).exists() and \
   (Path(CFG["final_model_dir"]) / "config.json").exists():
    log.info("Final model already exists. Skipping.")
else:
    full_tokenized = raw_ds.map(
        lambda x: preprocess(x, best_params["max_target_len"]),
        batched=True,
        remove_columns=raw_ds.column_names,
    )
    final_split = full_tokenized.train_test_split(test_size=0.05, seed=CFG["seed"])
    os.makedirs(CFG["final_model_dir"], exist_ok=True)

    final_args = Seq2SeqTrainingArguments(
        output_dir=CFG["final_model_dir"],

        evaluation_strategy="epoch",
        save_strategy="epoch",
        logging_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="eval_avg_rouge",
        greater_is_better=True,
        save_total_limit=2,

        learning_rate=best_params["learning_rate"],
        per_device_train_batch_size=best_params["batch_size"],
        per_device_eval_batch_size=8,
        gradient_accumulation_steps=best_params["grad_acc"],
        num_train_epochs=best_params["num_train_epochs"] + 2,
        weight_decay=best_params["weight_decay"],
        warmup_ratio=best_params["warmup_ratio"],
        lr_scheduler_type="cosine",

        label_smoothing_factor=best_params["label_smoothing"],
        max_grad_norm=1.0,

        fp16=True,
        gradient_checkpointing=True,
        optim="adafactor",

        predict_with_generate=True,
        generation_max_length=best_params["max_target_len"],
        generation_num_beams=4,

        dataloader_num_workers=4,
        dataloader_pin_memory=True,
        resume_from_checkpoint=True,

        report_to="none",
        seed=CFG["seed"],
    )

    final_model = AutoModelForSeq2SeqLM.from_pretrained(CFG["model_name"])
    final_model.config.use_cache = False

    final_model.generation_config = GenerationConfig(
        max_new_tokens=best_params["max_target_len"],
        num_beams=4,
        no_repeat_ngram_size=3,
        repetition_penalty=1.3,
        length_penalty=1.0,
        early_stopping=True,
        decoder_start_token_id=tokenizer.pad_token_id,
        bos_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
        forced_eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
    )

    final_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer, model=final_model,
        padding=True, pad_to_multiple_of=8,
    )

    final_trainer = Seq2SeqTrainer(
        model=final_model,
        args=final_args,
        train_dataset=final_split["train"],
        eval_dataset=final_split["test"],
        tokenizer=tokenizer,
        data_collator=final_collator,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)],
    )

    final_trainer.train()
    final_trainer.save_model(CFG["final_model_dir"])
    tokenizer.save_pretrained(CFG["final_model_dir"])
    log.info(f"Final model saved -> {CFG['final_model_dir']}")

# ────────────────────────────────────────────────────────────────
# 10. INFERENCE SANITY CHECK
# ────────────────────────────────────────────────────────────────
log.info("Running inference sanity check...")

test_model = AutoModelForSeq2SeqLM.from_pretrained(CFG["final_model_dir"])
test_tok   = AutoTokenizer.from_pretrained(CFG["final_model_dir"], use_fast=False)
test_model = test_model.eval().cuda()

sample_df = df.sample(min(5, len(df)), random_state=99)

for _, row in sample_df.iterrows():
    prompt = make_prompt(row["content"], row["grade"])
    inputs = test_tok(
        prompt, return_tensors="pt",
        truncation=True, max_length=CFG["max_input_len"]
    ).to("cuda")

    with torch.no_grad():
        out = test_model.generate(
            **inputs,
            max_new_tokens=best_params["max_target_len"],
            num_beams=4,
            no_repeat_ngram_size=3,
            repetition_penalty=1.3,
            length_penalty=1.0,
            early_stopping=True,
        )

    pred = test_tok.decode(out[0], skip_special_tokens=True).strip()
    log.info(
        f"\n[Lop {row['grade']}]\n"
        f"  Input (80c): {row['content'][:80]}...\n"
        f"  Reference  : {row['summary'][:120]}\n"
        f"  Predicted  : {pred[:120]}\n"
    )

log.info("All done!")
