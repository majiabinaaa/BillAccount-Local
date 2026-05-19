"""Generate cute decorative assets for PDF reports."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch
import os

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(ASSETS, exist_ok=True)


def save(fig, name):
    path = os.path.join(ASSETS, name)
    fig.savefig(path, transparent=True, bbox_inches='tight', pad_inches=0.1, dpi=150)
    plt.close(fig)
    print(f"  {name}")


# 1. Money bag
fig, ax = plt.subplots(figsize=(1.5, 1.5), dpi=150)
ax.set_xlim(0, 1.5); ax.set_ylim(0, 1.5); ax.axis('off')
bag = FancyBboxPatch((0.3, 0.2), 0.9, 0.9, boxstyle='round,pad=0.1',
                     facecolor='#8D6E63', edgecolor='#5D4037', linewidth=3)
ax.add_patch(bag)
ax.plot([0.75, 0.75], [1.15, 1.4], color='#5D4037', linewidth=3)
ax.text(0.75, 0.6, '$', ha='center', va='center', fontsize=40, fontweight='bold', color='#FFD54F')
ax.set_facecolor('none'); fig.patch.set_facecolor('none')
save(fig, 'money_bag.png')

# 2. Chart up
fig, ax = plt.subplots(figsize=(1.5, 1.5), dpi=150)
ax.set_xlim(0, 1.5); ax.set_ylim(0, 1.5); ax.axis('off')
ax.fill_between([0.2, 0.5, 0.8, 1.3], [0.2, 0.6, 0.5, 1.1], 0.2, color='#66BB6A', alpha=0.3)
ax.plot([0.2, 0.5, 0.8, 1.3], [0.2, 0.6, 0.5, 1.1], color='#43A047', linewidth=4, solid_capstyle='round')
ax.scatter([0.2, 0.5, 0.8, 1.3], [0.2, 0.6, 0.5, 1.1], s=100, color='#2E7D32', zorder=5)
ax.set_facecolor('none'); fig.patch.set_facecolor('none')
save(fig, 'chart_up.png')

# 3. Crown
fig, ax = plt.subplots(figsize=(1.5, 1.2), dpi=150)
ax.set_xlim(0, 1.5); ax.set_ylim(0, 1.2); ax.axis('off')
ax.fill([0.1, 1.4, 1.3, 0.2], [0.1, 0.1, 0.3, 0.3], color='#FFB300', edgecolor='#E65100', linewidth=2)
for cx, h in [(0.3, 0.8), (0.75, 1.1), (1.2, 0.8)]:
    ax.fill([cx-0.2, cx, cx+0.2], [0.3, h, 0.3], color='#FFD54F', edgecolor='#E65100', linewidth=2)
for gx in [0.3, 0.75, 1.2]:
    ax.scatter(gx, 0.55, s=80, color='#E53935', edgecolors='#B71C1C', linewidths=1, zorder=10)
ax.set_facecolor('none'); fig.patch.set_facecolor('none')
save(fig, 'crown.png')

# 4. Rocket
fig, ax = plt.subplots(figsize=(1, 1.5), dpi=150)
ax.set_xlim(0, 1); ax.set_ylim(0, 1.5); ax.axis('off')
ax.fill([0.2, 0.5, 0.8], [0.2, 1.2, 0.2], color='#42A5F5', edgecolor='#1565C0', linewidth=2.5)
ax.fill([0.3, 0.5, 0.7], [0.2, 0.4, 0.2], color='#E53935', edgecolor='#B71C1C', linewidth=2)
ax.add_patch(Circle((0.5, 0.7), 0.1, facecolor='white', edgecolor='#1565C0', linewidth=2))
ax.fill([0.3, 0.5, 0.7], [0.2, 0.0, 0.2], color='#FF7043', alpha=0.8)
ax.set_facecolor('none'); fig.patch.set_facecolor('none')
save(fig, 'rocket.png')

# 5. Sparkles
fig, ax = plt.subplots(figsize=(3, 0.6), dpi=150)
ax.set_xlim(0, 3); ax.set_ylim(0, 0.6); ax.axis('off')
cs = ['#FF6B6B', '#4ECDC4', '#FFE66D', '#FF8E72', '#A8E6CF']
for i in range(25):
    ax.scatter(np.random.uniform(0.1, 2.9), np.random.uniform(0.1, 0.5),
               s=np.random.uniform(30, 100), c=np.random.choice(cs),
               marker=np.random.choice(['*', 'o', 'D', '^', 's']), alpha=0.7)
ax.set_facecolor('none'); fig.patch.set_facecolor('none')
save(fig, 'sparkles.png')

# 6. Medal
fig, ax = plt.subplots(figsize=(1, 1.3), dpi=150)
ax.set_xlim(0, 1); ax.set_ylim(0, 1.3); ax.axis('off')
ax.add_patch(Circle((0.5, 0.6), 0.35, facecolor='#FFD54F', edgecolor='#F57F17', linewidth=3))
ax.text(0.5, 0.55, '1', ha='center', va='center', fontsize=36, fontweight='bold', color='#E65100')
ax.fill([0.35, 0.5, 0.65], [0.95, 1.2, 0.95], color='#E53935', edgecolor='#B71C1C', linewidth=2)
ax.set_facecolor('none'); fig.patch.set_facecolor('none')
save(fig, 'medal.png')

# 7. Party burst
fig, ax = plt.subplots(figsize=(2, 2), dpi=150)
ax.set_xlim(0, 2); ax.set_ylim(0, 2); ax.axis('off')
cs2 = ['#E91E63', '#FF9800', '#FFEB3B', '#4CAF50', '#2196F3', '#9C27B0']
for i in range(40):
    a = np.random.uniform(0, 2*np.pi)
    d = np.random.uniform(0.2, 0.85)
    ax.scatter(1+d*np.cos(a), 1+d*np.sin(a), s=np.random.uniform(20, 80),
               c=np.random.choice(cs2), alpha=0.8,
               marker=np.random.choice(['o', '*', 'D', '^', 's', 'P']))
ax.scatter(1, 1, s=200, color='#FFD54F', edgecolors='#FF8F00', linewidths=2)
ax.set_facecolor('none'); fig.patch.set_facecolor('none')
save(fig, 'party.png')

# 8. Fire
fig, ax = plt.subplots(figsize=(1, 1.3), dpi=150)
ax.set_xlim(0, 1); ax.set_ylim(0, 1.3); ax.axis('off')
t = np.linspace(0, np.pi, 50)
fx = 0.5 + 0.25 * np.sin(t)
fy = 0.1 + 0.6 * (1 - np.abs(np.cos(t)))
ax.fill(fx, fy, color='#FF5722', alpha=0.9)
ax.fill([0.35, 0.5, 0.65], [0.2, 0.05, 0.2], color='#FF9800', alpha=0.8)
ax.fill([0.4, 0.5, 0.6], [0.7, 1.1, 0.7], color='#FFEB3B', alpha=0.6)
ax.set_facecolor('none'); fig.patch.set_facecolor('none')
save(fig, 'fire.png')

# 9. Background patterns
for color, name in [('#FFF3E0', 'bg_warm.png'), ('#E8F5E9', 'bg_green.png'),
                     ('#E3F2FD', 'bg_blue.png')]:
    fig, ax = plt.subplots(figsize=(6, 6), dpi=80)
    ax.set_xlim(0, 6); ax.set_ylim(0, 6); ax.axis('off')
    for _ in range(200):
        ax.scatter(np.random.uniform(0, 6), np.random.uniform(0, 6),
                   s=np.random.uniform(2, 12), color='#FFFFFF',
                   alpha=np.random.uniform(0.05, 0.25))
    ax.set_facecolor(color); fig.patch.set_facecolor('none')
    save(fig, name)

print(f"\nDone! {len(os.listdir(ASSETS))} assets in assets/")
