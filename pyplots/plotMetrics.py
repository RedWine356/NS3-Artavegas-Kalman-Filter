"""
plot_all.py  —  Complete plotting script for TCP-Vegas + Kalman Filter project
Generates:
  Figure Set 1: 6-panel Kalman RTT analysis (from rtt_samples CSV)
  Figure Set 2: Parameter sweep line plots (from metrics CSV)
  Figure Set 3: Heatmap summary

Usage:
    python3 plot_all.py \
        --metrics /Users/ridhwanasif/Downloads/ns3/pyplots/metrics.csv \
        --rtt     /Users/ridhwanasif/Downloads/ns3/pyplots/rtt_samples.csv \
        --out     /Users/ridhwanasif/Downloads/ns3/pyplots
"""

import argparse
import os
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import Normalize
import matplotlib.cm as cm

# ── Global style ──────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":      "DejaVu Sans",
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "axes.grid":        True,
    "grid.alpha":       0.35,
    "grid.linestyle":   "--",
    "figure.dpi":       120,
})

RAW_COL      = "#5C9BD6"   # blue  — raw RTT
FILT_COL     = "#E05C5C"   # red   — filtered RTT
SPIKE_COL    = "#4CAF50"   # green — spike absorbed
LAG_COL      = "#FF9800"   # orange— filter lag
GAIN_COL     = "#9C27B0"   # purple— Kalman gain
VAR_RAW_COL  = "#5C9BD6"
VAR_FILT_COL = "#E05C5C"

PALETTE = {
    "Throughput_Mbps":   "#2196F3",
    "AvgDelay_ms":       "#FF5722",
    "PDR_pct":           "#4CAF50",
    "DropRate_pct":      "#F44336",
    "Energy_J_per_node": "#9C27B0",
    "VarReduction_pct":  "#FF9800",
}

METRIC_LABELS = {
    "Throughput_Mbps":   ("Network Throughput",       "Throughput (Mbps)"),
    "AvgDelay_ms":       ("Avg End-to-End Delay",     "Delay (ms)"),
    "PDR_pct":           ("Packet Delivery Ratio",    "PDR (%)"),
    "DropRate_pct":      ("Packet Drop Ratio",        "Drop Rate (%)"),
    "Energy_J_per_node": ("Energy per Node",          "Energy (J)"),
    "VarReduction_pct":  ("Kalman Variance Reduction","Var. Reduction (%)"),
}

PARAM_META = {
    "Nodes":    ("Number of Nodes",    "Nodes"),
    "Flows":    ("Number of Flows",    "Flows"),
    "PPS":      ("Packets per Second", "Packets/s"),
    "Speed_ms": ("Vehicle Speed",      "Speed (m/s)"),
}

FIXED = {
    "Nodes":    {"Flows": 10,  "PPS": 100, "Speed_ms": 10},
    "Flows":    {"Nodes": 60,  "PPS": 100, "Speed_ms": 10},
    "PPS":      {"Nodes": 40,  "Flows": 10, "Speed_ms": 10},
    "Speed_ms": {"Nodes": 40,  "Flows": 10, "PPS": 100},
}


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE SET 1  —  6-panel Kalman RTT Analysis
# ═══════════════════════════════════════════════════════════════════════════════

