import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ── Load Data ──────────────────────────────────────────────────────────────
df = pd.read_csv("pmkisan_data.csv")

plt.style.use('seaborn-v0_8-whitegrid')
colors = ['#2ecc71','#e74c3c','#3498db','#f39c12','#9b59b6']

# ── 1. Bottom 10 Districts Bar Chart ──────────────────────────────────────
bottom10 = df.nsmallest(10, 'Uptake_Pct').copy()

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(bottom10['District'] + ' (' + bottom10['State'] + ')',
               bottom10['Uptake_Pct'], color='#e74c3c', edgecolor='white')
ax.axvline(df['Uptake_Pct'].mean(), color='#2ecc71', linestyle='--', linewidth=2,
           label=f"National Avg: {df['Uptake_Pct'].mean():.1f}%")
ax.set_xlabel('PM-KISAN Uptake (%)', fontsize=12)
ax.set_title('Bottom 10 Districts by PM-KISAN Uptake\n(Priority Intervention Targets)', fontsize=14, fontweight='bold')
ax.legend()
for bar, val in zip(bars, bottom10['Uptake_Pct']):
    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
            f'{val}%', va='center', fontsize=10)
plt.tight_layout()
plt.savefig('outputs/01_bottom10_districts.png', dpi=150, bbox_inches='tight')
plt.close()
print(" Chart 1 saved")

# ── 2. Uptake Gap (absolute farmers not enrolled) ─────────────────────────
bottom10_gap = df.nsmallest(10, 'Uptake_Pct').copy()

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(bottom10_gap['District'] + ' (' + bottom10_gap['State'] + ')',
               bottom10_gap['Gap_Farmers'] / 1000, color='#e67e22', edgecolor='white')
ax.set_xlabel('Farmers NOT Enrolled (in thousands)', fontsize=12)
ax.set_title('Uptake Gap — Eligible Farmers Missing from PM-KISAN\n(Bottom 10 Districts)', fontsize=14, fontweight='bold')
for bar, val in zip(bars, bottom10_gap['Gap_Farmers']):
    ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
            f'{val:,}', va='center', fontsize=9)
plt.tight_layout()
plt.savefig('outputs/02_uptake_gap.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart 2 saved")

# ── 3. Correlation Heatmap ────────────────────────────────────────────────
corr_cols = ['Uptake_Pct','Literacy_Rate','Internet_Penetration',
             'Female_Farmer_Pct','Bank_Branch_Per_Lakh','ASHA_Worker_Coverage']
corr_matrix = df[corr_cols].corr()

fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdYlGn',
            center=0, ax=ax, linewidths=0.5)
ax.set_title('Correlation Matrix — PM-KISAN Uptake vs Socio-Economic Factors',
             fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('outputs/03_correlation_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()
print(" Chart 3 saved")

# ── 4. Scatter: Literacy vs Uptake ────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

for ax, xcol, xlabel in zip(axes,
    ['Literacy_Rate', 'Bank_Branch_Per_Lakh'],
    ['Literacy Rate (%)', 'Bank Branches per Lakh Population']):

    ax.scatter(df[xcol], df['Uptake_Pct'], alpha=0.7, color='#3498db', edgecolors='white', s=80)

    # Highlight bottom 10
    ax.scatter(bottom10[xcol], bottom10['Uptake_Pct'],
               color='#e74c3c', s=120, zorder=5, label='Bottom 10 Districts')

    # Regression line
    slope, intercept, r, p, _ = stats.linregress(df[xcol], df['Uptake_Pct'])
    x_line = np.linspace(df[xcol].min(), df[xcol].max(), 100)
    ax.plot(x_line, slope * x_line + intercept, color='#e74c3c',
            linewidth=2, linestyle='--')

    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel('PM-KISAN Uptake (%)', fontsize=11)
    ax.set_title(f'{xlabel} vs Uptake\n(r = {r:.2f}, p = {p:.3f})', fontsize=12, fontweight='bold')
    ax.legend()

plt.tight_layout()
plt.savefig('outputs/04_scatter_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
print(" Chart 4 saved")

# ── 5. State-wise Average Uptake ──────────────────────────────────────────
state_avg = df.groupby('State')['Uptake_Pct'].mean().sort_values()

fig, ax = plt.subplots(figsize=(10, 6))
bar_colors = ['#e74c3c' if v < 50 else '#f39c12' if v < 65 else '#2ecc71' for v in state_avg]
bars = ax.bar(state_avg.index, state_avg.values, color=bar_colors, edgecolor='white')
ax.axhline(df['Uptake_Pct'].mean(), color='navy', linestyle='--', linewidth=2,
           label=f'Overall Avg: {df["Uptake_Pct"].mean():.1f}%')
ax.set_ylabel('Average Uptake (%)', fontsize=12)
ax.set_title('State-wise Average PM-KISAN Uptake', fontsize=14, fontweight='bold')
ax.set_xticklabels(state_avg.index, rotation=30, ha='right')
red_patch = mpatches.Patch(color='#e74c3c', label='Critical (<50%)')
orange_patch = mpatches.Patch(color='#f39c12', label='Moderate (50-65%)')
green_patch = mpatches.Patch(color='#2ecc71', label='Good (>65%)')
ax.legend(handles=[red_patch, orange_patch, green_patch,
          plt.Line2D([0],[0], color='navy', linestyle='--', label=f'Overall Avg: {df["Uptake_Pct"].mean():.1f}%')])
plt.tight_layout()
plt.savefig('outputs/05_statewise_uptake.png', dpi=150, bbox_inches='tight')
plt.close()
print(" Chart 5 saved")

# ── 6. Print Statistical Summary ─────────────────────────────────────────
print("\n" + "="*55)
print("   PM-KISAN UPTAKE — STATISTICAL SUMMARY")
print("="*55)
print(f"Total Districts Analysed : {len(df)}")
print(f"National Avg Uptake      : {df['Uptake_Pct'].mean():.1f}%")
print(f"Highest Uptake           : {df['Uptake_Pct'].max():.1f}% ({df.loc[df['Uptake_Pct'].idxmax(),'District']})")
print(f"Lowest Uptake            : {df['Uptake_Pct'].min():.1f}% ({df.loc[df['Uptake_Pct'].idxmin(),'District']})")
print(f"Total Farmers in Gap     : {df['Gap_Farmers'].sum():,}")
print(f"\nBottom 10 Districts:")
print(bottom10[['District','State','Uptake_Pct','Gap_Farmers']].to_string(index=False))

# Correlation with uptake
print(f"\nCorrelation with Uptake:")
for col in ['Literacy_Rate','Internet_Penetration','Bank_Branch_Per_Lakh','ASHA_Worker_Coverage']:
    r, p = stats.pearsonr(df[col], df['Uptake_Pct'])
    print(f"  {col:<30} r={r:+.2f}  p={p:.3f}")

print("\n All 5 charts saved in outputs/ folder")