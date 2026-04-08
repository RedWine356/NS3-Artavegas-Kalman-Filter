import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ── Load CSV ──────────────────────────────────────────────────────────────────
df = pd.read_csv('/Users/ridhwanasif/Downloads/ns3/pyplots/adaptive_kalman.csv')

print("=" * 60)
print("TCP-ArtaVegas: Adaptive Kalman Filter Analysis")
print("=" * 60)
print(f"Total samples: {len(df)}")
print(f"Time range:     {df['Timestamp'].min():.2f}s to {df['Timestamp'].max():.2f}s")
print(f"Distance range: {df['Distance'].min():.2f}m to {df['Distance'].max():.2f}m")
print()

raw   = df['Raw_RTT_ms']
fixed = df['Fixed_Filtered_ms']
adapt = df['Adaptive_Filtered_ms']

def stats(series, name):
    print(f"{name}:")
    print(f"  Mean: {series.mean():.2f} ms  Std: {series.std():.2f} ms")
    print(f"  Min:  {series.min():.2f} ms   Max: {series.max():.2f} ms")

stats(raw,   "Raw RTT")
stats(fixed, "Fixed Kalman  (R=2.68)")
stats(adapt, "Adaptive Kalman (R=2.68 + 0.01*d)")

print()
print("Kalman Filter Effectiveness:")
fix_var_red  = (1 - fixed.std() / raw.std()) * 100
adap_var_red = (1 - adapt.std() / raw.std()) * 100
print(f"  Fixed    variance reduction: {fix_var_red:.1f}%")
print(f"  Adaptive variance reduction: {adap_var_red:.1f}%")
print(f"  Adaptive IMPROVEMENT:        {adap_var_red - fix_var_red:.1f}%")
print(f"  Fixed    peak reduction: {raw.max() - fixed.max():.2f} ms")
print(f"  Adaptive peak reduction: {raw.max() - adapt.max():.2f} ms")
print("=" * 60)

# ── Colors ────────────────────────────────────────────────────────────────────
C_RAW   = '#5C9BD6'   # blue
C_FIXED = '#E05C5C'   # red
C_ADAPT = '#4CAF50'   # green
C_GAIN  = '#9C27B0'   # purple
C_R     = '#FF9800'   # orange

# ── Figure: 8 panels ──────────────────────────────────────────────────────────
fig, axes = plt.subplots(4, 2, figsize=(15, 18))
fig.suptitle('TCP-ArtaVegas: Fixed vs Adaptive Kalman Filter Comparison',
             fontsize=14, fontweight='bold', y=0.99)

# ── [0,0] RTT over Time — all three ──────────────────────────────────────────
ax = axes[0, 0]
ax.plot(df['Timestamp'], raw,   color=C_RAW,   lw=0.5, alpha=0.6, label='Raw RTT')
ax.plot(df['Timestamp'], fixed, color=C_FIXED, lw=1.3, label='Fixed Kalman (R=2.68)')
ax.plot(df['Timestamp'], adapt, color=C_ADAPT, lw=1.3, label='Adaptive Kalman')
ax.set_xlabel('Time (s)')
ax.set_ylabel('RTT (ms)')
ax.set_title('RTT over Time: Raw vs Fixed vs Adaptive Kalman')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# ── [0,1] RTT vs Distance — all three ────────────────────────────────────────
ax = axes[0, 1]
ax.scatter(df['Distance'], raw,   s=2, alpha=0.3, color=C_RAW,   label='Raw RTT')
ax.scatter(df['Distance'], fixed, s=2, alpha=0.4, color=C_FIXED, label='Fixed Kalman')
ax.scatter(df['Distance'], adapt, s=2, alpha=0.4, color=C_ADAPT, label='Adaptive Kalman')
ax.set_xlabel('Distance (m)')
ax.set_ylabel('RTT (ms)')
ax.set_title('RTT vs Distance')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# ── [1,0] Distribution ────────────────────────────────────────────────────────
ax = axes[1, 0]
bins = np.linspace(min(raw.min(), fixed.min(), adapt.min()),
                   max(raw.max(), fixed.max(), adapt.max()), 60)