def plot_kalman_analysis(rtt_csv, out_dir, tag=""):
    """
    Reproduces the 6-panel figure you had before:
      [0,0] RTT over time       [0,1] RTT vs distance
      [1,0] RTT distribution    [1,1] Spike absorption
      [2,0] Kalman gain         [2,1] Rolling variance
    """
    if not os.path.exists(rtt_csv):
        print(f"  [SKIP] RTT file not found: {rtt_csv}")
        return

    df = pd.read_csv(rtt_csv)
    if df.empty:
        print(f"  [SKIP] RTT file is empty.")
        return

    raw  = df["Raw_RTT_ms"].values
    filt_col = "Filtered_RTT_ms" if "Filtered_RTT_ms" in df.columns else "Fixed_Filtered_ms"
    filt = df[filt_col].values
    t    = df["Timestamp"].values
    dist = df["Distance"].values
    K_col = "Kalman_Gain" if "Kalman_Gain" in df.columns else "K_fixed"
    K = df[K_col].values
    fig = plt.figure(figsize=(16, 13))
    fig.suptitle(
        f"TCP-ArtaVegas: Kalman Filter RTT Smoothing Analysis  {tag}",
        fontsize=14, fontweight="bold", y=0.99
    )
    gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.42, wspace=0.32)

    # ── [0,0] RTT over time ───────────────────────────────────────────────
    ax00 = fig.add_subplot(gs[0, 0])
    ax00.plot(t, raw,  color=RAW_COL,  linewidth=0.6, alpha=0.7, label="Raw RTT")
    ax00.plot(t, filt, color=FILT_COL, linewidth=1.4, label="Filtered RTT (Kalman)")
    ax00.set_title("RTT over Time: Raw vs Kalman Filtered", fontsize=11, fontweight="bold")
    ax00.set_xlabel("Time (s)")
    ax00.set_ylabel("RTT (ms)")
    ax00.legend(fontsize=9)

    # ── [0,1] RTT vs distance ─────────────────────────────────────────────
    ax01 = fig.add_subplot(gs[0, 1])
    ax01.scatter(dist, raw,  s=3, color=RAW_COL,  alpha=0.45, label="Raw RTT")
    ax01.scatter(dist, filt, s=3, color=FILT_COL, alpha=0.55, label="Filtered RTT")
    ax01.set_title("RTT vs Distance: Raw vs Kalman Filtered", fontsize=11, fontweight="bold")
    ax01.set_xlabel("Distance (m)")
    ax01.set_ylabel("RTT (ms)")
    ax01.legend(fontsize=9)

    # ── [1,0] RTT distribution ────────────────────────────────────────────
    ax10 = fig.add_subplot(gs[1, 0])
    bins = np.linspace(min(raw.min(), filt.min()),
                       max(raw.max(), filt.max()), 50)
    ax10.hist(raw,  bins=bins, color=RAW_COL,  alpha=0.6, label="Raw RTT",      edgecolor="none")
    ax10.hist(filt, bins=bins, color=FILT_COL, alpha=0.6, label="Filtered RTT", edgecolor="none")
    ax10.set_title("RTT Distribution: Kalman Filter Narrows the Spread",
                   fontsize=11, fontweight="bold")
    ax10.set_xlabel("RTT (ms)")
    ax10.set_ylabel("Frequency")
    ax10.legend(fontsize=9)

    # ── [1,1] Spike absorption ────────────────────────────────────────────
    ax11 = fig.add_subplot(gs[1, 1])
    diff = raw - filt
    ax11.fill_between(t, diff, 0,
                      where=(diff >= 0), color=SPIKE_COL, alpha=0.7,
                      label="Spike Absorbed")
    ax11.fill_between(t, diff, 0,
                      where=(diff < 0),  color=LAG_COL,   alpha=0.7,
                      label="Filter Lag")
    ax11.axhline(0, color="black", linewidth=0.8)
    ax11.set_title("Spike Absorption by Kalman Filter", fontsize=11, fontweight="bold")
    ax11.set_xlabel("Time (s)")
    ax11.set_ylabel("Raw − Filtered RTT (ms)")
    ax11.legend(fontsize=9)

    # ── [2,0] Kalman gain evolution ───────────────────────────────────────
    ax20 = fig.add_subplot(gs[2, 0])
    ax20.plot(t, K, color=GAIN_COL, linewidth=1.2, label="Kalman Gain K")
    ax20.axhline(0.5, color="gray", linewidth=1.0, linestyle="--",
                 label="K=0.5 (Equal Trust)")
    ax20.set_ylim(0, 1.0)
    ax20.set_title("Kalman Gain Evolution (Lower = More Smoothing)",
                   fontsize=11, fontweight="bold")
    ax20.set_xlabel("Time (s)")
    ax20.set_ylabel("Kalman Gain (K)")
    ax20.legend(fontsize=9)

    # ── [2,1] Rolling variance ────────────────────────────────────────────
    ax21 = fig.add_subplot(gs[2, 1])
    window = min(50, len(raw) // 4) if len(raw) > 8 else 2
    raw_s  = pd.Series(raw)
    filt_s = pd.Series(filt)
    raw_var  = raw_s.rolling(window).var().values
    filt_var = filt_s.rolling(window).var().values
    ax21.plot(t, raw_var,  color=VAR_RAW_COL,  linewidth=1.0,
              label=f"Raw RTT Variance",       alpha=0.85)
    ax21.plot(t, filt_var, color=VAR_FILT_COL, linewidth=1.0,
              label=f"Filtered RTT Variance",  alpha=0.85)
    ax21.set_title(f"Variance Reduction by Kalman Filter (window={window})",
                   fontsize=11, fontweight="bold")
    ax21.set_xlabel("Time (s)")
    ax21.set_ylabel(f"Rolling Variance (window={window})")
    ax21.legend(fontsize=9)

    # ── Stats annotation ──────────────────────────────────────────────────
    raw_range  = raw.max()  - raw.min()
    filt_range = filt.max() - filt.min()
    var_red    = (1 - filt_range / raw_range) * 100 if raw_range > 0 else 0
    peak_red   = raw.max() - filt.max()
    txt = (f"Raw:  avg={raw.mean():.2f}ms  max={raw.max():.1f}ms\n"
           f"Filt: avg={filt.mean():.2f}ms  max={filt.max():.1f}ms\n"
           f"Peak reduction: {peak_red:.1f}ms  |  Var reduction: {var_red:.1f}%")
    fig.text(0.5, 0.005, txt, ha="center", fontsize=9,
             color="#333333",
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#f5f5f5",
                       edgecolor="#cccccc"))

    safe = tag.replace(" ", "_").replace("=", "").replace(",", "")
    fname = os.path.join(out_dir, f"kalman_analysis{safe}.png")
    plt.savefig(fname, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {fname}")


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE SET 2  —  Parameter sweep line plots
# ═══════════════════════════════════════════════════════════════════════════════

def filter_sweep(df, varied_param):
    fixed = FIXED[varied_param]
    mask  = pd.Series([True] * len(df), index=df.index)
    for col, val in fixed.items():
        if col in df.columns:
            mask &= (df[col] == val)
    return df[mask].sort_values(varied_param)


def plot_sweep(df, varied_param, out_dir):
    """
    6-panel figure: 5 metrics + Kalman variance reduction vs one swept parameter.
    """
    sweep = filter_sweep(df, varied_param)
    if sweep.empty:
        print(f"  [WARN] No data for sweep: {varied_param}. Skipping.")
        return

    param_label, param_xlabel = PARAM_META[varied_param]
    x = sweep[varied_param].values

    metrics_to_plot = [
        "Throughput_Mbps",
        "AvgDelay_ms",
        "PDR_pct",
        "DropRate_pct",
        "Energy_J_per_node",
        "VarReduction_pct",
    ]

    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle(
        f"TCP-Vegas + Kalman Filter  ·  Varying {param_label}",
        fontsize=14, fontweight="bold", y=0.99
    )

    for ax, col in zip(axes.flatten(), metrics_to_plot):
        if col not in sweep.columns:
            ax.axis("off")
            continue

        y     = sweep[col].values
        color = PALETTE.get(col, "#607D8B")
        title, ylabel = METRIC_LABELS[col]

        ax.plot(x, y, "o-", color=color, linewidth=2.2,
                markersize=8, markerfacecolor="white",
                markeredgewidth=2.2, markeredgecolor=color,
                zorder=3)
        ax.fill_between(x, y, alpha=0.07, color=color)

        # Annotate points
        for xi, yi in zip(x, y):
            ax.annotate(f"{yi:.2f}",
                        xy=(xi, yi), xytext=(0, 9),
                        textcoords="offset points",
                        ha="center", fontsize=8, color=color,
                        fontweight="bold")

        ax.set_title(title,    fontsize=11, fontweight="bold", pad=8)
        ax.set_xlabel(param_xlabel, fontsize=10)
        ax.set_ylabel(ylabel,  fontsize=10)
        ax.set_xticks(x)
        ax.tick_params(labelsize=9)

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    fname = os.path.join(out_dir, f"sweep_{varied_param.lower()}.png")
    plt.savefig(fname, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {fname}")


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE SET 3  —  Heatmap summary
# ═══════════════════════════════════════════════════════════════════════════════

def plot_heatmap(df, out_dir):
    """
    Heatmap: rows = metrics, columns = (param, level) combinations.
    Color = normalized value per metric (0=worst, 1=best).
    """
    metrics = [
        "Throughput_Mbps",
        "AvgDelay_ms",
        "PDR_pct",
        "DropRate_pct",
        "Energy_J_per_node",
        "VarReduction_pct",
    ]
    metrics = [m for m in metrics if m in df.columns]

    # Build a matrix: one column per (param, level)
    col_labels = []
    data_cols   = []

    for param, (param_label, _) in PARAM_META.items():
        sweep = filter_sweep(df, param)
        if sweep.empty:
            continue
        for _, row in sweep.iterrows():
            level = row[param]
            col_labels.append(f"{param_label[:6]}.\n={level:.0f}")
            data_cols.append([row[m] if m in row else np.nan for m in metrics])

    if not data_cols:
        print("  [WARN] No data for heatmap.")
        return

    matrix = np.array(data_cols).T   # shape: (n_metrics, n_cols)

    # Normalize each row 0→1
    # For metrics where lower=better (delay, drop, energy), invert
    lower_is_better = {"AvgDelay_ms", "DropRate_pct", "Energy_J_per_node"}
    norm_matrix = np.zeros_like(matrix)
    for i, m in enumerate(metrics):
        row = matrix[i]
        rmin, rmax = np.nanmin(row), np.nanmax(row)
        if rmax > rmin:
            normed = (row - rmin) / (rmax - rmin)
        else:
            normed = np.zeros_like(row)
        if m in lower_is_better:
            normed = 1 - normed   # invert: low value = good = bright
        norm_matrix[i] = normed

    metric_labels_short = [METRIC_LABELS[m][0] for m in metrics]

    fig, ax = plt.subplots(figsize=(max(14, len(col_labels) * 0.85), 6))
    fig.suptitle("Performance Heatmap — All Sweeps  (Green=Good, Red=Poor)",
                 fontsize=13, fontweight="bold")

    im = ax.imshow(norm_matrix, aspect="auto", cmap="RdYlGn",
                   vmin=0, vmax=1, interpolation="nearest")

    ax.set_xticks(range(len(col_labels)))
    ax.set_xticklabels(col_labels, fontsize=8, rotation=0)
    ax.set_yticks(range(len(metric_labels_short)))
    ax.set_yticklabels(metric_labels_short, fontsize=10)

    # Annotate cells with raw values
    for i in range(len(metrics)):
        for j in range(len(col_labels)):
            val = matrix[i, j]
            txt = f"{val:.1f}"
            brightness = norm_matrix[i, j]
            text_color = "black" if 0.25 < brightness < 0.75 else "white" if brightness <= 0.25 else "black"
            ax.text(j, i, txt, ha="center", va="center",
                    fontsize=7.5, color=text_color, fontweight="bold")

    # Vertical separators between param groups
    col_idx = 0
    for param in PARAM_META:
        sweep = filter_sweep(df, param)
        n = len(sweep)
        if n == 0:
            continue
        col_idx += n
        if col_idx < len(col_labels):
            ax.axvline(col_idx - 0.5, color="white", linewidth=2)

    plt.colorbar(im, ax=ax, label="Normalized Performance (1=Best)",
                 fraction=0.02, pad=0.02)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    fname = os.path.join(out_dir, "heatmap_summary.png")
    plt.savefig(fname, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {fname}")


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE SET 4  —  Combined overview (4 metrics, all sweeps on one figure)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_combined_overview(df, out_dir):
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle("All Metrics — All Parameter Sweeps Combined",
                 fontsize=14, fontweight="bold")

    all_metrics = [
        "Throughput_Mbps",
        "AvgDelay_ms",
        "PDR_pct",
        "DropRate_pct",
        "Energy_J_per_node",
        "VarReduction_pct",
    ]
    linestyles = ["-o", "-s", "-^", "-D"]
    colors_per_param = ["#2196F3", "#FF5722", "#4CAF50", "#9C27B0"]

    for ax, col in zip(axes.flatten(), all_metrics):
        if col not in df.columns:
            ax.axis("off")
            continue
        title, ylabel = METRIC_LABELS[col]
        for (param, (plabel, _)), ls, pc in zip(
                PARAM_META.items(), linestyles, colors_per_param):
            sweep = filter_sweep(df, param)
            if sweep.empty:
                continue
            x = np.arange(len(sweep))
            y = sweep[col].values
            ax.plot(x, y, ls, linewidth=1.9, markersize=6,
                    label=plabel, color=pc, alpha=0.85)

        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.set_xlabel("Parameter Level  (L1 → L5)", fontsize=9)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.set_xticks(range(5))
        ax.set_xticklabels(["L1", "L2", "L3", "L4", "L5"], fontsize=8)
        ax.legend(fontsize=7.5, loc="best")

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fname = os.path.join(out_dir, "overview_all.png")
    plt.savefig(fname, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {fname}")


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE SET 5  —  Per-node throughput (bonus metric)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_per_node_throughput(pernode_csv, out_dir):
    if not os.path.exists(pernode_csv):
        print(f"  [SKIP] Per-node file not found: {pernode_csv}")
        return

    df = pd.read_csv(pernode_csv)
    if df.empty:
        print(f"  [SKIP] Per-node file is empty.")
        return

    COLOR_BAR  = "#2196F3"
    COLOR_LINE = "#FF5722"
    COLOR_BOX  = "#4CAF50"

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle("Per-Node Throughput Analysis  (Bonus Metric)",
                 fontsize=14, fontweight="bold")

    # Panel 1: Bar chart for baseline run
    baseline = df[(df["Nodes"] == 20) & (df["Flows"] == 10) &
                  (df["PPS"]   == 100) & (df["Speed_ms"] == 10)]
    if baseline.empty:
        first    = df.iloc[0]
        baseline = df[(df["Nodes"]    == first["Nodes"])   &
                      (df["Flows"]    == first["Flows"])   &
                      (df["PPS"]      == first["PPS"])     &
                      (df["Speed_ms"] == first["Speed_ms"])]

    ax = axes[0]
    if not baseline.empty:
        nodes_idx = baseline["NodeIndex"].values
        tp        = baseline["Throughput_Mbps"].values
        bars = ax.bar(nodes_idx, tp, color=COLOR_BAR, alpha=0.8,
                      edgecolor="white", linewidth=0.5)
        for bar, val in zip(bars, tp):
            ax.text(bar.get_x() + bar.get_width()/2,
                    bar.get_height() + 0.01 * max(tp),
                    f"{val:.2f}", ha="center", va="bottom",
                    fontsize=7, color=COLOR_BAR, fontweight="bold")
        cfg = baseline.iloc[0]
        ax.set_title(
            f"Per-Node Throughput (Baseline)\n"
            f"nodes={int(cfg['Nodes'])}, flows={int(cfg['Flows'])}, "
            f"pps={int(cfg['PPS'])}, speed={cfg['Speed_ms']:.0f}m/s",
            fontsize=10, fontweight="bold")
        ax.set_xlabel("Node Index")
        ax.set_ylabel("Throughput (Mbps)")
        ax.set_xticks(nodes_idx)
        ax.tick_params(axis="x", labelsize=8)
        ax.grid(True, axis="y", linestyle="--", alpha=0.4)

    # Panel 2: Avg per-node throughput vs node count
    ax2 = axes[1]
    sweep_df = df[(df["Flows"] == 10) & (df["PPS"] == 100) & (df["Speed_ms"] == 10)]
    if sweep_df.empty:
        sweep_df = df

    node_counts = sorted(sweep_df["Nodes"].unique())
    avg_tp = [sweep_df[sweep_df["Nodes"] == n]["Throughput_Mbps"].mean() for n in node_counts]
    min_tp = [sweep_df[sweep_df["Nodes"] == n]["Throughput_Mbps"].min()  for n in node_counts]
    max_tp = [sweep_df[sweep_df["Nodes"] == n]["Throughput_Mbps"].max()  for n in node_counts]

    ax2.plot(node_counts, avg_tp, "o-", color=COLOR_LINE, linewidth=2.2,
             markersize=8, markerfacecolor="white", markeredgewidth=2.2,
             markeredgecolor=COLOR_LINE, label="Avg per-node throughput")
    ax2.fill_between(node_counts, min_tp, max_tp, alpha=0.15,
                     color=COLOR_LINE, label="Min-Max range")
    for xi, yi in zip(node_counts, avg_tp):
        ax2.annotate(f"{yi:.2f}", xy=(xi, yi), xytext=(0, 9),
                     textcoords="offset points", ha="center",
                     fontsize=8, color=COLOR_LINE, fontweight="bold")
    ax2.set_title("Avg Per-Node Throughput vs Node Count\n(shaded = min/max range)",
                  fontsize=10, fontweight="bold")
    ax2.set_xlabel("Number of Nodes")
    ax2.set_ylabel("Throughput (Mbps)")
    ax2.set_xticks(node_counts)
    ax2.legend(fontsize=8)
    ax2.grid(True, linestyle="--", alpha=0.4)

    # Panel 3: Box plot
    ax3 = axes[2]
    box_data = [sweep_df[sweep_df["Nodes"] == n]["Throughput_Mbps"].values
                for n in node_counts]
    bp = ax3.boxplot(box_data, patch_artist=True,
                     medianprops=dict(color="white", linewidth=2),
                     whiskerprops=dict(color=COLOR_BOX),
                     capprops=dict(color=COLOR_BOX),
                     flierprops=dict(marker="o", color=COLOR_BOX,
                                     markersize=4, alpha=0.5))
    for patch in bp["boxes"]:
        patch.set_facecolor(COLOR_BOX)
        patch.set_alpha(0.6)
    ax3.set_title("Throughput Distribution per Node Count\n"
                  "(tighter box = fairer sharing among nodes)",
                  fontsize=10, fontweight="bold")
    ax3.set_xlabel("Number of Nodes")
    ax3.set_ylabel("Per-Node Throughput (Mbps)")
    ax3.set_xticklabels([str(n) for n in node_counts], fontsize=9)
    ax3.grid(True, axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fname = os.path.join(out_dir, "per_node_throughput.png")
    plt.savefig(fname, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {fname}")


# ═══════════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate all plots for NS-3 TCP-Vegas Kalman project")
    parser.add_argument("--metrics",
        default="/Users/ridhwanasif/Downloads/ns3/pyplots/metrics.csv")
    parser.add_argument("--rtt",
        default="/Users/ridhwanasif/Downloads/ns3/pyplots/rtt_samples.csv")
    parser.add_argument("--pernode",
        default="/Users/ridhwanasif/Downloads/ns3/pyplots/per_node_throughput.csv")
    parser.add_argument("--out",
        default="/Users/ridhwanasif/Downloads/ns3/pyplots")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    # Figure Set 1
    print("\n=== Figure Set 1: Kalman RTT Analysis ===")
    if args.rtt and os.path.exists(args.rtt):
        plot_kalman_analysis(args.rtt, args.out)
    else:
        rtt_files = [f for f in os.listdir(args.out)
                     if f.startswith("rtt_") and f.endswith(".csv")]
        if rtt_files:
            rtt_files.sort()
            for rf in rtt_files:
                tag = rf.replace("rtt_","").replace(".csv","")
                plot_kalman_analysis(os.path.join(args.out, rf),
                                     args.out, tag=f"_{tag}")
        else:
            print("  [SKIP] No RTT CSV found.")

    # Figure Set 2
    print("\n=== Figure Set 2: Parameter Sweep Plots ===")
    if not os.path.exists(args.metrics):
        print(f"  [SKIP] Metrics file not found: {args.metrics}")
    else:
        df = pd.read_csv(args.metrics)
        print(f"  Loaded {len(df)} rows")
        for param in PARAM_META:
            print(f"  Plotting sweep: {param}")
            plot_sweep(df, param, args.out)

        print("\n=== Figure Set 3: Heatmap Summary ===")
        plot_heatmap(df, args.out)

        print("\n=== Figure Set 4: Combined Overview ===")
        plot_combined_overview(df, args.out)

    # Figure Set 5
    print("\n=== Figure Set 5: Per-Node Throughput ===")
    plot_per_node_throughput(args.pernode, args.out)

    print(f"\nAll done. Plots saved to: {args.out}")