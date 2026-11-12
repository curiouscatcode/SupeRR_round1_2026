"""
Part D — Phase Specialist Analysis Visualizations
=================================================
Generates:
1. outputs/visualizations/16_phase_specialists_grid.png
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

OUT_DIR = Path("outputs/visualizations")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Load data
ph_df = pd.read_csv("data/processed/phase_specialist_rankings.csv")
print(f"Loaded {len(ph_df)} phase entries.")


def plot_phase_specialists_grid():
    fig, axes = plt.subplots(2, 3, figsize=(16, 10), dpi=300)
    
    categories = [
        # Batters (Row 0)
        ('Batter_Powerplay', axes[0, 0], '#3caea3', 'Batting: Powerplay (Overs 1-6)', 'Bayesian Strike Rate', True),
        ('Batter_MiddleOvers', axes[0, 1], '#f6d55c', 'Batting: Middle Overs (Overs 7-15)', 'Bayesian Strike Rate', True),
        ('Batter_DeathOvers', axes[0, 2], '#ed553b', 'Batting: Death Overs (Overs 16-20)', 'Bayesian Strike Rate', True),
        # Bowlers (Row 1)
        ('Bowler_Powerplay', axes[1, 0], '#2e86c1', 'Bowling: Powerplay (Overs 1-6)', 'Bayesian Economy Rate', False),
        ('Bowler_MiddleOvers', axes[1, 1], '#8e44ad', 'Bowling: Middle Overs (Overs 7-15)', 'Bayesian Economy Rate', False),
        ('Bowler_DeathOvers', axes[1, 2], '#d35400', 'Bowling: Death Overs (Overs 16-20)', 'Bayesian Economy Rate', False)
    ]
    
    for cat_name, ax, color, title, metric_label, higher_is_better in categories:
        cat_data = ph_df[ph_df['category'] == cat_name].head(5).iloc[::-1].copy() # Reverse so #1 is on top
        y_pos = np.arange(len(cat_data))
        
        bars = ax.barh(y_pos, cat_data['bayesian_metric'], color=color, edgecolor='black', height=0.6, alpha=0.85, zorder=3)
        prior_val = cat_data['phase_prior'].iloc[0]
        
        # Add reference prior line
        ax.axvline(prior_val, color='#7f8c8d', linestyle='--', linewidth=1.5, zorder=2,
                   label=f"Phase Prior: {prior_val:.1f}")
                   
        # Labels on bars
        for bar, (_, r) in zip(bars, cat_data.iterrows()):
            width = bar.get_width()
            val_text = f" {width:.2f} ({int(r['sample_deliveries'])}b)"
            ax.text(width + (0.5 if higher_is_better else 0.1), bar.get_y() + bar.get_height()/2, 
                    val_text, va='center', ha='left', fontsize=8.5, fontweight='bold', color='#1b2631')
                    
        ax.set_yticks(y_pos)
        ax.set_yticklabels([f"#{int(r['rank'])} {r['player_name']}" for _, r in cat_data.iterrows()],
                           fontsize=9.5, fontweight='bold')
        ax.set_title(title, fontsize=11, fontweight='bold', pad=10)
        ax.set_xlabel(f"{metric_label} ({'Higher' if higher_is_better else 'Lower'} is Better)", 
                      fontsize=9.5, fontweight='bold', labelpad=6)
        
        if higher_is_better:
            ax.set_xlim(0, max(cat_data['bayesian_metric'].max() * 1.25, 200))
        else:
            ax.set_xlim(0, max(cat_data['bayesian_metric'].max() * 1.35, 12))
            
        ax.legend(loc='lower right', fontsize=8)
        ax.grid(True, linestyle='--', alpha=0.5, zorder=0)
        
    fig.suptitle("Phase Specialists Grid: Top 5 Qualified Players Across Match Phases (2022–2026)\n"
                 "Evaluated on Phase-Specific Bayesian Metrics with Empirically Grounded Sample Thresholds", 
                 fontsize=13, fontweight='bold', y=0.99)
                 
    out_path = OUT_DIR / "16_phase_specialists_grid.png"
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Generated: {out_path}")


if __name__ == '__main__':
    plot_phase_specialists_grid()
