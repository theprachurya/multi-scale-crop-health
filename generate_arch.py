import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(12, 10))
ax.axis('off')

def draw_box(ax, x, y, width, height, text, facecolor, edgecolor='black', fontsize=10):
    rect = patches.Rectangle((x, y), width, height, linewidth=1.5, edgecolor=edgecolor, facecolor=facecolor, zorder=2)
    ax.add_patch(rect)
    ax.text(x + width/2, y + height/2, text, horizontalalignment='center', verticalalignment='center', fontsize=fontsize, fontweight='bold', zorder=3)
    return rect

# Inputs
draw_box(ax, 1, 8, 2.5, 1, "Leaf Images\n(PlantVillage)\nRGB 224x224", '#d9f0a3')
draw_box(ax, 4.5, 8, 2.5, 1, "UAV Images\n(MH-Soya)\nRGB 224x224", '#addd8e')
draw_box(ax, 8, 8, 2.5, 1, "Satellite Images\n(EuroSAT Proxy)\nRGB 224x224", '#78c679')

for x in [2.25, 5.75, 9.25]:
    ax.annotate('', xy=(x, 7), xytext=(x, 8), arrowprops=dict(facecolor='black', width=2, headwidth=8))

# Backbones
draw_box(ax, 1, 6, 2.5, 1, "EfficientNet-B0\n(Frozen Backbone)", '#bdd7e7')
draw_box(ax, 4.5, 6, 2.5, 1, "ResNet50\n(Frozen Backbone)", '#6baed6')
draw_box(ax, 8, 6, 2.5, 1, "ResNet50\n(Frozen Backbone)", '#3182bd')

for x in [2.25, 5.75, 9.25]:
    ax.annotate('', xy=(x, 5), xytext=(x, 6), arrowprops=dict(facecolor='black', width=2, headwidth=8))

# Vectors
draw_box(ax, 1, 4, 2.5, 1, "Feature Vector\n(1280-dim)", '#fcae91')
draw_box(ax, 4.5, 4, 2.5, 1, "Feature Vector\n(2048-dim)", '#fb6a4a')
draw_box(ax, 8, 4, 2.5, 1, "Feature Vector\n(2048-dim)", '#de2d26')

# Arrows to Concat
ax.annotate('', xy=(5.75, 3), xytext=(2.25, 4), arrowprops=dict(facecolor='black', width=2, headwidth=8))
ax.annotate('', xy=(5.75, 3), xytext=(5.75, 4), arrowprops=dict(facecolor='black', width=2, headwidth=8))
ax.annotate('', xy=(5.75, 3), xytext=(9.25, 4), arrowprops=dict(facecolor='black', width=2, headwidth=8))

# Concat
draw_box(ax, 3.5, 2, 4.5, 1, "Concatenation Fusion\n(5376-dim)", '#cbc9e2')

ax.annotate('', xy=(5.75, 1), xytext=(5.75, 2), arrowprops=dict(facecolor='black', width=2, headwidth=8))

# Head
draw_box(ax, 3.5, 0, 4.5, 1, "Shared Classification Head\nFC(512) -> Dropout(0.5) -> FC(256)\n-> Softmax(3 classes)", '#9e9ac8')

ax.annotate('', xy=(5.75, -1), xytext=(5.75, 0), arrowprops=dict(facecolor='black', width=2, headwidth=8))

# Output
draw_box(ax, 3.5, -2, 4.5, 1, "Output Probability:\nHealthy | Stressed | Diseased", '#dadaeb')

plt.title("MultiScaleCropNet Architecture Diagram", fontsize=16, fontweight='bold', pad=20)
plt.xlim(0, 11.5)
plt.ylim(-3, 10)
plt.tight_layout()
plt.savefig('architecture_diagram.png', dpi=300, bbox_inches='tight')
print("Architecture diagram generated efficiently!")
