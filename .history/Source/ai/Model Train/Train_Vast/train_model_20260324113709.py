"""
train_model.py — PhoBERTSUM với Optuna HPO
Tối ưu cho Vast.ai (RTX 3090/4090)
Tích hợp: FP16 mixed precision, gradient accumulation, data leakage fix,
           pos_weight, macro F1, gradient clipping, early stopping
"""

import os
import gc
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.cuda.amp import autocast, GradScaler
from transformers import AutoTokenizer, AutoModel, get_linear_schedule_with_warmup
import optuna
from sklearn.model_selection import GroupShuffleSplit
import pandas as pd
import numpy as np
from tqdm import tqdm
from torch.optim import AdamW
from sklearn.metrics import f1_score
import warnings
warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────
# CONFIG — chỉnh ở đây trước khi chạy
# ──────────────────────────────────────────────
DATA_PATH    = "./Data_TX_train.xlsx"   # đường dẫn file data
MODEL_NAME   = "vinai/phobert-base"
SAVE_DIR     = "./checkpoints"          # thư mục lưu best model
N_TRIALS     = 20                       # số trial Optuna
TEST_SIZE    = 0.2
RANDOM_STATE = 42
DEVICE       = "cuda" if torch.cuda.is_available() else "cpu"

os.makedirs(SAVE_DIR, exist_ok=True)

# ──────────────────────────────────────────────
# TOKENIZER — load 1 lần duy nhất
# ──────────────────────────────────────────────
print(f"[INFO] Loading tokenizer from {MODEL_NAME} ...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=False)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
print(f"[INFO] Device: {DEVICE}")
if DEVICE == "cuda":
    print(f"[INFO] GPU: {torch.cuda.get_device_name(0)}")
    print(f"[INFO] VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")


# ──────────────────────────────────────────────
# MODEL
# ──────────────────────────────────────────────
class PhoBERTSUM(nn.Module):
    def __init__(self, encoder):
        super().__init__()
        self.encoder = encoder
        hidden = encoder.config.hidden_size
        self.classifier = nn.Sequential(
            nn.Dropout(0.1),
            nn.Linear(hidden, 1)
        )

    def forward(self, input_ids, attention_mask):
        outputs = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        # Mean pooling — ổn định hơn chỉ lấy [CLS]
        sent_emb = outputs.last_hidden_state.mean(dim=1)
        return self.classifier(sent_emb)


# ──────────────────────────────────────────────
# DATASET
# ──────────────────────────────────────────────
class SentenceDataset(Dataset):
    def __init__(self, data, tokenizer, max_len=256):
        self.data      = data.reset_index(drop=True)
        self.tokenizer = tokenizer
        self.max_len   = max_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row      = self.data.iloc[idx]
        sentence = str(row['sentence'])
        label    = float(row['label'])

        encoding = self.tokenizer(
            sentence,
            truncation=True,
            padding='max_length',
            max_length=self.max_len,
            return_tensors='pt'
        )
        return {
            'input_ids'     : encoding['input_ids'].squeeze(0),
            'attention_mask': encoding['attention_mask'].squeeze(0),
            'label'         : torch.tensor(label, dtype=torch.float)
        }


# ──────────────────────────────────────────────
# TRAIN ONE EPOCH
# ──────────────────────────────────────────────
def train_epoch(model, dataloader, optimizer, scheduler,
                device, pos_weight, scaler, accum_steps):
    model.train()
    total_loss = 0
    criterion  = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer.zero_grad()

    for step, batch in enumerate(tqdm(dataloader, desc="  Training", leave=False)):
        input_ids      = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels         = batch['label'].to(device)

        with autocast():                                    # FP16
            outputs = model(input_ids, attention_mask)
            loss    = criterion(outputs.squeeze(), labels)
            loss    = loss / accum_steps                   # scale loss

        scaler.scale(loss).backward()

        if (step + 1) % accum_steps == 0:
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(optimizer)
            scaler.update()
            optimizer.zero_grad()
            scheduler.step()

        total_loss += loss.item() * accum_steps            # unscale cho log

    # xử lý batch dư (không chia hết accum_steps)
    if (step + 1) % accum_steps != 0:
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scaler.step(optimizer)
        scaler.update()
        optimizer.zero_grad()
        scheduler.step()

    return total_loss / len(dataloader)


# ──────────────────────────────────────────────
# VALIDATE
# ──────────────────────────────────────────────
def validate(model, dataloader, device, pos_weight):
    model.eval()
    total_loss = 0
    all_preds, all_labels = [], []
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)

    with torch.no_grad():
        for batch in tqdm(dataloader, desc="  Validating", leave=False):
            input_ids      = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels         = batch['label'].to(device)

            with autocast():
                outputs = model(input_ids, attention_mask)
                loss    = criterion(outputs.squeeze(), labels)

            total_loss += loss.item()

            probs = torch.sigmoid(outputs.squeeze())
            preds = (probs > 0.5).float()
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    avg_loss = total_loss / len(dataloader)
    f1_macro = f1_score(all_labels, all_preds, average='macro')   # cân bằng 2 class
    f1_bin   = f1_score(all_labels, all_preds, average='binary')  # theo dõi thêm
    return avg_loss, f1_macro, f1_bin


