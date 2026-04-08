"""
plot_hybrid.py — Plots for hybrid wired+wireless TCP Vegas + Kalman simulation

Usage:
    python3 plot_hybrid.py \
        --metrics /path/to/metrics_hybrid.csv \
        --rtt     /path/to/rtt_hybrid.csv \
        --pernode /path/to/per_node_hybrid.csv \
        --out     /path/to/output/dir
"""

import argparse
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family":       "DejaVu Sans",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.grid":         True,
    "grid.alpha":        0.35,
    "grid.linestyle":    "--",
    "figure.dpi":        120,
})

PALETTE = {
    "Throughput_Mbps":   "#2196F3",
    "AvgDelay_ms":       "#FF5722",
    "PDR_pct":           "#4CAF50",
    "DropRate_pct":      "#F44336",
    "Energy_J_wifi":     "#9C27B0",
    "VarReduction_pct":  "#FF9800",
}

METRIC_LABELS = {
    "Throughput_Mbps":  ("Network Throughput",       "Throughput (Mbps)"),
    "AvgDelay_ms":      ("Avg End-to-End Delay",     "Delay (ms)"),
    "PDR_pct":          ("Packet Delivery Ratio",    "PDR (%)"),
    "DropRate_pct":     ("Packet Drop Ratio",        "Drop Rate (%)"),
    "Energy_J_wifi":    ("WiFi Node Energy",         "Energy (J)"),
    "VarReduction_pct": ("Kalman Var. Reduction",    "Var. Reduction (%)"),
}

# ── Filter helpers ────────────────────────────────────────────────────────────
def dedup(df, keys):
    existing = [k for k in keys if k in df.columns]
    return df.drop_duplicates(subset=existing, keep="last").reset_index(drop=True)


