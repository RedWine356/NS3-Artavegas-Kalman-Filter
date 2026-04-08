NS3_DIR="/Users/ridhwanasif/Downloads/ns3/ns-3-dev"
WIRELESS_DIR="/Users/ridhwanasif/Downloads/ns3/pyplots/wireless"
SCRIPT="scratch/mob"
PLOT_SCRIPT="/Users/ridhwanasif/Downloads/ns3/pyplots/plotMetrics.py"

# ── Setup ─────────────────────────────────────────────────────────────────────
mkdir -p "$WIRELESS_DIR"
cd "$NS3_DIR"

echo "=================================================="
echo " Wireless Simulation Sweep"
echo " Output: $WIRELESS_DIR"
echo "=================================================="

# Delete stale CSVs and PNGs
rm -f "$WIRELESS_DIR/metrics.csv"
rm -f "$WIRELESS_DIR/per_node_throughput.csv"
rm -f "$WIRELESS_DIR/rtt_samples.csv"
rm -f "$WIRELESS_DIR/sweep_*.png"
rm -f "$WIRELESS_DIR/heatmap_summary.png"
rm -f "$WIRELESS_DIR/overview_all.png"
rm -f "$WIRELESS_DIR/per_node_throughput.png"
rm -f "$WIRELESS_DIR/kalman_analysis.png"
echo "Cleaned old files."
echo ""

# ── 1. Node Sweep (flows=10, pps=100, speed=10) ───────────────────────────────
echo "=== 1. Node Sweep (flows=10, pps=100, speed=10) ==="
for N in 20 40 60 80 100; do
    echo "→ nodes=$N"
    ./ns3 run "$SCRIPT \
        --nodes=$N --flows=10 --pps=100 --speed=10 --time=20 \
        --out=$WIRELESS_DIR/metrics.csv \
        --rtt=$WIRELESS_DIR/rtt_samples.csv \
        --pernode=$WIRELESS_DIR/per_node_throughput.csv" 2>/dev/null
done

# ── 2. Flow Sweep (nodes=60, pps=100, speed=10) ───────────────────────────────
echo ""
echo "=== 2. Flow Sweep (nodes=60, pps=100, speed=10) ==="
for F in 10 20 30 40 50; do
    echo "→ flows=$F"
    ./ns3 run "$SCRIPT \
        --nodes=60 --flows=$F --pps=100 --speed=10 --time=20 \
        --out=$WIRELESS_DIR/metrics.csv \
        --rtt=$WIRELESS_DIR/rtt_samples.csv \
        --pernode=$WIRELESS_DIR/per_node_throughput.csv" 2>/dev/null
done

# ── 3. PPS Sweep (nodes=40, flows=10, speed=10) ───────────────────────────────
echo ""
echo "=== 3. PPS Sweep (nodes=40, flows=10, speed=10) ==="
for P in 100 200 300 400 500; do
    echo "→ pps=$P"
    ./ns3 run "$SCRIPT \
        --nodes=40 --flows=10 --pps=$P --speed=10 --time=20 \
        --out=$WIRELESS_DIR/metrics.csv \
        --rtt=$WIRELESS_DIR/rtt_samples.csv \
        --pernode=$WIRELESS_DIR/per_node_throughput.csv" 2>/dev/null
done

# ── 4. Speed Sweep (nodes=40, flows=10, pps=100) ──────────────────────────────
echo ""
echo "=== 4. Speed Sweep (nodes=40, flows=10, pps=100) ==="
for S in 5 10 15 20 25; do
    echo "→ speed=$S m/s"
    ./ns3 run "$SCRIPT \
        --nodes=40 --flows=10 --pps=100 --speed=$S --time=20 \
        --out=$WIRELESS_DIR/metrics.csv \
        --rtt=$WIRELESS_DIR/rtt_samples.csv \
        --pernode=$WIRELESS_DIR/per_node_throughput.csv" 2>/dev/null
done

# ── Plot ──────────────────────────────────────────────────────────────────────
echo ""
echo "=== All wireless runs done. Plotting... ==="
python3 "$PLOT_SCRIPT" \
    --metrics "$WIRELESS_DIR/metrics.csv" \
    --rtt     "$WIRELESS_DIR/rtt_samples.csv" \
    --pernode "$WIRELESS_DIR/per_node_throughput.csv" \
    --out     "$WIRELESS_DIR"

echo ""
echo "=================================================="
echo " Wireless sweep complete!"
echo " Results in: $WIRELESS_DIR"
echo "=================================================="
