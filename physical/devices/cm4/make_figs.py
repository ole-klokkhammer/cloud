#!/usr/bin/env python3
"""Figures for drafts/edge-node/README.md - OBO T160 passive thermal build.
Run:  python drafts/edge-node/figs/make_figs.py
External 190x150x77, clear internal 176x135x67 (OBO datablad, art. 2007541).
Temperatures are conduction estimates from the README model, not measurements."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, FancyBboxPatch

OUT = os.path.dirname(os.path.abspath(__file__))
WALL, PCB, MET, PAD, MOD, SOC = "#cfcfcf", "#3b7d3f", "#aeb9c1", "#ef8354", "#5b7c99", "#2f4f68"
RED, GRN, DIM = "#c0392b", "#27703a", "#444444"
plt.rcParams.update({"font.size": 8, "font.family": "DejaVu Sans",
                     "savefig.dpi": 200, "savefig.facecolor": "white", "axes.linewidth": 0})

def box(ax, x, y, w, h, fc, ec="#555555", lw=0.7, z=2):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, zorder=z))

def lab(ax, x, y, s, size=7.5, color="#222222", ha="left", va="center", weight="normal"):
    ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va, weight=weight, zorder=9,
            bbox=dict(fc="white", ec="none", alpha=0.88, pad=1.2))

def arrow(ax, x, y0, y1, s, side=1.5, ha="left"):
    ax.add_patch(FancyArrowPatch((x, y0), (x, y1), arrowstyle="<|-|>", mutation_scale=7,
                                 lw=0.7, color=DIM, zorder=9))
    if s:
        lab(ax, x + side, (y0 + y1) / 2, s, 7, DIM, ha=ha)

def harrow(ax, y, x0, x1, s, dy=3.5):
    ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle="<|-|>", mutation_scale=7,
                                 lw=0.7, color=DIM, zorder=9))
    if s:
        lab(ax, (x0 + x1) / 2, y + dy, s, 6.8, DIM, ha="center")

def shell(ax):
    """T160 section: 3 mm walls, 67 mm clear internal, lid with overlapping flange and gasket."""
    box(ax, 0, 0, 190, 3, WALL)
    box(ax, 0, 0, 3, 67, WALL); box(ax, 187, 0, 3, 67, WALL)
    box(ax, -4, 67, 198, 3, WALL)
    box(ax, -4, 58, 7, 12, WALL); box(ax, 187, 58, 7, 12, WALL)
    box(ax, -1, 65.4, 5, 1.7, "#333333"); box(ax, 186, 65.4, 5, 1.7, "#333333")
    ax.plot([7, 183], [67, 67], color="#555555", lw=0.7, ls=":")
    lab(ax, -13, 71.5, "lid, quick fastener\n+ IP66 gasket", 7, ha="left")


# ------------------------------------------------------------------ fig 1
def fig1():
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.6), sharey=True)
    for ax, kind in zip(axes, ("naive", "bridged")):
        ax.set_xlim(-18, 278); ax.set_ylim(-9, 80); ax.set_aspect("equal"); ax.axis("off")
        shell(ax)
        if kind == "naive":
            box(ax, 15, 3, 6, 6, "#8d8d8d"); box(ax, 169, 3, 6, 6, "#8d8d8d")
            box(ax, 15, 9, 160, 1.6, PCB)
            box(ax, 72, 10.6, 46, 5, MOD); box(ax, 86, 10.6, 18, 5, SOC)
            box(ax, 65, 15.6, 60, 6, MET)
            ax.add_patch(Circle((110, 42), 25, fc="#ffe3dd", ec="none", zorder=1))
            lab(ax, 110, 51, "trapped air", 8.5, RED, ha="center", weight="bold")
            lab(ax, 110, 40, "~25 K/W die to wall\n+100 K at 4 W\nthrottles", 7.4, RED, ha="center")
            lab(ax, 63, 18.6, "flat 6 mm heatsink", 7, ha="right")
            lab(ax, 132, 6, "6 mm standoffs", 7)
            arrow(ax, 25, 3, 67, "67 mm clear\ninternal", side=3)
            ax.set_title("NOT this: the heatsink warms the box air, not the box",
                         fontsize=9, color=RED, pad=3)
        else:
            box(ax, 15, 3, 6, 12, "#8d8d8d"); box(ax, 169, 3, 6, 12, "#8d8d8d")
            box(ax, 15, 15, 160, 1.6, PCB)
            box(ax, 72, 16.6, 46, 5, MOD); box(ax, 86, 16.6, 18, 5, SOC)
            box(ax, 65, 21.6, 60, 40, MET)
            for fx in range(69, 122, 6):
                ax.plot([fx, fx], [23, 56.5], color="#7f8c93", lw=0.5, zorder=3)
            box(ax, 65, 56.5, 60, 5, "#9aa7ae")
            box(ax, 55, 61.5, 80, 2.6, PAD)
            box(ax, 45, 64.1, 100, 2, "#7f8c93")
            specs = [(65.1, "Al spreader 100 x 90 x 2 mm", "spreads the point contact"),
                     (62.8, "silicone pad 4 mm, squashed to 2.5", "0.2 K/W"),
                     (59.0, "heatsink top plate, solid", ""),
                     (40.0, "passive heatsink ~40 mm, fins vertical", ""),
                     (19.0, "CM4 module + shield", ""),
                     (15.8, "PCB on 12 mm M3 standoffs", ""),
                     (1.5, "3 mm PP/GF wall", "1.4 K/W across the spreader")]
            for y, s, extra in specs:
                ax.plot([193, 200], [max(y, 1), max(y, 1)], color="#999", lw=0.6, zorder=8)
                lab(ax, 202, y, s + ("\n" + extra if extra else ""), 7,
                    GRN if "K/W" in extra else "#222222")
            ax.annotate("", xy=(63, 59), xytext=(38, 34),
                        arrowprops=dict(arrowstyle="->", color=GRN, lw=1.4))
            lab(ax, 36, 30, "heat path 2-3 K/W", 7.8, GRN, ha="center", weight="bold")
            arrow(ax, 145, 3, 67, "67 mm clear\ninternal", side=3)
            lab(ax, 95, -6.0, "12 + 1.6 + 5 + 40 + 2.6 + 2 = 63.2 mm, so the pad takes up the last few mm",
                7.2, DIM, ha="center")
            ax.set_title("THIS: the stack reaches the lid, so heat leaves through the plastic",
                         fontsize=9, color=GRN, pad=3)
    fig.suptitle("Section through the OBO T160. Drawn base-down; on a wall rotate 90 degrees, the stack is identical.",
                 fontsize=8.5, color=DIM, y=1.02)
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    fig.savefig(f"{OUT}/fig1-section.png", bbox_inches="tight", facecolor="white")
    fig.savefig(f"{OUT}/fig1-section.svg", bbox_inches="tight", facecolor="white"); plt.close(fig)

# ------------------------------------------------------------------ fig 2
def fig2():
    fig, ax = plt.subplots(figsize=(9.6, 8.2))
    ax.set_xlim(-12, 205); ax.set_ylim(-58, 165); ax.set_aspect("equal"); ax.axis("off")
    box(ax, 0, 0, 190, 150, "#efefef")                                   # outer 190 x 150
    ax.add_patch(Rectangle((7, 7.5), 176, 135, fc="none", ec="#777", lw=0.8, ls="--", zorder=3))
    lab(ax, 9.5, 138, "clear internal 176 x 135", 7.2, "#555")
    box(ax, 15, 30, 160, 90, "#dfeadc", "#3b7d3f")
    lab(ax, 16, 114, "CM4 IO board ~160 x 90  (measure yours)", 7.4, "#27703a")
    harrow(ax, 122, 7, 15, "8 mm")
    harrow(ax, 40, 175, 183, "8 mm")
    ax.add_patch(FancyArrowPatch((170, 30), (170, 7.5), arrowstyle="<|-|>", mutation_scale=7,
                                 lw=0.7, color=DIM, zorder=9))
    lab(ax, 172, 19, "22 mm", 6.8, DIM)
    box(ax, 60, 63, 45.5, 24, MOD, "#33506a"); box(ax, 70, 66, 18, 18, SOC)
    lab(ax, 71, 58, "BCM2711", 6.8, ha="left")
    ax.add_patch(Rectangle((38, 30), 100, 90, fc="none", ec=GRN, lw=1.1, ls="--", zorder=6))
    lab(ax, 39, 123, "Al spreader 100 x 90 footprint, centred on the SoC", 7, GRN)
    for x, w, name in [(40, 15, "HDMI"), (112, 14, "USB"), (128, 14, "USB"), (150, 18, "RJ45")]:
        box(ax, x, 22, w, 8, "#9aa7ae"); lab(ax, x + w / 2, 18, name, 6.2, DIM, ha="center")
    box(ax, 168, 60, 7, 12, "#9aa7ae")
    lab(ax, 166, 66, "DC", 6.2, DIM, ha="right")
    for cx, r, nm in [(58, 6, "M25"), (92, 6, "M25"), (126, 8, "M32")]:
        ax.add_patch(Circle((cx, 3.5), r, fc="#bdbdbd", ec="#666", lw=0.7, zorder=4))
        lab(ax, cx, 3.5, nm, 5.8, "#333", ha="center")
    lab(ax, 8, -6, "base knockouts: use two for the USB extension and the DC lead, leave the other 10 plugs in", 7, DIM)
    ax.add_patch(FancyArrowPatch((58, -3), (58, -26), arrowstyle="-", color="#333", lw=1.6, zorder=5))
    ax.add_patch(FancyArrowPatch((92, -3), (92, -26), arrowstyle="-", color="#333", lw=1.6, zorder=5))
    ax.add_patch(FancyBboxPatch((36, -40), 40, 14, boxstyle="round,pad=1,rounding_size=2",
                                fc="#dfe6ec", ec="#33506a", lw=0.9, zorder=6))
    lab(ax, 56, -33, "Electrolama zzh", 7, "#222", ha="center")
    lab(ax, 56, -37.5, "outside the box", 6.4, "#555", ha="center")
    ax.add_patch(FancyArrowPatch((76, -33), (96, -33), arrowstyle="->,head_width=1.5,head_length=3",
                                 color=RED, lw=1.1, zorder=7))
    lab(ax, 100, -33, "zzh antenna: >=10 cm from the\nCM4 whips, away from the RJ45 lead", 6.8, RED)
    for wx in (63, 103):
        ax.plot([wx, wx], [87, 108], color=RED, lw=1.2, zorder=7)
        ax.plot([wx - 2, wx + 2], [108, 108], color=RED, lw=1.2, zorder=7)
    lab(ax, 108, 104, "U.FL whips vertical, clear of the shield,\nthe RJ45 and the DC lead", 6.8, RED)
    lab(ax, 178, 152, "long axis horizontal,\ncables enter from below", 7, DIM, ha="right")
    lab(ax, 95, -50, "the spreader presses up against the lid, out of this page; connector positions are "
                     "schematic, confirm them on your board", 6.8, "#888", ha="center")
    ax.set_title("Plan view, lid off. 8 mm per side along the board, 22 mm across.",
                 fontsize=9, color=DIM, pad=2)
    fig.tight_layout()
    fig.savefig(f"{OUT}/fig2-plan.png", bbox_inches="tight", facecolor="white")
    fig.savefig(f"{OUT}/fig2-plan.svg", bbox_inches="tight", facecolor="white"); plt.close(fig)

# ------------------------------------------------------------------ fig 3
def fig3():
    Rroom, Rair, Rbridge, P = round(1 / 0.485, 1), 25.0, 2.5, (1.5, 4.0)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.2, 4.4),
                                   gridspec_kw=dict(width_ratios=[1.15, 1]))
    ax1.set_xlim(0, 10); ax1.set_ylim(0, 10); ax1.axis("off")
    def chain(y, nodes, title, color):
        x = 0.35
        ax1.text(0.35, y + 1.55, title, fontsize=8.5, color=color, weight="bold")
        for i, (nm, rw) in enumerate(nodes):
            w = 1.5
            ax1.add_patch(Rectangle((x, y), w, 1.1, fc="#f4f4f4", ec=color, lw=0.9))
            ax1.text(x + w / 2, y + 0.72, nm, fontsize=6.8, ha="center", va="center")
            if rw is not None:
                ax1.text(x + w / 2, y + 0.26, f"{rw:g} K/W", fontsize=6.8, ha="center",
                         va="center", color=color)
            if i < len(nodes) - 1:
                ax1.add_patch(FancyArrowPatch((x + w, y + 0.55), (x + w + 0.45, y + 0.55),
                                              arrowstyle="-|>", mutation_scale=7, lw=0.9, color=color))
            x += w + 0.45
        ax1.text(x + 0.1, y + 0.55, "room", fontsize=6.8, va="center")
    chain(6.6, [("die", None), ("heatsink", None), ("box air", Rair), ("wall", Rroom)],
          "flat heatsink only", RED)
    ax1.text(0.35, 5.6, "4 W -> +108 K -> 133 C: throttles", fontsize=7.4, color=RED)
    chain(2.4, [("die", None), ("heatsink", None), ("pad", 0.2), ("spreader+plastic", 1.4), ("wall", Rroom)],
          "heatsink + pad + spreader to the lid", GRN)
    ax1.text(0.35, 1.4, "4 W -> +18 K -> 43 C", fontsize=7.4, color=GRN)
    ax1.set_title("Thermal circuit, box sitting in a 25 C room", fontsize=9, color=DIM, pad=2)

    groups, colors, series = [], ["#5b7c99", "#c8d3da"], [25, 40]
    for label, R in (("flat heatsink\nonly", Rair + Rroom), ("heatsink + pad\n+ spreader", Rbridge + Rroom)):
        for p in P:
            groups.append((f"{label}\n{p} W", [25 + p * R, 40 + p * R]))
    xs = range(len(groups))
    for i, (nm, vals) in enumerate(groups):
        for j, (v, amb) in enumerate(zip(vals, series)):
            clipped = v > 88
            ax2.bar(i + (j - 0.5) * 0.36, min(v, 88), 0.34, color=colors[j],
                    ec="#555", lw=0.5, hatch="//" if clipped else None)
            ax2.text(i + (j - 0.5) * 0.36, min(v, 88) + 1.5,
                     (">88" if clipped else f"{v:.0f}"), fontsize=6.8, ha="center")
    ax2.axhline(85, color=RED, lw=1, ls="--"); ax2.text(3.55, 86.5, "throttle ~85 C", fontsize=6.8, color=RED, ha="right")
    ax2.axhline(65, color=GRN, lw=1, ls="--"); ax2.text(3.55, 66.5, "target <65 C", fontsize=6.8, color=GRN, ha="right")
    ax2.set_xticks(list(xs)); ax2.set_xticklabels([g[0] for g in groups], fontsize=6.8)
    ax2.set_ylabel("predicted SoC temp (C)", fontsize=7.5); ax2.set_ylim(0, 100)
    ax2.tick_params(labelsize=7, length=0)
    for s in ("top", "right", "left"):
        ax2.spines[s].set_visible(False)
    ax2.set_title("Model estimate, not a measurement\nbars: 25 C room (dark), 40 C hot loft (light)",
                  fontsize=8, color=DIM, pad=4)
    fig.tight_layout()
    fig.savefig(f"{OUT}/fig3-model.png", bbox_inches="tight", facecolor="white")
    fig.savefig(f"{OUT}/fig3-model.svg", bbox_inches="tight", facecolor="white"); plt.close(fig)

for f in (fig1, fig2, fig3):
    f(); print(f.__name__, "ok")