ax.hist(raw,   bins=bins, alpha=0.45, color=C_RAW,   label='Raw RTT',       edgecolor='none')
ax.hist(fixed, bins=bins, alpha=0.55, color=C_FIXED, label='Fixed Kalman',  edgecolor='none')
ax.hist(adapt, bins=bins, alpha=0.55, color=C_ADAPT, label='Adaptive Kalman', edgecolor='none')
ax.set_xlabel('RTT (ms)')
ax.set_ylabel('Frequency')
ax.set_title('RTT Distribution: Adaptive Kalman Narrows Spread More')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# ── [1,1] Spike absorption — Fixed Kalman ────────────────────────────────────
ax = axes[1, 1]
diff_fixed = raw - fixed
diff_adapt = raw - adapt
ax.fill_between(df['Timestamp'], 0, diff_fixed,
                where=(diff_fixed >= 0), color=C_FIXED, alpha=0.5,
                label='Fixed: Spike Absorbed')
ax.fill_between(df['Timestamp'], 0, diff_fixed,
                where=(diff_fixed < 0),  color='orange', alpha=0.4,
                label='Fixed: Filter Lag')
ax.axhline(0, color='black', lw=0.6)
ax.set_xlabel('Time (s)')
ax.set_ylabel('Raw − Fixed Filtered (ms)')
ax.set_title('Spike Absorption — Fixed Kalman')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# ── [2,0] Spike absorption — Adaptive Kalman ─────────────────────────────────
ax = axes[2, 0]
ax.fill_between(df['Timestamp'], 0, diff_adapt,
                where=(diff_adapt >= 0), color=C_ADAPT, alpha=0.5,
                label='Adaptive: Spike Absorbed')
ax.fill_between(df['Timestamp'], 0, diff_adapt,
                where=(diff_adapt < 0),  color='orange', alpha=0.4,
                label='Adaptive: Filter Lag')
ax.axhline(0, color='black', lw=0.6)
ax.set_xlabel('Time (s)')
ax.set_ylabel('Raw − Adaptive Filtered (ms)')
ax.set_title('Spike Absorption — Adaptive Kalman')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# ── [2,1] Kalman Gain comparison ─────────────────────────────────────────────
ax = axes[2, 1]
ax.plot(df['Timestamp'], df['K_fixed'],    color=C_FIXED, lw=1.2,
        label='K fixed (constant)')
ax.plot(df['Timestamp'], df['K_adaptive'], color=C_ADAPT, lw=1.2,
        label='K adaptive (decreases with distance)')
ax.axhline(0.5, color='gray', lw=1.0, ls='--', label='K=0.5 equal trust')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Kalman Gain (K)')
ax.set_ylim(0, 1.0)
ax.set_title('Kalman Gain: Fixed vs Adaptive\n(Lower K = more smoothing)')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# ── [3,0] R_adaptive over distance ───────────────────────────────────────────
ax = axes[3, 0]
ax.plot(df['Distance'], df['R_adaptive'], color=C_R, lw=1.5,
        label='R adaptive = 2.68 + 0.01×d')
ax.axhline(2.68, color=C_FIXED, lw=1.2, ls='--',
           label='R fixed = 2.68')
ax.set_xlabel('Distance (m)')
ax.set_ylabel('Measurement Noise R')
ax.set_title('Adaptive R grows with Distance\n(Physically motivated: farther = noisier)')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# ── [3,1] Rolling variance — all three ───────────────────────────────────────
ax = axes[3, 1]
window = 50
raw_var   = raw.rolling(window=window, min_periods=1).var()
fixed_var = fixed.rolling(window=window, min_periods=1).var()
adapt_var = adapt.rolling(window=window, min_periods=1).var()

ax.plot(df['Timestamp'], raw_var,   color=C_RAW,   lw=1.0, alpha=0.8,
        label='Raw Variance')
ax.plot(df['Timestamp'], fixed_var, color=C_FIXED, lw=1.2,
        label='Fixed Kalman Variance')
ax.plot(df['Timestamp'], adapt_var, color=C_ADAPT, lw=1.2,
        label='Adaptive Kalman Variance')
ax.set_xlabel('Time (s)')
ax.set_ylabel(f'Rolling Variance (window={window})')
ax.set_title('Variance Reduction: Adaptive Kalman outperforms Fixed')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.98])
out = '/Users/ridhwanasif/Downloads/ns3/pyplots/adaptive_kalman_analysis.png'
plt.savefig(out, dpi=150, bbox_inches='tight')
plt.show()
print(f"\nPlot saved to: {out}")