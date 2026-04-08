NS3_DIR="/Users/ridhwanasif/Downloads/ns3/ns-3-dev"
HYBRID_DIR="/Users/ridhwanasif/Downloads/ns3/pyplots/hybrid"
SCRIPT="scratch/hybrid"
PLOT_SCRIPT="/Users/ridhwanasif/Downloads/ns3/pyplots/plotHybrid.py"

# ── Setup ─────────────────────────────────────────────────────────────────────
mkdir -p "$HYBRID_DIR"
cd "$NS3_DIR"

echo "=================================================="
echo " Hybrid Wired+Wireless Simulation Sweep"
echo " Output: $HYBRID_DIR"
echo "=================================================="

rm -f "$HYBRID_DIR/metrics_hybrid.csv"
rm -f "$HYBRID_DIR/rtt_hybrid.csv"
rm -f "$HYBRID_DIR/per_node_hybrid.csv"
rm -f "$HYBRID_DIR/hybrid_*.png"
echo "Cleaned old files."
echo ""

# ── 1. Node Sweep ─────────────────────────────────────────────────────────────
echo "=== 1. Node Sweep ==="
for W in 5 10 15 20 25; do
    M=$W; F=$W
    echo "→ wired=$W mobile=$M flows=$F"
    ./ns3 run "$SCRIPT \
        --wired_nodes=$W --mobile_nodes=$M --flows=$F \
        --pps=100 --speed=10 --coverage=1 --time=20 \
        --out=$HYBRID_DIR/metrics_hybrid.csv \
        --rtt=$HYBRID_DIR/rtt_hybrid.csv \
        --pernode=$HYBRID_DIR/per_node_hybrid.csv" 2>/dev/null
done

# ── 2. Flow Sweep ─────────────────────────────────────────────────────────────
echo ""
echo "=== 2. Flow Sweep (wired=10, mobile=10) ==="
for F in 5 10 15 20 25; do
    echo "→ flows=$F"
    ./ns3 run "$SCRIPT \
        --wired_nodes=10 --mobile_nodes=10 --flows=$F \
        --pps=100 --speed=10 --coverage=1 --time=20 \
        --out=$HYBRID_DIR/metrics_hybrid.csv \
        --rtt=$HYBRID_DIR/rtt_hybrid.csv \
        --pernode=$HYBRID_DIR/per_node_hybrid.csv" 2>/dev/null
done

# ── 3. PPS Sweep ──────────────────────────────────────────────────────────────
echo ""
echo "=== 3. PPS Sweep ==="
for P in 100 200 300 400 500; do
    echo "→ pps=$P"
    ./ns3 run "$SCRIPT \
        --wired_nodes=10 --mobile_nodes=10 --flows=10 \
        --pps=$P --speed=10 --coverage=1 --time=20 \
        --out=$HYBRID_DIR/metrics_hybrid.csv \
        --rtt=$HYBRID_DIR/rtt_hybrid.csv \
        --pernode=$HYBRID_DIR/per_node_hybrid.csv" 2>/dev/null
done

# ── 4. Speed Sweep ────────────────────────────────────────────────────────────
echo ""
echo "=== 4. Speed Sweep ==="
for S in 5 10 15 20 25; do
    echo "→ speed=$S m/s"
    ./ns3 run "$SCRIPT \
        --wired_nodes=10 --mobile_nodes=10 --flows=10 \
        --pps=100 --speed=$S --coverage=1 --time=20 \
        --out=$HYBRID_DIR/metrics_hybrid.csv \
        --rtt=$HYBRID_DIR/rtt_hybrid.csv \
        --pernode=$HYBRID_DIR/per_node_hybrid.csv" 2>/dev/null
done

# ── 5. Coverage Sweep ─────────────────────────────────────────────────────────
echo ""
echo "=== 5. Coverage Sweep ==="
for C in 1 2 3 4 5; do
    echo "→ coverage=${C}x"
    ./ns3 run "$SCRIPT \
        --wired_nodes=10 --mobile_nodes=10 --flows=10 \
        --pps=100 --speed=10 --coverage=$C --time=20 \
        --out=$HYBRID_DIR/metrics_hybrid.csv \
        --rtt=$HYBRID_DIR/rtt_hybrid.csv \
        --pernode=$HYBRID_DIR/per_node_hybrid.csv" 2>/dev/null
done

# ── Plot ──────────────────────────────────────────────────────────────────────
echo ""
echo "=== Plotting... ==="
python3 "$PLOT_SCRIPT" \
    --metrics "$HYBRID_DIR/metrics_hybrid.csv" \
    --rtt     "$HYBRID_DIR/rtt_hybrid.csv" \
    --pernode "$HYBRID_DIR/per_node_hybrid.csv" \
    --out     "$HYBRID_DIR"

echo ""
echo "=================================================="
echo " Hybrid sweep complete! Results in: $HYBRID_DIR"
echo "=================================================="
