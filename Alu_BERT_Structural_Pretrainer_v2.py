import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm
import os
import math
import random

# =========================================================
# 1. Configuration: Duplex-BERT v2
# =========================================================
CONFIG = {
    'vocab': {'A': 0, 'C': 1, 'G': 2, 'U': 3, 'T': 3, '-': 4, 'N': 5, '*': 5, '[MASK]': 6, '[SEP]': 7, '[PAD]': 8},
    'vocab_size': 9,
    'seq_len': 301, 
    'd_model': 128,
    'nhead': 8,
    'num_layers': 6,
    'batch_size': 32,
    'lr': 0.0005,
    'epochs': 150,
    'mask_prob': 0.15
}

# =========================================================
# 2. Alignment-Aware Parsing (Gap-Preserving)
# =========================================================
def parse_aligned_seq_v2(row, type_col):
    try:
        p = str(row[f'{type_col}_pair'])
        u = str(row[f'{type_col}_unpair'])
        length = max(len(p), len(u))
        p = p.ljust(length)
        u = u.ljust(length)
        s = ""
        for i in range(length):
            if p[i] != ' ': s += p[i]
            elif u[i] != ' ': s += u[i]
            else: s += '-' 
        return s
    except: return ""

def encode_duplex_v2(ecs_seq, es_seq, max_len=301):
    def seq_to_idx(seq):
        idx = [CONFIG['vocab'].get(c, 5) for c in seq]
        if len(idx) < max_len: idx += [8] * (max_len - len(idx))
        return torch.tensor(idx[:max_len], dtype=torch.long)
    return seq_to_idx(ecs_seq), seq_to_idx(es_seq)

# =========================================================
# 3. Structural Alu Dataset (Elite 20%)
# =========================================================
class StructuralAluDataset(Dataset):
    def __init__(self, csv_file):
        print(f"🧬 Loading Elite Structural Alu Corpus: {csv_file}")
        df = pd.read_csv(csv_file)
        self.pairs = []
        for _, row in tqdm(df.iterrows(), total=df.shape[0], desc="Parsing Duplexes"):
            es = parse_aligned_seq_v2(row, 'es')
            ecs = parse_aligned_seq_v2(row, 'ecs')
            if '*' in es and len(es) >= 301 and len(ecs) >= 301:
                c = es.find('*')
                s, e = c - 150, c + 151
                if e <= len(es) and e <= len(ecs):
                    self.pairs.append((ecs[s:e], es[s:e]))
        print(f"✅ Loaded {len(self.pairs)} Elite Duplexes.")

    def __len__(self): return len(self.pairs)
    def __getitem__(self, idx):
        ecs_seq, es_seq = self.pairs[idx]
        ecs_idx, es_idx = encode_duplex_v2(ecs_seq, es_seq)
        input_ecs = ecs_idx.clone()
        label_ecs = ecs_idx.clone()
        mask_mask = (torch.rand(input_ecs.shape) < CONFIG['mask_prob']) & (input_ecs != 8)
        input_ecs[mask_mask] = CONFIG['vocab']['[MASK]']
        label_ecs[~mask_mask] = -100 
        return input_ecs, es_idx, label_ecs

# =========================================================
# 4. Duplex-BERT Architecture
# =========================================================
class DuplexBERT(nn.Module):
    def __init__(self):
        super().__init__()
        self.embedding = nn.Embedding(CONFIG['vocab_size'], CONFIG['d_model'])
        self.seg_embedding = nn.Embedding(2, CONFIG['d_model']) 
        self.pos_enc = nn.Parameter(torch.randn(1, CONFIG['seq_len'], CONFIG['d_model']))
        layer = nn.TransformerEncoderLayer(d_model=CONFIG['d_model'], nhead=CONFIG['nhead'], batch_first=True)
        self.transformer = nn.TransformerEncoder(layer, num_layers=CONFIG['num_layers'])
        self.fc_out = nn.Linear(CONFIG['d_model'], CONFIG['vocab_size'])

    def forward(self, ecs_idx, es_idx):
        ecs_emb = self.embedding(ecs_idx) + self.seg_embedding(torch.zeros_like(ecs_idx))
        es_emb = self.embedding(es_idx) + self.seg_embedding(torch.ones_like(es_idx))
        x = (ecs_emb + es_emb) + self.pos_enc
        out = self.transformer(x)
        return self.fc_out(out)

# =========================================================
# 5. Training Main Loop
# =========================================================
if __name__ == "__main__":
    base = r"C:\Users\hskim\OneDrive\Desktop\GeminiCLI files\4_Data_Analysis\Deep_Learning_Models"
    elite_file = os.path.join(base, "UAG_Elite_Top20.csv")
    save_path = os.path.join(base, "Alu_BERT_Structural_v2.pth")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    print(f"🚀 Initializing Structural Alu-BERT v2 Training on {device}...")
    ds = StructuralAluDataset(elite_file)
    ldr = DataLoader(ds, batch_size=CONFIG['batch_size'], shuffle=True)
    
    model = DuplexBERT().to(device)
    opt = optim.Adam(model.parameters(), lr=CONFIG['lr'])
    crit = nn.CrossEntropyLoss(ignore_index=-100)
    
    best_loss = float('inf')
    
    print("\n🧠 Learning the 'Duplex Grammar' (Structural MLM)...")
    for e in range(CONFIG['epochs']):
        ls = 0
        pbar = tqdm(ldr, desc=f"Epoch {e+1}/{CONFIG['epochs']}", leave=False)
        for x_ecs, x_es, y in pbar:
            x_ecs, x_es, y = x_ecs.to(device), x_es.to(device), y.to(device)
            opt.zero_grad()
            pred = model(x_ecs, x_es)
            loss = crit(pred.view(-1, CONFIG['vocab_size']), y.view(-1))
            loss.backward()
            opt.step()
            ls += loss.item()
            pbar.set_postfix({'Loss': f"{loss.item():.4f}"})
        
        avg_loss = ls/len(ldr)
        print(f"   Epoch {e+1}: Avg Loss = {avg_loss:.6f}")
        
        # Save best model
        if avg_loss < best_loss:
            best_loss = avg_loss
            torch.save(model.state_dict(), save_path)
            # print(f"      [SAVED] New Best Loss: {best_loss:.6f}")

    print(f"\n✅ Training Complete. Best Model saved to: {save_path}")
