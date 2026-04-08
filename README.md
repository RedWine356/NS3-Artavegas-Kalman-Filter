# TCP Vegas + Adaptive Kalman Filter — NS-3 Simulation

**BUET CSE — Network Simulation Project**

## Project Overview
NS-3 simulation of TCP Vegas in 6G-like mobile wireless scenarios.
Implements a novel adaptive Kalman filter for RTT smoothing that
reduces peak RTT spikes by 79.4% and variance by 68.3%.

## Files

| File | Description |
|---|---|
| `artaVegas_Kalman.cc` | Single vehicle, fixed Kalman R=2.68 |
| `artaVegas_AdaptiveKalman.cc` | Fixed vs Adaptive Kalman comparison |
| `mob.cc` | Multi-node wireless parameter sweep |
| `hybrid.cc` | Hybrid wired+wireless topology (bonus) |
| `run_sweep_wireless.sh` | Automates wireless parameter sweep |
| `run_sweep_hybrid.sh` | Automates hybrid parameter sweep |
| `plotMetrics.py` | Plots wireless sweep results |
| `plot_hybrid.py` | Plots hybrid sweep results |
| `plot_adaptive_kalman.py` | Fixed vs Adaptive Kalman comparison plots |

## How to Run

```bash
# Copy .cc files to scratch folder
cp *.cc ~/Downloads/ns3/ns-3-dev/scratch/

# Single vehicle Kalman
cd ~/Downloads/ns3/ns-3-dev
./ns3 run "scratch/artaVegas_AdaptiveKalman --speed=33.33 --time=90"

# Multi-node wireless sweep
bash run_sweep_wireless.sh

# Hybrid sweep
bash run_sweep_hybrid.sh
```

## Key Results
- Peak RTT reduction: 32ms → 6.6ms (79.4%)
- Variance reduction: 68.3% (fixed), higher with adaptive
- Max hybrid throughput: 52.9 Mbps at 500 pps
- 80-node saturation anomaly: throughput collapses to 3.1 Mbps

## Requirements
- NS-3 (version 3.41+)
- Python 3 with pandas, matplotlib, numpy
