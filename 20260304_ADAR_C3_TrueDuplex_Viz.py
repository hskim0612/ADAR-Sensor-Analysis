import RNA
import matplotlib.pyplot as plt
import os
import json
import pandas as pd

def get_300bp_target(fasta_path, site):
    with open(fasta_path, 'r') as f:
        seq = "".join([line.strip() for line in f if not line.startswith(">")]).upper().replace('T', 'U')
    start = max(0, site - 150)
    end = min(len(seq), site + 150)
    return seq[start:end]

def plot_true_duplex(sensor_seq, target_seq, site_id, candidate_idx, output_dir):
    complex_seq = f"{sensor_seq}&{target_seq}"
    struct, mfe = RNA.cofold(complex_seq)
    
    # Get physical coordinates for the duplex (No linker hack)
    coords = RNA.get_xy_coordinates(struct)
    
    # Process coordinates
    xs, ys = [], []
    for i in range(len(sensor_seq) + len(target_seq)):
        pt = coords.get(i)
        xs.append(pt.X)
        ys.append(pt.Y)
    
    # Parse pairs
    pairs = []
    stack = []
    # ViennaRNA's struct for duplex uses '&' but the coordinate engine 
    # treats them as a continuous sequence of indices (0 to N+M-1)
    struct_no_amp = struct.replace('&', '.')
    for i, char in enumerate(struct):
        if char == '(': stack.append(i)
        elif char == ')':
            if stack:
                j = stack.pop()
                pairs.append((j, i))
                
    paired_indices = set()
    for p in pairs:
        paired_indices.add(p[0]); paired_indices.add(p[1])

    plt.figure(figsize=(16, 12))
    plt.title(f"True Duplex: C3 Site {site_id} (300bp Target vs 300bp Sensor)\nMFE: {mfe:.2f} kcal/mol", fontsize=16)

    # Draw base pairs (Hydrogen bonds)
    for (i, j) in pairs:
        plt.plot([xs[i], xs[j]], [ys[i], ys[j]], color='#BBBBBB', linestyle='-', linewidth=0.8, zorder=1)

    # Draw Backbones
    sensor_len = len(sensor_seq)
    plt.plot(xs[:sensor_len], ys[:sensor_len], color='#ff7f0e', label='Sensor (300bp)', linewidth=2, alpha=0.6, zorder=2)
    plt.plot(xs[sensor_len:], ys[sensor_len:], color='#1f77b4', label='Target C3 mRNA (300bp)', linewidth=2, alpha=0.6, zorder=2)

    # Highlight Bulges/Mismatches in RED
    unpaired_x = [xs[i] for i in range(len(xs)) if i not in paired_indices]
    unpaired_y = [ys[i] for i in range(len(ys)) if i not in paired_indices]
    plt.scatter(unpaired_x, unpaired_y, s=15, color='#FF1744', edgecolors='none', label='Bulge/Mismatch', zorder=3)

    # 50th Codon Highlight (Index 148 in Sensor - Middle of the Codon)
    c_idx = 148
    if c_idx < sensor_len:
        base = sensor_seq[c_idx]
        plt.scatter(xs[c_idx], ys[c_idx], s=40, facecolors='yellow', edgecolors='black', linewidth=0.5, zorder=4)
        plt.text(xs[c_idx], ys[c_idx], base, fontsize=4, ha='center', va='center', color='black', fontweight='bold', zorder=5)

    plt.legend(loc='upper right', fontsize=12)
    plt.axis('equal'); plt.axis('off')
    
    filename = f"C3_Site_{site_id}_Cand_{candidate_idx}_Duplex.png"
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    return filepath

if __name__ == "__main__":
    out_dir = "ADAR_C3_Visualizations"
    if not os.path.exists(out_dir): os.makedirs(out_dir)
    
    # Load 18 candidates from the consensus file
    # (Extracting first candidate for Site 1131 as a pilot)
    lead_sensor = "AUCGGCCCCCCAUUUCCCUGGCUCGUAGACUGGACGGUGUCCUCACCAGAGAGUGCAGAUGGGACUCGGUGGGGGGGAGCCUCAUCAGGGUUCGACAGGAACACGGUGAGGUCUAAGGGCAUUCCGGGAGAGAAUUGGUUGGGUUUCUAGGUGAAGUUGAUCUGGGAGCGAGAGGUAAUUGUGGGGAUCCCGCUGCGUUCUGCCUGCGCCGUGUCAGUGCGUAAGUGCGGGAGGACGGUGGCAGACACAUACGAAUGCUCCUCAAACAGGUACUUUGCUGGGCGGUUCGGCUCCCCGUCC"
    lead_site = 1131
    
    target_300 = get_300bp_target("human_C3_mRNA.fasta", lead_site)
    
    print(f"🧬 Generating True Duplex Visualization for Site {lead_site}...")
    img_path = plot_true_duplex(lead_sensor, target_300, lead_site, 1, out_dir)
    print(f"✅ Success! Visualization saved to: {img_path}")