# ──────────────────────────────────────────────
# OPTUNA OBJECTIVE
# ──────────────────────────────────────────────
def objective(trial):
    # Load data
    data = pd.read_excel(DATA_PATH)

    # ── Fix data leakage: split theo doc_id ──
    gss = GroupShuffleSplit(n_splits=1, test_size=TEST_SIZE, random_state=RANDOM_STATE)
    train_idx, val_idx = next(gss.split(data, groups=data['doc_id']))
    train_data = data.iloc[train_idx].reset_index(drop=True)
    val_data   = data.iloc[val_idx].reset_index(drop=True)

    # ── pos_weight tính từ train_data ──
    n_neg      = (train_data['label'] == 0).sum()
    n_pos      = (train_data['label'] == 1).sum()
    pos_weight = torch.tensor([n_neg / n_pos], dtype=torch.float).to(DEVICE)

    # ── Hyperparameters ──
    learning_rate = trial.suggest_float("learning_rate", 1e-5, 5e-5, log=True)
    batch_size    = trial.suggest_categorical("batch_size", [8, 16, 32])
    max_len       = trial.suggest_categorical("max_len", [128, 256])
    num_epochs    = trial.suggest_int("num_epochs", 3, 6)
    warmup_ratio  = trial.suggest_float("warmup_ratio", 0.03, 0.15)
    weight_decay  = trial.suggest_float("weight_decay", 0.0, 0.1)
    accum_steps   = trial.suggest_categorical("accum_steps", [1, 2, 4])

    # Effective batch = batch_size * accum_steps
    print(f"\n[Trial {trial.number}] lr={learning_rate:.2e} | batch={batch_size} "
          f"| accum={accum_steps} (eff={batch_size*accum_steps}) "
          f"| max_len={max_len} | epochs={num_epochs}")

    # ── Datasets & Dataloaders ──
    train_dataset = SentenceDataset(train_data, tokenizer, max_len=max_len)
    val_dataset   = SentenceDataset(val_data,   tokenizer, max_len=max_len)

    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True,
        num_workers=4, pin_memory=True
    )
    val_loader = DataLoader(
        val_dataset, batch_size=batch_size, shuffle=False,
        num_workers=4, pin_memory=True
    )

    # ── Model ──
    encoder = AutoModel.from_pretrained(MODEL_NAME).to(DEVICE)
    model   = PhoBERTSUM(encoder).to(DEVICE)

    # ── Optimizer & Scheduler ──
    optimizer    = AdamW(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
    total_steps  = (len(train_loader) // accum_steps) * num_epochs
    warmup_steps = int(total_steps * warmup_ratio)
    scheduler    = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=warmup_steps,
        num_training_steps=total_steps
    )

    # ── FP16 scaler ──
    scaler = GradScaler()

    best_f1          = 0.0
    patience         = 3
    patience_counter = 0
    best_model_path  = os.path.join(SAVE_DIR, f"trial_{trial.number}_best.pt")

    for epoch in range(num_epochs):
        print(f"  Epoch {epoch+1}/{num_epochs}")

        train_loss = train_epoch(
            model, train_loader, optimizer, scheduler,
            DEVICE, pos_weight, scaler, accum_steps
        )
        val_loss, val_f1_macro, val_f1_bin = validate(
            model, val_loader, DEVICE, pos_weight
        )

        print(f"  → Train Loss: {train_loss:.4f} | "
              f"Val Loss: {val_loss:.4f} | "
              f"F1 Macro: {val_f1_macro:.4f} | "
              f"F1 Binary: {val_f1_bin:.4f}")

        # ── Save best ──
        if val_f1_macro > best_f1:
            best_f1 = val_f1_macro
            patience_counter = 0
            torch.save(model.state_dict(), best_model_path)
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"  Early stopping tại epoch {epoch+1}")
                break

        # ── Optuna pruning ──
        trial.report(val_f1_macro, epoch)
        if trial.should_prune():
            print("  Pruned by Optuna.")
            # dọn bộ nhớ trước khi prune
            del model, encoder, optimizer, scaler
            torch.cuda.empty_cache()
            gc.collect()
            raise optuna.exceptions.TrialPruned()

    # ── Dọn VRAM sau mỗi trial ──
    del model, encoder, optimizer, scaler
    torch.cuda.empty_cache()
    gc.collect()

    return best_f1


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  PhoBERTSUM — Optuna Hyperparameter Search")
    print("="*60)

    study = optuna.create_study(
        direction='maximize',
        pruner=optuna.pruners.MedianPruner(
            n_startup_trials=5,     # không prune 5 trial đầu
            n_warmup_steps=2        # không prune 2 epoch đầu mỗi trial
        ),
        study_name="phobert_summarization"
    )

    study.optimize(objective, n_trials=N_TRIALS, show_progress_bar=False)

    # ── Kết quả ──
    print("\n" + "="*60)
    print("  OPTUNA COMPLETED")
    print("="*60)
    print(f"Best F1 Macro : {study.best_value:.4f}")
    print(f"Best Params   :")
    for k, v in study.best_params.items():
        print(f"  {k:20s}: {v}")

    # ── Train lại với best params trên toàn bộ data ──
    print("\n[INFO] Training final model với best params ...")

    data = pd.read_excel(DATA_PATH)
    gss  = GroupShuffleSplit(n_splits=1, test_size=TEST_SIZE, random_state=RANDOM_STATE)
    train_idx, val_idx = next(gss.split(data, groups=data['doc_id']))
    train_data = data.iloc[train_idx].reset_index(drop=True)
    val_data   = data.iloc[val_idx].reset_index(drop=True)

    bp         = study.best_params
    n_neg      = (train_data['label'] == 0).sum()
    n_pos      = (train_data['label'] == 1).sum()
    pos_weight = torch.tensor([n_neg / n_pos], dtype=torch.float).to(DEVICE)

    train_dataset = SentenceDataset(train_data, tokenizer, max_len=bp['max_len'])
    val_dataset   = SentenceDataset(val_data,   tokenizer, max_len=bp['max_len'])
    train_loader  = DataLoader(train_dataset, batch_size=bp['batch_size'],
                               shuffle=True,  num_workers=4, pin_memory=True)
    val_loader    = DataLoader(val_dataset,   batch_size=bp['batch_size'],
                               shuffle=False, num_workers=4, pin_memory=True)

    encoder   = AutoModel.from_pretrained(MODEL_NAME).to(DEVICE)
    model     = PhoBERTSUM(encoder).to(DEVICE)
    optimizer = AdamW(model.parameters(),
                      lr=bp['learning_rate'], weight_decay=bp['weight_decay'])

    num_epochs   = bp['num_epochs']
    accum_steps  = bp['accum_steps']
    total_steps  = (len(train_loader) // accum_steps) * num_epochs
    warmup_steps = int(total_steps * bp['warmup_ratio'])
    scheduler    = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_steps
    )
    scaler = GradScaler()

    best_f1         = 0.0
    best_final_path = os.path.join(SAVE_DIR, "final_best_model.pt")
    patience        = 3
    patience_counter= 0

    for epoch in range(num_epochs):
        print(f"\nFinal Epoch {epoch+1}/{num_epochs}")
        train_loss = train_epoch(
            model, train_loader, optimizer, scheduler,
            DEVICE, pos_weight, scaler, accum_steps
        )
        val_loss, val_f1_macro, val_f1_bin = validate(
            model, val_loader, DEVICE, pos_weight
        )
        print(f"  Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | "
              f"F1 Macro: {val_f1_macro:.4f} | F1 Binary: {val_f1_bin:.4f}")

        if val_f1_macro > best_f1:
            best_f1 = val_f1_macro
            patience_counter = 0
            torch.save({
                'epoch'      : epoch + 1,
                'model_state': model.state_dict(),
                'optimizer'  : optimizer.state_dict(),
                'best_f1'    : best_f1,
                'params'     : bp
            }, best_final_path)
            print(f"  ✓ Saved best model → {best_final_path}")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"  Early stopping tại epoch {epoch+1}")
                break

    print(f"\n[DONE] Final model F1 Macro: {best_f1:.4f}")
    print(f"[DONE] Model saved tại: {best_final_path}")