def plot_sweep_generic(df, x_col, x_label, x_xlabel,
                       fixed_cols, title_suffix, out_dir, fname_suffix):
    """Generic sweep plot — 6 panels."""
    df = dedup(df, list(fixed_cols.keys()) + [x_col])
    mask = pd.Series([True] * len(df), index=df.index)
    for col, val in fixed_cols.items():
        if col in df.columns:
            mask &= (df[col] == val)
    sweep = df[mask].sort_values(x_col)

    if sweep.empty:
        print(f"  [WARN] No data for {x_col} sweep. Skipping.")
        return

    metrics = [m for m in METRIC_LABELS if m in sweep.columns]
    ncols, nrows = 3, (len(metrics) + 2) // 3

    fig, axes = plt.subplots(nrows, ncols, figsize=(16, 5 * nrows))
    fig.suptitle(f"Hybrid Wired+Wireless TCP Vegas  ·  {title_suffix}",
                 fontsize=14, fontweight="bold", y=0.99)

    ax_flat = axes.flatten() if len(metrics) > 1 else [axes]
    x = sweep[x_col].values

    for ax, col in zip(ax_flat, metrics):
        y     = sweep[col].values
        color = PALETTE.get(col, "#607D8B")
        title, ylabel = METRIC_LABELS[col]

        ax.plot(x, y, "o-", color=color, linewidth=2.2, markersize=8,
                markerfacecolor="white", markeredgewidth=2.2,
                markeredgecolor=color, zorder=3)
        ax.fill_between(x, y, alpha=0.07, color=color)
        for xi, yi in zip(x, y):
            ax.annotate(f"{yi:.2f}", xy=(xi, yi), xytext=(0, 9),
                        textcoords="offset points", ha="center",
                        fontsize=8, color=color, fontweight="bold")
        ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
        ax.set_xlabel(x_xlabel, fontsize=10)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_xticks(x)
        ax.tick_params(labelsize=9)

    for ax in ax_flat[len(metrics):]:
        ax.axis("off")

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    fname = os.path.join(out_dir, f"hybrid_sweep_{fname_suffix}.png")
    plt.savefig(fname, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {fname}")


def plot_kalman_rtt(rtt_csv, out_dir):
    """6-panel Kalman analysis for hybrid RTT."""
    if not os.path.exists(rtt_csv):
        print(f"  [SKIP] RTT file not found: {rtt_csv}")
        return

    df = pd.read_csv(rtt_csv)
    if df.empty:
        return

    raw   = df["Raw_RTT_ms"].values
    filt  = df["Filtered_RTT_ms"].values
    t     = df["Timestamp"].values
    dist  = df["Distance"].values
    K     = df["Kalman_Gain"].values
    R_adp = df["R_adaptive"].values if "R_adaptive" in df.columns else None

    RAW_C  = "#5C9BD6"
    FILT_C = "#E05C5C"
    K_C    = "#9C27B0"
    R_C    = "#FF9800"

    fig, axes = plt.subplots(3, 2, figsize=(16, 13))
    fig.suptitle("Hybrid Network: Adaptive Kalman RTT Smoothing\n"
                 "(Wired baseline + Wireless jitter combined)",
                 fontsize=13, fontweight="bold", y=0.99)

    # RTT over time
    axes[0,0].plot(t, raw,  color=RAW_C,  lw=0.6, alpha=0.7, label="Raw RTT")
    axes[0,0].plot(t, filt, color=FILT_C, lw=1.4, label="Filtered (Adaptive Kalman)")
    axes[0,0].set_title("RTT over Time: Raw vs Filtered", fontsize=11, fontweight="bold")
    axes[0,0].set_xlabel("Time (s)"); axes[0,0].set_ylabel("RTT (ms)")
    axes[0,0].legend(fontsize=9)

    # RTT vs distance
    axes[0,1].scatter(dist, raw,  s=3, color=RAW_C,  alpha=0.4, label="Raw RTT")
    axes[0,1].scatter(dist, filt, s=3, color=FILT_C, alpha=0.5, label="Filtered")
    axes[0,1].set_title("RTT vs Distance (wireless segment)", fontsize=11, fontweight="bold")
    axes[0,1].set_xlabel("Distance (m)"); axes[0,1].set_ylabel("RTT (ms)")
    axes[0,1].legend(fontsize=9)

    # Distribution
    bins = np.linspace(min(raw.min(), filt.min()),
                       max(raw.max(), filt.max()), 50)
    axes[1,0].hist(raw,  bins=bins, color=RAW_C,  alpha=0.6, label="Raw",     edgecolor="none")
    axes[1,0].hist(filt, bins=bins, color=FILT_C, alpha=0.6, label="Filtered",edgecolor="none")
    axes[1,0].set_title("RTT Distribution: Kalman Narrows Spread", fontsize=11, fontweight="bold")
    axes[1,0].set_xlabel("RTT (ms)"); axes[1,0].set_ylabel("Frequency")
    axes[1,0].legend(fontsize=9)

    # Spike absorption
    diff = raw - filt
    axes[1,1].fill_between(t, diff, 0, where=(diff >= 0), color="#4CAF50",
                           alpha=0.7, label="Spike Absorbed")
    axes[1,1].fill_between(t, diff, 0, where=(diff < 0),  color="#FF9800",
                           alpha=0.7, label="Filter Lag")
    axes[1,1].axhline(0, color="black", lw=0.8)
    axes[1,1].set_title("Spike Absorption by Adaptive Kalman", fontsize=11, fontweight="bold")
    axes[1,1].set_xlabel("Time (s)"); axes[1,1].set_ylabel("Raw − Filtered (ms)")
    axes[1,1].legend(fontsize=9)

    # Kalman gain
    axes[2,0].plot(t, K, color=K_C, lw=1.2, label="K adaptive")
    axes[2,0].axhline(0.5, color="gray", lw=1.0, ls="--", label="K=0.5 equal trust")
    axes[2,0].set_ylim(0, 1.0)
    axes[2,0].set_title("Kalman Gain (decreases as vehicle moves away)",
                         fontsize=11, fontweight="bold")
    axes[2,0].set_xlabel("Time (s)"); axes[2,0].set_ylabel("Kalman Gain K")
    axes[2,0].legend(fontsize=9)

    # R_adaptive vs distance
    if R_adp is not None:
        axes[2,1].plot(dist, R_adp, color=R_C, lw=1.5,
                       label="R = 2.68 + 0.01×distance")
        axes[2,1].axhline(2.68, color=FILT_C, lw=1.2, ls="--",
                          label="Fixed R = 2.68")
        axes[2,1].set_title("Adaptive R grows with Distance\n"
                             "(wired portion has stable baseline)",
                             fontsize=11, fontweight="bold")
        axes[2,1].set_xlabel("Distance (m)"); axes[2,1].set_ylabel("R (measurement noise)")
        axes[2,1].legend(fontsize=9)
    else:
        axes[2,1].axis("off")

    raw_range  = raw.max() - raw.min()
    filt_range = filt.max() - filt.min()
    var_red    = (1 - filt_range/raw_range)*100 if raw_range > 0 else 0
    peak_red   = raw.max() - filt.max()
    txt = (f"Raw:  avg={raw.mean():.2f}ms  max={raw.max():.1f}ms\n"
           f"Filt: avg={filt.mean():.2f}ms  max={filt.max():.1f}ms\n"
           f"Peak reduction: {peak_red:.1f}ms  |  Var reduction: {var_red:.1f}%")
    fig.text(0.5, 0.005, txt, ha="center", fontsize=9,
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#f5f5f5",
                       edgecolor="#cccccc"))

    plt.tight_layout(rect=[0, 0.04, 1, 0.98])
    fname = os.path.join(out_dir, "hybrid_kalman_rtt.png")
    plt.savefig(fname, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {fname}")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics",
        default="/Users/ridhwanasif/Downloads/ns3/pyplots/metrics_hybrid.csv")
    parser.add_argument("--rtt",
        default="/Users/ridhwanasif/Downloads/ns3/pyplots/rtt_hybrid.csv")
    parser.add_argument("--pernode",
        default="/Users/ridhwanasif/Downloads/ns3/pyplots/per_node_hybrid.csv")
    parser.add_argument("--out",
        default="/Users/ridhwanasif/Downloads/ns3/pyplots")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    # RTT Kalman analysis
    print("\n=== Hybrid Kalman RTT Analysis ===")
    plot_kalman_rtt(args.rtt, args.out)

    if not os.path.exists(args.metrics):
        print(f"[SKIP] Metrics not found: {args.metrics}")
    else:
        df = pd.read_csv(args.metrics)
        print(f"\nLoaded {len(df)} rows")
        print(df.to_string(index=False))

        # Create a "TotalNodes" column for node sweep
        if "WiredNodes" in df.columns and "MobileNodes" in df.columns:
            df["TotalNodes"] = df["WiredNodes"] + df["MobileNodes"]

        print("\n=== Parameter Sweep Plots ===")

        # Node sweep
        plot_sweep_generic(
            df, "TotalNodes", "Total Nodes", "Wired + Mobile Nodes",
            {"PPS": 100, "Speed_ms": 10, "Coverage": 1},  # ← removed Flows
            "Varying Number of Nodes", args.out, "nodes")

        # Flow sweep
        plot_sweep_generic(
            df, "Flows", "Flows", "Number of Flows",
            {"WiredNodes": 10, "MobileNodes": 10, "PPS": 100,
             "Speed_ms": 10, "Coverage": 1},
            "Varying Number of Flows", args.out, "flows")

        # PPS sweep
        plot_sweep_generic(
            df, "PPS", "PPS", "Packets/s",
            {"WiredNodes": 10, "MobileNodes": 10, "Flows": 10,
             "Speed_ms": 10, "Coverage": 1},
            "Varying Packets per Second", args.out, "pps")

        # Speed sweep
        plot_sweep_generic(
            df, "Speed_ms", "Speed", "Speed (m/s)",
            {"WiredNodes": 10, "MobileNodes": 10, "Flows": 10,
             "PPS": 100, "Coverage": 1},
            "Varying Vehicle Speed", args.out, "speed")

        # Coverage sweep
        plot_sweep_generic(
            df, "Coverage", "Coverage", "Coverage (x Tx_range)",
            {"WiredNodes": 10, "MobileNodes": 10, "Flows": 10,
             "PPS": 100, "Speed_ms": 10},
            "Varying Coverage Area", args.out, "coverage")

    print(f"\nAll done. Plots in: {args.out}")