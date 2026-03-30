"""
train_model_v2.py — PhoBERTSUM cải tiến
Thay đổi so với v1:
  1. Learning rate thấp hơn: 1e-5 → 3e-5
  2. Batch size phù hợp hơn: [8, 16] + accum để eff batch lớn hơn
  3. Thêm context câu xung quanh (prev + current + next)
  4. CLS token thay mean pooling
  5. Label smoothing
  6. Differential LR chi tiết theo layer
  7. 15 trials
  8. Early stopping patience=1
  9. PhoBERT-large
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
# CONFIG
# ──────────────────────────────────────────────
DATA_PATH    = "/workspace/Data_TX_train.xlsx"
MODEL_NAME   = "vinai/phobert-large"          # đổi sang large
SAVE_DIR     = "/workspace/checkpoints_v2"
N_TRIALS     = 15
TEST_SIZE    = 0.2
RANDOM_STATE = 42
DEVICE       = "cuda" if torch.cuda.is_available() else "cpu"

os.makedirs(SAVE_DIR, exist_ok=True)

# ──────────────────────────────────────────────
# TOKENIZER
# ──────────────────────────────────────────────
print(f"[INFO] Loading tokenizer từ {MODEL_NAME} ...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=False)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
print(f"[INFO] Device : {DEVICE}")
if DEVICE == "cuda":
    print(f"[INFO] GPU    : {torch.cuda.get_device_name(0)}")
    print(f"[INFO] VRAM   : {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")


# ──────────────────────────────────────────────
# MODEL — CLS pooling + deeper classifier
# ──────────────────────────────────────────────
class PhoBERTSUM(nn.Module):
    def __init__(self, encoder):
        super().__init__()
        self.encoder = encoder
        hidden = encoder.config.hidden_size  # 768 (base) hoặc 1024 (large)
        self.classifier = nn.Sequential(
            nn.Linear(hidden, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 1)
        )

    def forward(self, input_ids, attention_mask):
        outputs = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        # CLS token — đại diện toàn bộ sequence
        cls_emb = outputs.last_hidden_state[:, 0, :]
        return self.classifier(cls_emb)


# ──────────────────────────────────────────────
# DATASET — có context câu xung quanh
# ──────────────────────────────────────────────
class SentenceDataset(Dataset):
    def __init__(self, data, tokenizer, max_len=256):
        self.data      = data.reset_index(drop=True)
        self.tokenizer = tokenizer
        self.max_len   = max_len

        # Group các câu theo doc_id để lấy context
        self.doc_groups = self.data.groupby('doc_id').apply(
            lambda x: x.index.tolist()
        ).to_dict()

        # Map index → vị trí trong doc
        self.idx_to_pos = {}
        for doc_id, indices in self.doc_groups.items():
            for pos, idx in enumerate(indices):
                self.idx_to_pos[idx] = (doc_id, pos, indices)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row   = self.data.iloc[idx]
        label = float(row['label'])

        doc_id, pos, indices = self.idx_to_pos[idx]

        # Lấy câu hiện tại
        current = str(self.data.iloc[idx]['sentence'])

        # Lấy câu trước (nếu có)
        prev = str(self.data.iloc[indices[pos - 1]]['sentence']) \
               if pos > 0 else ""

        # Lấy câu sau (nếu có)
        nxt  = str(self.data.iloc[indices[pos + 1]]['sentence']) \
               if pos < len(indices) - 1 else ""

        # Ghép context: [prev] SEP [current] SEP [next]
        # Tokenizer tự thêm CLS và SEP
        if prev and nxt:
            text_a = prev
            text_b = current + " " + tokenizer.sep_token + " " + nxt
        elif prev:
            text_a = prev
            text_b = current
        elif nxt:
            text_a = current
            text_b = nxt
        else:
            text_a = current
            text_b = None

        encoding = self.tokenizer(
            text_a,
            text_b,
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
# LABEL SMOOTHING
# ──────────────────────────────────────────────
def smooth_labels(labels, smoothing=0.1):
    """1 → 0.9, 0 → 0.1 — giảm overconfidence"""
    return labels * (1 - smoothing) + 0.5 * smoothing


# ──────────────────────────────────────────────
# DIFFERENTIAL LR OPTIMIZER
# ──────────────────────────────────────────────
def build_optimizer(model, lr, weight_decay):
    """
    Chia encoder thành 4 group với lr tăng dần từ dưới lên trên.
    Classifier dùng lr đầy đủ.
    """
    encoder = model.encoder

    # Embeddings — layer thấp nhất, thay đổi ít nhất
    embeddings_params = list(encoder.embeddings.parameters())

    # 12 transformer layers (base) hoặc 24 layers (large)
    all_layers = list(encoder.encoder.layer)
    n          = len(all_layers)
    third      = n // 3

    lower_params  = []
    middle_params = []
    upper_params  = []
    for i, layer in enumerate(all_layers):
        if i < third:
            lower_params  += list(layer.parameters())
        elif i < 2 * third:
            middle_params += list(layer.parameters())
        else:
            upper_params  += list(layer.parameters())

    classifier_params = list(model.classifier.parameters())

    param_groups = [
        {"params": embeddings_params, "lr": lr * 0.01},   # rất nhỏ
        {"params": lower_params,      "lr": lr * 0.1},    # nhỏ
        {"params": middle_params,     "lr": lr * 0.3},    # vừa
        {"params": upper_params,      "lr": lr * 0.6},    # gần full
        {"params": classifier_params, "lr": lr},           # full lr
    ]

    return AdamW(param_groups, weight_decay=weight_decay)


# ──────────────────────────────────────────────
# TRAIN ONE EPOCH
# ──────────────────────────────────────────────
def train_epoch(model, dataloader, optimizer, scheduler,
                device, pos_weight, scaler, accum_steps, smoothing=0.1):
    model.train()
    total_loss = 0
    criterion  = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer.zero_grad()

    for step, batch in enumerate(tqdm(dataloader, desc="  Training", leave=False)):
        input_ids      = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels         = batch['label'].to(device)
        labels_smooth  = smooth_labels(labels, smoothing)   # label smoothing

        with autocast():
            outputs = model(input_ids, attention_mask)
            loss    = criterion(outputs.squeeze(), labels_smooth)
            loss    = loss / accum_steps

        scaler.scale(loss).backward()

        if (step + 1) % accum_steps == 0:
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(optimizer)
            scaler.update()
            optimizer.zero_grad()
            scheduler.step()

        total_loss += loss.item() * accum_steps

    # batch dư
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
    f1_macro = f1_score(all_labels, all_preds, average='macro')
    f1_bin   = f1_score(all_labels, all_preds, average='binary')
    return avg_loss, f1_macro, f1_bin


# ──────────────────────────────────────────────
# OPTUNA OBJECTIVE
# ──────────────────────────────────────────────
def objective(trial):
    data = pd.read_excel(DATA_PATH)

    # Split theo doc_id
    gss = GroupShuffleSplit(n_splits=1, test_size=TEST_SIZE, random_state=RANDOM_STATE)
    train_idx, val_idx = next(gss.split(data, groups=data['doc_id']))
    train_data = data.iloc[train_idx].reset_index(drop=True)
    val_data   = data.iloc[val_idx].reset_index(drop=True)

    # pos_weight
    n_neg      = (train_data['label'] == 0).sum()
    n_pos      = (train_data['label'] == 1).sum()
    pos_weight = torch.tensor([n_neg / n_pos], dtype=torch.float).to(DEVICE)

    # ── Hyperparameters ──
    # LR thấp hơn v1, phù hợp với large model
    learning_rate = trial.suggest_float("learning_rate", 1e-5, 4e-5, log=True)

    # Batch nhỏ nhưng tăng accum để eff batch đủ lớn
    batch_size  = trial.suggest_categorical("batch_size", [8, 16])
    accum_steps = trial.suggest_categorical("accum_steps", [2, 4])

    max_len      = trial.suggest_categorical("max_len", [128, 256])
    num_epochs   = trial.suggest_int("num_epochs", 3, 6)
    warmup_ratio = trial.suggest_float("warmup_ratio", 0.03, 0.15)
    weight_decay = trial.suggest_float("weight_decay", 0.0, 0.1)
    smoothing    = trial.suggest_float("smoothing", 0.05, 0.15)

    eff_batch = batch_size * accum_steps
    print(f"\n[Trial {trial.number}] lr={learning_rate:.2e} | "
          f"batch={batch_size} | accum={accum_steps} (eff={eff_batch}) | "
          f"max_len={max_len} | epochs={num_epochs} | smooth={smoothing:.2f}")

    # ── Datasets ──
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

    # ── Differential LR Optimizer ──
    optimizer   = build_optimizer(model, learning_rate, weight_decay)
    total_steps = (len(train_loader) // accum_steps) * num_epochs
    warmup_steps= int(total_steps * warmup_ratio)
    scheduler   = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=warmup_steps,
        num_training_steps=total_steps
    )
    scaler = GradScaler()

    best_f1          = 0.0
    patience         = 1                   # dừng sớm patience=1
    patience_counter = 0
    best_model_path  = os.path.join(SAVE_DIR, f"trial_{trial.number}_best.pt")

    for epoch in range(num_epochs):
        print(f"  Epoch {epoch+1}/{num_epochs}")

        # Freeze embeddings + lower layers trong 2 epoch đầu
        freeze = epoch < 2
        for param in encoder.embeddings.parameters():
            param.requires_grad = not freeze
        for layer in list(encoder.encoder.layer)[:len(encoder.encoder.layer)//3]:
            for param in layer.parameters():
                param.requires_grad = not freeze

        train_loss = train_epoch(
            model, train_loader, optimizer, scheduler,
            DEVICE, pos_weight, scaler, accum_steps, smoothing
        )
        val_loss, val_f1_macro, val_f1_bin = validate(
            model, val_loader, DEVICE, pos_weight
        )

        print(f"  → Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | "
              f"F1 Macro: {val_f1_macro:.4f} | F1 Binary: {val_f1_bin:.4f}")

        if val_f1_macro > best_f1:
            best_f1 = val_f1_macro
            patience_counter = 0
            torch.save(model.state_dict(), best_model_path)
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"  Early stopping tại epoch {epoch+1}")
                break

        trial.report(val_f1_macro, epoch)
        if trial.should_prune():
            print("  Pruned.")
            del model, encoder, optimizer, scaler
            torch.cuda.empty_cache()
            gc.collect()
            raise optuna.exceptions.TrialPruned()

    del model, encoder, optimizer, scaler
    torch.cuda.empty_cache()
    gc.collect()

    return best_f1


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  PhoBERTSUM v2 — Optuna Hyperparameter Search")
    print(f"  Model : {MODEL_NAME}")
    print(f"  Trials: {N_TRIALS}")
    print("="*60)

    study = optuna.create_study(
        direction='maximize',
        pruner=optuna.pruners.MedianPruner(
            n_startup_trials=4,
            n_warmup_steps=1
        ),
        study_name="phobert_large_summarization"
    )

    study.optimize(objective, n_trials=N_TRIALS, show_progress_bar=False)

    print("\n" + "="*60)
    print("  OPTUNA COMPLETED")
    print("="*60)
    print(f"Best F1 Macro : {study.best_value:.4f}")
    print("Best Params   :")
    for k, v in study.best_params.items():
        print(f"  {k:20s}: {v}")

    # ── Final model với best params ──
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
    optimizer = build_optimizer(model, bp['learning_rate'], bp['weight_decay'])

    accum_steps  = bp['accum_steps']
    num_epochs   = bp['num_epochs']
    total_steps  = (len(train_loader) // accum_steps) * num_epochs
    warmup_steps = int(total_steps * bp['warmup_ratio'])
    scheduler    = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_steps
    )
    scaler = GradScaler()

    best_f1          = 0.0
    best_final_path  = os.path.join(SAVE_DIR, "final_best_model.pt")
    patience         = 1
    patience_counter = 0

    for epoch in range(num_epochs):
        print(f"\nFinal Epoch {epoch+1}/{num_epochs}")

        freeze = epoch < 2
        for param in encoder.embeddings.parameters():
            param.requires_grad = not freeze
        for layer in list(encoder.encoder.layer)[:len(encoder.encoder.layer)//3]:
            for param in layer.parameters():
                param.requires_grad = not freeze

        train_loss = train_epoch(
            model, train_loader, optimizer, scheduler,
            DEVICE, pos_weight, scaler, accum_steps, bp['smoothing']
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
            print(f"  ✓ Saved → {best_final_path}")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"  Early stopping tại epoch {epoch+1}")
                break

    print(f"\n[DONE] Final F1 Macro : {best_f1:.4f}")
    print(f"[DONE] Model saved    : {best_final_path}")