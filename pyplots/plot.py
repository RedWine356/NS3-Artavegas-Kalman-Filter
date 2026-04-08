import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('mobile_rtt.csv')

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# RTT over Time
axes[0,0].plot(df['Timestamp'], df['RTT_ms'], 'b-', alpha=0.7, linewidth=0.5)
axes[0,0].set_xlabel('Time (s)')
axes[0,0].set_ylabel('RTT (ms)')
axes[0,0].set_title('RTT over Time')
axes[0,0].grid(True, alpha=0.3)

# RTT vs Distance
axes[0,1].scatter(df['Distance'], df['RTT_ms'], alpha=0.3, s=2, c='red')
axes[0,1].set_xlabel('Distance (m)')
axes[0,1].set_ylabel('RTT (ms)')
axes[0,1].set_title('RTT vs Distance')
axes[0,1].grid(True, alpha=0.3)

# RTT Distribution
axes[1,0].hist(df['RTT_ms'], bins=50, edgecolor='black', alpha=0.7)
axes[1,0].set_xlabel('RTT (ms)')
axes[1,0].set_ylabel('Frequency')
axes[1,0].set_title('RTT Distribution (Long tail = Jitter)')
axes[1,0].grid(True, alpha=0.3)

# Rolling average to show trend
df['RTT_rolling'] = df['RTT_ms'].rolling(window=50).mean()
axes[1,1].plot(df['Distance'], df['RTT_ms'], 'b.', alpha=0.1, markersize=1, label='Raw RTT')
axes[1,1].plot(df['Distance'], df['RTT_rolling'], 'r-', linewidth=2, label='Moving Avg')
axes[1,1].set_xlabel('Distance (m)')
axes[1,1].set_ylabel('RTT (ms)')
axes[1,1].set_title('RTT Trend with Jitter')
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('rtt_analysis.png', dpi=150)
plt.show()

print(f"RTT Statistics:")
print(f"  Mean: {df['RTT_ms'].mean():.2f} ms")
print(f"  Std:  {df['RTT_ms'].std():.2f} ms")
print(f"  Min:  {df['RTT_ms'].min():.2f} ms")
print(f"  Max:  {df['RTT_ms'].max():.2f} ms")