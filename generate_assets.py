"""Generate kawaii-style decorative assets for PDF reports."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch, Arc, Wedge, Ellipse
from matplotlib.collections import PatchCollection
import os

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(ASSETS, exist_ok=True)

# Kawaii color palette
PINK = "#FFB6C1"
PINK_DARK = "#FF69B4"
LAVENDER = "#E6E6FA"
MINT = "#98FB98"
PEACH = "#FFDAB9"
CREAM = "#FFFDD0"
SKY = "#87CEEB"
LEMON = "#F0E68C"
SALMON = "#FFA07A"
LILAC = "#DDA0DD"
SAKURA = "#F8BBD0"
MATCHA = "#C8E6C9"


def save(fig, name):
    path = os.path.join(ASSETS, name)
    fig.savefig(path, transparent=True, bbox_inches='tight', pad_inches=0.1, dpi=150)
    plt.close(fig)
    print(f"  OK: {name}")


# ==================== Kawaii Backgrounds ====================

def make_bg(filename, base_color, dot_color, accent_color):
    """Soft gradient background with cute polka dots."""
    fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
    ax.set_xlim(0, 8); ax.set_ylim(0, 8); ax.axis('off')

    # Gradient overlay
    gradient = np.linspace(0, 1, 100).reshape(1, -1)
    gradient = np.vstack([gradient] * 100)
    ax.imshow(gradient, extent=[0, 8, 0, 8], aspect='auto',
              cmap=matplotlib.colors.LinearSegmentedColormap.from_list(
                  '', [base_color, '#FFFFFF']), alpha=0.3)

    # Polka dots
    np.random.seed(42)
    for _ in range(120):
        x, y = np.random.uniform(0.2, 7.8), np.random.uniform(0.2, 7.8)
        size = np.random.uniform(15, 50)
        alpha = np.random.uniform(0.08, 0.2)
        ax.scatter(x, y, s=size, c=dot_color, alpha=alpha, edgecolors='none')

    # Small stars scattered
    for _ in range(20):
        x, y = np.random.uniform(0.5, 7.5), np.random.uniform(0.5, 7.5)
        ax.scatter(x, y, s=np.random.uniform(8, 20), c=accent_color,
                   alpha=np.random.uniform(0.15, 0.3), marker='*', edgecolors='none')

    ax.set_facecolor(base_color)
    fig.patch.set_facecolor('none')
    save(fig, filename)


if __name__ == "__main__":
    print("Generating kawaii backgrounds...")
    make_bg('bg_kawaii_pink.png', '#FFF0F5', PINK, PINK_DARK)
    make_bg('bg_kawaii_lavender.png', '#F5F0FF', LAVENDER, '#9370DB')
    make_bg('bg_kawaii_mint.png', '#F0FFF0', MINT, '#3CB371')


    # ==================== Kawaii Divider ====================

    print("Generating kawaii divider...")
    fig, ax = plt.subplots(figsize=(6, 0.8), dpi=150)
    ax.set_xlim(0, 6); ax.set_ylim(0, 0.8); ax.axis('off')

    # Dashed line
    ax.plot([0.3, 5.7], [0.4, 0.4], color=PINK, linewidth=1.5,
            linestyle='--', dashes=(4, 3), alpha=0.6)

    # Small flowers and stars along the line
    decorations = [
        (0.5, '✿', SAKURA), (1.5, '✦', LEMON), (2.5, '❀', PINK),
        (3.0, '✿', LAVENDER), (3.5, '❀', MINT), (4.5, '✦', PEACH),
        (5.5, '✿', SAKURA),
    ]
    for x, char, color in decorations:
        ax.text(x, 0.4, char, ha='center', va='center', fontsize=11, color=color)

    ax.set_facecolor('none'); fig.patch.set_facecolor('none')
    save(fig, 'kawaii_divider.png')


    # ==================== Kawaii Corner Decoration ====================

    print("Generating kawaii corner decoration...")
    fig, ax = plt.subplots(figsize=(2, 2), dpi=150)
    ax.set_xlim(0, 2); ax.set_ylim(0, 2); ax.axis('off')

    # Vine-like curve
    t = np.linspace(0, np.pi/2, 50)
    x_vine = 0.1 + 0.8 * np.sin(t)
    y_vine = 0.1 + 0.8 * np.cos(t)
    ax.plot(x_vine, y_vine, color=MINT, linewidth=2, alpha=0.7)

    # Small leaves
    for i in range(5):
        angle = i * np.pi / 10
        lx = 0.1 + 0.5 * np.sin(angle)
        ly = 0.1 + 0.5 * np.cos(angle)
        ax.scatter(lx, ly, s=30, c=MINT, alpha=0.5, marker='o')

    # Small flowers at corner
    ax.text(0.15, 0.15, '✿', ha='center', va='center', fontsize=16, color=SAKURA)
    ax.text(0.5, 0.5, '❀', ha='center', va='center', fontsize=10, color=PINK, alpha=0.6)

    ax.set_facecolor('none'); fig.patch.set_facecolor('none')
    save(fig, 'kawaii_corner.png')


    # ==================== Kawaii Frame ====================

    print("Generating kawaii frame...")
    fig, ax = plt.subplots(figsize=(4, 4), dpi=150)
    ax.set_xlim(0, 4); ax.set_ylim(0, 4); ax.axis('off')

    # Rounded rectangle border
    border = FancyBboxPatch((0.15, 0.15), 3.7, 3.7,
                             boxstyle='round,pad=0.2',
                             facecolor='none', edgecolor=PINK,
                             linewidth=2.5, linestyle='-', alpha=0.6)
    ax.add_patch(border)

    # Corner decorations
    for cx, cy in [(0.4, 0.4), (3.6, 0.4), (0.4, 3.6), (3.6, 3.6)]:
        ax.scatter(cx, cy, s=40, c=SAKURA, alpha=0.7, marker='*')

    # Small dots along edges
    for i in np.linspace(0.6, 3.4, 8):
        ax.scatter(i, 0.2, s=10, c=PINK, alpha=0.3)
        ax.scatter(i, 3.8, s=10, c=PINK, alpha=0.3)
        ax.scatter(0.2, i, s=10, c=PINK, alpha=0.3)
        ax.scatter(3.8, i, s=10, c=PINK, alpha=0.3)

    ax.set_facecolor('none'); fig.patch.set_facecolor('none')
    save(fig, 'kawaii_frame.png')


    # ==================== Kawaii Stars Cluster ====================

    print("Generating kawaii stars cluster...")
    fig, ax = plt.subplots(figsize=(3, 1), dpi=150)
    ax.set_xlim(0, 3); ax.set_ylim(0, 1); ax.axis('off')

    colors = [SAKURA, LEMON, LAVENDER, MINT, PEACH, PINK]
    for i in range(8):
        x = 0.2 + i * 0.35
        y = 0.3 + np.random.uniform(-0.15, 0.15)
        size = np.random.uniform(40, 100)
        c = np.random.choice(colors)
        marker = np.random.choice(['*', '✦', '•'])
        if marker == '✦':
            ax.text(x, y, '✦', ha='center', va='center',
                    fontsize=int(np.random.uniform(8, 16)), color=c)
        else:
            ax.scatter(x, y, s=size, c=c, alpha=0.7, marker='*', edgecolors='none')

    ax.set_facecolor('none'); fig.patch.set_facecolor('none')
    save(fig, 'kawaii_stars.png')


    # ==================== Kawaii Hearts Row ====================

    print("Generating kawaii hearts row...")
    fig, ax = plt.subplots(figsize=(4, 0.6), dpi=150)
    ax.set_xlim(0, 4); ax.set_ylim(0, 0.6); ax.axis('off')

    heart_colors = [SAKURA, PINK, PINK_DARK, SALMON, '#FF8A80']
    for i, x in enumerate(np.linspace(0.3, 3.7, 10)):
        y = 0.3 + np.sin(i * 0.8) * 0.08
        c = heart_colors[i % len(heart_colors)]
        ax.text(x, y, '♥', ha='center', va='center',
                fontsize=np.random.randint(8, 16), color=c, alpha=0.7)

    ax.set_facecolor('none'); fig.patch.set_facecolor('none')
    save(fig, 'kawaii_hearts.png')


    # ==================== Kawaii Cloud ====================

    print("Generating kawaii cloud...")
    fig, ax = plt.subplots(figsize=(3, 1.5), dpi=150)
    ax.set_xlim(0, 3); ax.set_ylim(0, 1.5); ax.axis('off')

    # Cloud shape from overlapping circles
    cloud_circles = [
        (0.8, 0.7, 0.45), (1.3, 0.85, 0.5), (1.8, 0.8, 0.45),
        (1.1, 0.55, 0.35), (1.6, 0.55, 0.35), (1.35, 0.5, 0.3),
    ]
    for cx, cy, r in cloud_circles:
        ax.add_patch(Circle((cx, cy), r, facecolor='white', edgecolor='#E0E0E0',
                             linewidth=1, alpha=0.9))

    # Kawaii face on cloud
    ax.text(1.3, 0.65, '‿‿', ha='center', va='center', fontsize=8, color='#888')
    ax.scatter([1.15, 1.45], [0.8, 0.8], s=12, c='#888', alpha=0.6)

    ax.set_facecolor('none'); fig.patch.set_facecolor('none')
    save(fig, 'kawaii_cloud.png')


    # ==================== Kawaii Flower ====================

    print("Generating kawaii flower...")
    fig, ax = plt.subplots(figsize=(1.5, 1.5), dpi=150)
    ax.set_xlim(0, 1.5); ax.set_ylim(0, 1.5); ax.axis('off')

    # Petals
    petal_colors = [SAKURA, PINK, '#FFCDD2', '#F8BBD0']
    for i in range(6):
        angle = i * np.pi / 3
        px = 0.75 + 0.3 * np.cos(angle)
        py = 0.75 + 0.3 * np.sin(angle)
        ax.add_patch(Circle((px, py), 0.22, facecolor=petal_colors[i % 4],
                             edgecolor='white', linewidth=1.5, alpha=0.85))

    # Center
    ax.add_patch(Circle((0.75, 0.75), 0.15, facecolor=LEMON,
                         edgecolor='white', linewidth=1.5))

    ax.set_facecolor('none'); fig.patch.set_facecolor('none')
    save(fig, 'kawaii_flower.png')


    # ==================== Kawaii Ribbon/Bow ====================

    print("Generating kawaii ribbon...")
    fig, ax = plt.subplots(figsize=(2, 1.5), dpi=150)
    ax.set_xlim(0, 2); ax.set_ylim(0, 1.5); ax.axis('off')

    # Bow loops
    ax.add_patch(Wedge((0.7, 0.75), 0.45, 30, 150, facecolor=PINK_DARK,
                        edgecolor='white', linewidth=1.5, alpha=0.9))
    ax.add_patch(Wedge((1.3, 0.75), 0.45, 210, 330, facecolor=PINK_DARK,
                        edgecolor='white', linewidth=1.5, alpha=0.9))
    # Center knot
    ax.add_patch(Circle((1.0, 0.75), 0.12, facecolor='#E91E63',
                         edgecolor='white', linewidth=1.5))
    # Tails
    ax.fill([0.85, 1.0, 1.15], [0.63, 0.3, 0.63], color=PINK_DARK,
            edgecolor='white', linewidth=1, alpha=0.8)

    ax.set_facecolor('none'); fig.patch.set_facecolor('none')
    save(fig, 'kawaii_ribbon.png')


    # ==================== Kawaii Piggy Bank ====================

    print("Generating kawaii piggy...")
    fig, ax = plt.subplots(figsize=(2, 2), dpi=150)
    ax.set_xlim(0, 2); ax.set_ylim(0, 2); ax.axis('off')

    # Body
    ax.add_patch(Ellipse((1.0, 0.9), 1.4, 1.0, facecolor='#FFCDD2',
                 edgecolor='#E91E63', linewidth=2))
    # Ears
    ax.add_patch(Ellipse((0.55, 1.4), 0.25, 0.3, facecolor='#FFCDD2',
                 edgecolor='#E91E63', linewidth=1.5, angle=20))
    ax.add_patch(Ellipse((1.45, 1.4), 0.25, 0.3, facecolor='#FFCDD2',
                 edgecolor='#E91E63', linewidth=1.5, angle=-20))
    # Snout
    ax.add_patch(Ellipse((1.0, 0.7), 0.4, 0.28, facecolor='#EF9A9A',
                 edgecolor='#E91E63', linewidth=1.5))
    # Nostrils
    ax.scatter([0.9, 1.1], [0.7, 0.7], s=10, c='#E91E63', alpha=0.7)
    # Eyes
    ax.scatter([0.8, 1.2], [1.1, 1.1], s=15, c='#333', alpha=0.8)
    # Coin slot
    ax.plot([0.85, 1.15], [1.45, 1.45], color='#E91E63', linewidth=2, alpha=0.6)
    # Legs
    for lx in [0.55, 0.75, 1.25, 1.45]:
        ax.add_patch(FancyBboxPatch((lx-0.06, 0.3), 0.12, 0.2,
                     boxstyle='round,pad=0.03', facecolor='#FFCDD2',
                     edgecolor='#E91E63', linewidth=1))

    ax.set_facecolor('none'); fig.patch.set_facecolor('none')
    save(fig, 'kawaii_piggy.png')


    # ==================== Kawaii Coin Stack ====================

    print("Generating kawaii coins...")
    fig, ax = plt.subplots(figsize=(1.5, 1.5), dpi=150)
    ax.set_xlim(0, 1.5); ax.set_ylim(0, 1.5); ax.axis('off')

    for i, y in enumerate([0.2, 0.45, 0.7, 0.95]):
        color = LEMON if i % 2 == 0 else '#FFD54F'
        ax.add_patch(Ellipse((0.75, y), 0.9, 0.25, facecolor=color,
                     edgecolor='#F57F17', linewidth=1.5, alpha=0.9))
        ax.text(0.75, y, '¥', ha='center', va='center', fontsize=12,
                fontweight='bold', color='#E65100', alpha=0.7)

    ax.set_facecolor('none'); fig.patch.set_facecolor('none')
    save(fig, 'kawaii_coins.png')


    # ==================== Kawaii Trophy ====================

    print("Generating kawaii trophy...")
    fig, ax = plt.subplots(figsize=(1.5, 2), dpi=150)
    ax.set_xlim(0, 1.5); ax.set_ylim(0, 2); ax.axis('off')

    # Cup body
    ax.fill([0.3, 1.2, 1.1, 0.4], [0.6, 0.6, 1.4, 1.4], color=LEMON,
            edgecolor='#F57F17', linewidth=2)
    # Handles
    ax.add_patch(Arc((0.3, 1.0), 0.3, 0.5, angle=0, theta1=270, theta2=90,
                 color='#F57F17', linewidth=2))
    ax.add_patch(Arc((1.2, 1.0), 0.3, 0.5, angle=0, theta1=90, theta2=270,
                 color='#F57F17', linewidth=2))
    # Stem
    ax.fill([0.6, 0.9, 0.85, 0.65], [0.35, 0.35, 0.6, 0.6], color='#F57F17')
    # Base
    ax.add_patch(FancyBboxPatch((0.35, 0.15), 0.8, 0.2,
                 boxstyle='round,pad=0.05', facecolor=LEMON,
                 edgecolor='#F57F17', linewidth=2))
    # Star on trophy
    ax.text(0.75, 1.0, '★', ha='center', va='center', fontsize=20, color='#E65100')

    ax.set_facecolor('none'); fig.patch.set_facecolor('none')
    save(fig, 'kawaii_trophy.png')


    # ==================== Kawaii Wallet ====================

    print("Generating kawaii wallet...")
    fig, ax = plt.subplots(figsize=(2, 1.5), dpi=150)
    ax.set_xlim(0, 2); ax.set_ylim(0, 1.5); ax.axis('off')

    # Wallet body
    ax.add_patch(FancyBboxPatch((0.2, 0.3), 1.6, 1.0,
                 boxstyle='round,pad=0.1', facecolor=LAVENDER,
                 edgecolor='#9370DB', linewidth=2))
    # Flap
    ax.add_patch(FancyBboxPatch((0.2, 0.9), 1.6, 0.4,
                 boxstyle='round,pad=0.08', facecolor='#D1C4E9',
                 edgecolor='#9370DB', linewidth=1.5))
    # Clasp
    ax.add_patch(Circle((1.0, 0.95), 0.08, facecolor=LEMON,
                 edgecolor='#F57F17', linewidth=1.5))
    # Card peeking out
    ax.fill([0.4, 0.9, 0.9, 0.4], [0.65, 0.65, 0.85, 0.85],
            color='white', edgecolor='#BDBDBD', linewidth=1)

    ax.set_facecolor('none'); fig.patch.set_facecolor('none')
    save(fig, 'kawaii_wallet.png')


    # ==================== ====================

    print(f"\nDone! {len(os.listdir(ASSETS))} assets in assets/")
