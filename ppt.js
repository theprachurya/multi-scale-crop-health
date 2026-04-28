const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "MultiScaleCropNet – Minor Project First Review";

// ─── Design constants ──────────────────────────────────────────────────────
const W = 10, H = 5.625;
const BLACK = "000000", WHITE = "FFFFFF", LGRAY = "D9D9D9", GRAY = "595959", MGRAY = "8C8C8C";
const FONT = "Times New Roman";
const PAD = 0.45; // slide margin

function slideTitle(slide, text) {
  // Black header bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: W, h: 0.55,
    fill: { color: BLACK }, line: { color: BLACK }
  });
  slide.addText(text, {
    x: PAD, y: 0, w: W - PAD * 2, h: 0.55,
    fontSize: 18, bold: true, fontFace: FONT,
    color: WHITE, valign: "middle", align: "left", margin: 0
  });
  // Bottom border line
  slide.addShape(pres.shapes.LINE, {
    x: 0, y: H - 0.06, w: W, h: 0,
    line: { color: BLACK, width: 1.5 }
  });
  // Page footer
  slide.addText("MultiScaleCropNet  |  SRM Institute of Science and Technology  |  Minor Project First Review", {
    x: PAD, y: H - 0.28, w: W - PAD, h: 0.22,
    fontSize: 7, fontFace: FONT, color: MGRAY, align: "left"
  });
}

function hRule(slide, y) {
  slide.addShape(pres.shapes.LINE, {
    x: PAD, y, w: W - PAD * 2, h: 0,
    line: { color: LGRAY, width: 0.8 }
  });
}

function box(slide, x, y, w, h, opts = {}) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h,
    fill: { color: opts.fill || WHITE },
    line: { color: opts.border || BLACK, width: opts.lw || 1 }
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 1 – Title
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: WHITE };

  // Top thick bar
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: W, h: 1.1,
    fill: { color: BLACK }, line: { color: BLACK }
  });

  s.addText("Minor Project – First Review", {
    x: PAD, y: 0.05, w: W - PAD, h: 0.4,
    fontSize: 12, fontFace: FONT, color: "AAAAAA", bold: false, valign: "middle"
  });

  s.addText("Multi-Scale Crop Health Classification\nusing Deep Learning", {
    x: PAD, y: 0.42, w: W - PAD, h: 0.72,
    fontSize: 24, fontFace: FONT, color: WHITE, bold: true, valign: "middle"
  });

  // Tagline
  s.addText("Satellite · UAV · Leaf-Level Multi-Modal CNN Fusion  |  MultiScaleCropNet", {
    x: PAD, y: 1.12, w: W - PAD * 2, h: 0.35,
    fontSize: 11, fontFace: FONT, color: GRAY, italic: true
  });

  // Divider
  s.addShape(pres.shapes.LINE, {
    x: PAD, y: 1.55, w: W - PAD * 2, h: 0,
    line: { color: BLACK, width: 1 }
  });

  // Project info block
  const infoY = 1.72;
  s.addText([
    { text: "Project Category: ", options: { bold: true } },
    { text: "Research  |  " },
    { text: "Guide: ", options: { bold: true } },
    { text: "Dr. E. Poongothai" }
  ], {
    x: PAD, y: infoY, w: W - PAD * 2, h: 0.32,
    fontSize: 12, fontFace: FONT, color: BLACK
  });

  s.addText("Prachurya Subhasmita  (RA2311026010855)      Mohammad Sufyan  (RA2311026010858)", {
    x: PAD, y: infoY + 0.35, w: W - PAD * 2, h: 0.32,
    fontSize: 12, fontFace: FONT, color: BLACK, bold: true
  });

  s.addText("Department of Computational Intelligence\nSRM Institute of Science and Technology, Kattankulathur, Chennai", {
    x: PAD, y: infoY + 0.72, w: W - PAD * 2, h: 0.5,
    fontSize: 11, fontFace: FONT, color: GRAY
  });

  // Result highlight box
  box(s, PAD, 3.22, W - PAD * 2, 0.95, { fill: "F2F2F2", border: BLACK, lw: 1.2 });
  s.addText("Best Result: Full Fusion (Scalar-Weighted)  —  Accuracy: 95.77%  |  F1-Macro: 0.9578  |  10-Configuration Ablation", {
    x: PAD + 0.15, y: 3.28, w: W - PAD * 2 - 0.3, h: 0.45,
    fontSize: 13, fontFace: FONT, color: BLACK, bold: true, align: "center", valign: "middle"
  });
  s.addText("Tested on balanced test set of 804 samples (268 per class)  |  Single seed 42  |  Google Colab T4 GPU  |  PyTorch 2.5.1", {
    x: PAD + 0.15, y: 3.73, w: W - PAD * 2 - 0.3, h: 0.3,
    fontSize: 9.5, fontFace: FONT, color: GRAY, align: "center"
  });

  // Bottom bar
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: H - 0.28, w: W, h: 0.28,
    fill: { color: BLACK }, line: { color: BLACK }
  });
  s.addText("Minor Project  |  SRM Institute of Science and Technology, Chennai  |  2025–2026", {
    x: PAD, y: H - 0.28, w: W - PAD, h: 0.28,
    fontSize: 8, fontFace: FONT, color: "AAAAAA", valign: "middle"
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 2 – Abstract
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  slideTitle(s, "Abstract");

  const CONTENT_Y = 0.72, LINE_H = 5.625 - 0.72 - 0.38;

  s.addText([
    { text: "This paper presents ", options: {} },
    { text: "MultiScaleCropNet", options: { bold: true, italic: true } },
    { text: ", a hierarchical feature-fusion deep learning framework for three-class crop health classification — ", options: {} },
    { text: "Healthy", options: { bold: true } },
    { text: ", ", options: {} },
    { text: "Stressed", options: { bold: true } },
    { text: ", and ", options: {} },
    { text: "Diseased", options: { bold: true } },
    { text: " — by simultaneously fusing imagery from three complementary spatial scales: ground-level leaf photographs (PlantVillage, ≈54,000 images), intermediate-altitude UAV frames (MH-SoyaHealthVision, ≈2,840 images), and macro-level Sentinel-2 satellite tiles (EuroSATallBands, ≈10,500 mapped tiles).", options: {} }
  ], {
    x: PAD, y: CONTENT_Y, w: W - PAD * 2, h: 1.2,
    fontSize: 11, fontFace: FONT, color: BLACK
  });

  hRule(s, CONTENT_Y + 1.3);

  // Four key points in 2×2 layout
  const pts = [
    ["Architecture", "EfficientNet-B0 (leaf, partially fine-tuned) + ResNet50 × 2 (UAV & satellite, fully frozen). Four configurable fusion strategies: concatenation, scalar-weighted (best), learned gating, and cross-modal attention."],
    ["Satellite Labeling", "NDVI-based percentile partition on EuroSATallBands Sentinel-2 TIFFs (B08/B04). Lower 33% → Diseased, middle 34% → Stressed, upper 33% → Healthy. Replaces earlier photometric proxy approach."],
    ["Ablation Study", "Ten-configuration ablation: 3 single-modality, 3 dual-modality, and 4 full-fusion variants. Strict pre-triplet 70/15/15 split isolation. Balanced test set of 804 samples (268 per class)."],
    ["Key Results", "Best model (scalar-weighted full fusion): 95.77% accuracy, F1-macro 0.9578. UAV is strongest single modality (F1 0.9137). Scalar weighting improves over equal concatenation by learning to down-weight noisy NDVI satellite proxy."]
  ];

  const bx = [PAD, 5.3, PAD, 5.3];
  const by = [2.18, 2.18, 3.58, 3.58];
  const bw = 4.6, bh = 1.2;

  pts.forEach((pt, i) => {
    box(s, bx[i], by[i], bw, bh, { fill: "F7F7F7", border: BLACK, lw: 0.8 });
    s.addText(pt[0], {
      x: bx[i] + 0.12, y: by[i] + 0.07, w: bw - 0.24, h: 0.3,
      fontSize: 10.5, fontFace: FONT, color: BLACK, bold: true
    });
    s.addText(pt[1], {
      x: bx[i] + 0.12, y: by[i] + 0.37, w: bw - 0.24, h: bh - 0.42,
      fontSize: 9, fontFace: FONT, color: GRAY, wrap: true
    });
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 3 – Problem Context
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  slideTitle(s, "Problem Context & Motivation");

  // Three modality boxes
  const cols = [
    { label: "Satellite (Macro)", pts: ["10–60 m/pixel Sentinel-2 tiles", "Field-level vegetation vigor", "Cannot resolve lesion textures", "NDVI captures canopy stress proxy"] },
    { label: "UAV (Meso)", pts: ["Centimetre-scale aerial imaging", "Canopy structure & spread patterns", "Mottling, defoliation visible", "Limited land-context awareness"] },
    { label: "Leaf (Micro)", pts: ["Sub-millimetre focal photography", "Fine-grained lesion morphology", "Colour, texture, boundary detail", "No field-level spatial context"] }
  ];

  const cw = 2.8, ch = 2.4, cy = 0.72, gap = 0.2;
  const startX = (W - 3 * cw - 2 * gap) / 2;

  cols.forEach((c, i) => {
    const cx = startX + i * (cw + gap);
    box(s, cx, cy, cw, ch, { fill: "F2F2F2", border: BLACK, lw: 1 });
    s.addText(c.label, {
      x: cx + 0.12, y: cy + 0.1, w: cw - 0.24, h: 0.35,
      fontSize: 11, fontFace: FONT, color: BLACK, bold: true, align: "center"
    });
    hRule(s, cy + 0.45);
    c.pts.forEach((pt, j) => {
      s.addText([{ text: "▸  " + pt, options: {} }], {
        x: cx + 0.12, y: cy + 0.52 + j * 0.42, w: cw - 0.24, h: 0.4,
        fontSize: 9, fontFace: FONT, color: GRAY
      });
    });
  });

  // Arrow between boxes
  s.addText("→", {
    x: startX + cw + 0.02, y: cy + ch / 2 - 0.2, w: gap, h: 0.4,
    fontSize: 18, fontFace: FONT, color: BLACK, align: "center", bold: true
  });
  s.addText("→", {
    x: startX + 2 * cw + gap + 0.02, y: cy + ch / 2 - 0.2, w: gap, h: 0.4,
    fontSize: 18, fontFace: FONT, color: BLACK, align: "center", bold: true
  });

  // Fragmentation problem
  box(s, PAD, cy + ch + 0.22, W - PAD * 2, 1.08, { fill: "F2F2F2", border: BLACK, lw: 1 });
  s.addText("Core Fragmentation Problem", {
    x: PAD + 0.15, y: cy + ch + 0.28, w: W - PAD * 2 - 0.3, h: 0.3,
    fontSize: 11, fontFace: FONT, color: BLACK, bold: true, align: "center"
  });
  s.addText([
    { text: "Manual inspection", options: { bold: true } },
    { text: " is subjective and unscalable.  " },
    { text: "Satellite-only", options: { bold: true } },
    { text: " models cannot resolve fine-grained disease.  " },
    { text: "Leaf-level CNNs", options: { bold: true } },
    { text: " lack field context.  No prior work fuses all three CNN-based modalities under a controlled ablation." }
  ], {
    x: PAD + 0.15, y: cy + ch + 0.6, w: W - PAD * 2 - 0.3, h: 0.55,
    fontSize: 10, fontFace: FONT, color: GRAY, align: "center"
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 4 – Research Objectives
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  slideTitle(s, "Research Objectives");

  const objectives = [
    ["O1", "Single-Scale Baselines", "Train and evaluate independent CNN baselines for each modality: EfficientNet-B0 (leaf), ResNet50 (UAV), ResNet50 (satellite). Establish per-scale performance benchmarks."],
    ["O2", "Multi-Branch Architecture", "Design MultiScaleCropNet — a unified multi-branch architecture with dedicated pretrained encoders per modality, independent non-shared weights, and configurable fusion strategies."],
    ["O3", "Feature-Level Fusion", "Implement and compare four fusion strategies: concatenation (5376-d), scalar-weighted (512-d, learnable), learned gating (sample-wise), and cross-modal attention fusion."],
    ["O4", "NDVI Satellite Labeling", "Partition EuroSATallBands tiles using NDVI percentile bands from Sentinel-2 B08/B04 to derive a physically grounded health-state taxonomy, replacing photometric proxies."],
    ["O5", "10-Configuration Ablation", "Conduct a complete 10-configuration ablation covering all single, dual, and full fusion variants (including 4 fusion-strategy comparisons) to quantify each modality and fusion contribution."]
  ];

  const OX = PAD, OW = 1.1 - PAD, TW = W - OX - 0.2;

  objectives.forEach((o, i) => {
    const oy = 0.72 + i * 0.9;
    // Number circle
    box(s, OX, oy + 0.08, 0.55, 0.55, { fill: BLACK, border: BLACK });
    s.addText(o[0], {
      x: OX, y: oy + 0.08, w: 0.55, h: 0.55,
      fontSize: 11, fontFace: FONT, color: WHITE, bold: true, align: "center", valign: "middle"
    });
    s.addText(o[1], {
      x: OX + 0.65, y: oy + 0.05, w: TW - 0.65, h: 0.28,
      fontSize: 11, fontFace: FONT, color: BLACK, bold: true
    });
    s.addText(o[2], {
      x: OX + 0.65, y: oy + 0.32, w: TW - 0.65, h: 0.5,
      fontSize: 9.5, fontFace: FONT, color: GRAY
    });
    if (i < objectives.length - 1) hRule(s, oy + 0.88);
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 5 – Dataset Description
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  slideTitle(s, "Dataset Description & Biological Taxonomy");

  const datasets = [
    {
      name: "PlantVillage  (Leaf / Micro)",
      stats: "~54,000 images  |  38 disease labels  |  14 crop species",
      rows: [
        ["Healthy", "Any folder containing ___healthy substring"],
        ["Stressed", "Cedar Apple Rust, Powdery Mildew, Common Rust, Spider Mites, Leaf Scorch  (surface, reversible)"],
        ["Diseased", "Bacterial Spot, Early/Late Blight, Black Rot, YLCV, Mosaic Virus, Huanglongbing  (systemic)"]
      ],
      note: "Yields: 3,260 Healthy | 5,256 Stressed | 23,162 Diseased"
    },
    {
      name: "MH-SoyaHealthVision  (UAV / Meso)",
      stats: "~2,840 images  |  Soybean only  |  UAV aerial dataset",
      rows: [
        ["Healthy", "Healthy_Soyabean folder"],
        ["Stressed", "Soyabean Rust, Semilooper Pest Attack, Caterpillar Pest Attack  (mechanical, reversible)"],
        ["Diseased", "Soyabean Mosaic Virus — systemic, spreads through phloem, no cure"]
      ],
      note: "Yields: 280 Healthy | 1,790 Stressed | 772 Diseased  (smallest pool; heavy UAV oversampling)"
    },
    {
      name: "EuroSATallBands  (Satellite / Macro)",
      stats: "~10,500 mapped tiles  |  13-band Sentinel-2  |  64×64 pixels",
      rows: [
        ["Healthy", "AnnualCrop, PermanentCrop (managed cropland NDVI prior) → upper 33% NDVI"],
        ["Stressed", "HerbaceousVegetation, Pasture (unmanaged stress-prone prior) → middle 34% NDVI"],
        ["Diseased", "Lower 33% NDVI from mapped classes. NDVI = (B08−B04)/(B08+B04+ε). Proxy for low-vigor canopy."]
      ],
      note: "NDVI partition replaces earlier photometric proxy. Satellite labels are proxy canopy-health, not confirmed pathology."
    }
  ];

  const dh = 1.48, dw = W - PAD * 2;
  datasets.forEach((d, i) => {
    const dy = 0.68 + i * (dh + 0.12);
    box(s, PAD, dy, dw, dh, { fill: "F9F9F9", border: BLACK, lw: 0.8 });
    s.addText(d.name, {
      x: PAD + 0.12, y: dy + 0.06, w: 5.5, h: 0.28,
      fontSize: 10.5, fontFace: FONT, color: BLACK, bold: true
    });
    s.addText(d.stats, {
      x: PAD + 0.12, y: dy + 0.06, w: dw - 0.24, h: 0.28,
      fontSize: 9, fontFace: FONT, color: MGRAY, align: "right"
    });
    d.rows.forEach((r, j) => {
      s.addText(r[0] + ":", {
        x: PAD + 0.12, y: dy + 0.36 + j * 0.3, w: 1.0, h: 0.26,
        fontSize: 9, fontFace: FONT, color: BLACK, bold: true
      });
      s.addText(r[1], {
        x: PAD + 1.14, y: dy + 0.36 + j * 0.3, w: dw - 1.26, h: 0.26,
        fontSize: 9, fontFace: FONT, color: GRAY
      });
    });
    s.addText(d.note, {
      x: PAD + 0.12, y: dy + dh - 0.27, w: dw - 0.24, h: 0.22,
      fontSize: 8.5, fontFace: FONT, color: BLACK, italic: true
    });
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 6 – System Architecture
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  slideTitle(s, "System Architecture — MultiScaleCropNet");

  // Left: architecture diagram (text-based)
  const diag = [
    ["INPUT TRIPLET", "(Leaf 224×224,  UAV 224×224,  Satellite 224×224)", false],
    ["", "↓  ↓  ↓", false],
    ["BACKBONE ENCODERS", "", true],
    ["EfficientNet-B0 (Leaf)", "Partially fine-tuned  |  features.7–8 trainable  |  Output: 1280-d", false],
    ["ResNet50 (UAV)", "Fully frozen  |  layer4 frozen  |  Output: 2048-d", false],
    ["ResNet50 (Satellite)", "Fully frozen  |  Separate weight instance  |  Output: 2048-d", false],
    ["", "↓", false],
    ["FUSION MODULE", "ConcatFusion [1280 ‖ 2048 ‖ 2048] = 5376-d  |  or  ScalarWeighted (512-d, best)  |  Attention / Gating", false],
    ["", "↓", false],
    ["CLASSIFICATION HEAD", "FC(5376→1024) → BN → ReLU → Dropout(0.5)", false],
    ["", "FC(1024→256) → BN → ReLU → Dropout(0.3)", false],
    ["", "FC(256→3) → Softmax", false],
    ["", "↓", false],
    ["OUTPUT", "Healthy  /  Stressed  /  Diseased", false],
  ];

  const DX = PAD, DY = 0.7, DW = 5.5, rowH = 0.29;
  diag.forEach((row, i) => {
    if (row[2]) {
      s.addText(row[0], {
        x: DX, y: DY + i * rowH, w: DW, h: rowH,
        fontSize: 9, fontFace: FONT, color: BLACK, bold: true
      });
    } else if (row[0]) {
      s.addText(row[0] + ":", {
        x: DX, y: DY + i * rowH, w: 2.0, h: rowH,
        fontSize: 9, fontFace: FONT, color: BLACK, bold: true
      });
      s.addText(row[1], {
        x: DX + 2.05, y: DY + i * rowH, w: DW - 2.05, h: rowH,
        fontSize: 9, fontFace: FONT, color: GRAY
      });
    } else {
      s.addText(row[1], {
        x: DX, y: DY + i * rowH, w: DW, h: rowH,
        fontSize: 10, fontFace: FONT, color: BLACK, align: "left"
      });
    }
  });

  // Right: specs panel
  const RX = 6.1, RY = 0.68, RW = W - RX - PAD, RH = H - RY - 0.38;
  box(s, RX, RY, RW, RH, { fill: "F2F2F2", border: BLACK, lw: 1 });

  const specs = [
    ["Model Parameters"],
    ["EfficientNet-B0", "5.3M params"],
    ["ResNet50 × 2", "25.6M each"],
    ["Head + Fusion", "~5M trainable"],
    [""],
    ["Fusion Strategies"],
    ["Concat", "5376-d, param-free"],
    ["Scalar-Weighted ★", "512-d, best result"],
    ["Learned Gating", "collapsed (0.7536)"],
    ["Attention", "512-d, 4 heads"],
    [""],
    ["Training Config"],
    ["Epochs", "12 (early stop p=10)"],
    ["Batch size", "8 (4 GB VRAM)"],
    ["Optimizer", "AdamW"],
    ["LR (backbone)", "1e-4"],
    ["LR (head)", "1e-3"],
    ["Label smoothing", "ε = 0.1"],
    ["Seed", "42  |  Single split"],
  ];

  let ry = RY + 0.1;
  specs.forEach(r => {
    if (r.length === 1) {
      if (r[0]) {
        s.addText(r[0], {
          x: RX + 0.12, y: ry, w: RW - 0.24, h: 0.25,
          fontSize: 9, fontFace: FONT, color: BLACK, bold: true
        });
      }
      ry += r[0] ? 0.26 : 0.1;
    } else {
      s.addText(r[0], {
        x: RX + 0.15, y: ry, w: 1.5, h: 0.23,
        fontSize: 8.5, fontFace: FONT, color: GRAY
      });
      s.addText(r[1], {
        x: RX + 1.65, y: ry, w: RW - 1.77, h: 0.23,
        fontSize: 8.5, fontFace: FONT, color: BLACK, bold: true
      });
      ry += 0.24;
    }
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 7 – Data Pipeline
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  slideTitle(s, "Data Pipeline & Triplet Construction");

  const steps = [
    ["1. Data Ingestion", "PlantVillage ZIP → data/raw/leaf/. MH-Soya ZIP (nested) → data/raw/uav/. EuroSATallBands ZIP → data/raw/satellite/ (TIFFs retained for NDVI)."],
    ["2. NDVI Labeling (Satellite)", "For each EuroSATallBands TIFF: compute mean NDVI = (B08 − B04) / (B08 + B04 + 1e-8). Dataset-adaptive percentile partition: lower 33% → Diseased, middle 34% → Stressed, upper 33% → Healthy. On-the-fly RGB from B04/B03/B02 for model input."],
    ["3. Leaf & UAV Alignment", "Keyword-based folder mapping per biological taxonomy. UAV pool sorted chronologically before splitting to prevent adjacent video-frame leakage between train/test."],
    ["4. Zero-Leakage Split", "For each class c and modality m: raw pool → sorted → 70/15/15 split into disjoint train/val/test pools. Triplets formed by sampling independently with replacement within matching-class pools only."],
    ["5. Triplet Generation", "Class-balanced oversampling: max(⌊N_min × ratio⌋, N_floor) triplets per class. Floors: 1000 (train) / 200 (val) / 200 (test). Final: 3,759 train | 804 val | 804 test (268/class each)."],
    ["6. Augmentation", "Train: Resize(256)→RandomCrop(224)→HFlip(0.5)→VFlip(0.3)→Rotation(±15°)→ColorJitter→Grayscale(0.05)→Normalize(ImageNet). Val/Test: Resize(224)→Normalize only."]
  ];

  const sh = 0.71, sw = W - PAD * 2, sx = PAD;
  steps.forEach((st, i) => {
    const sy = 0.7 + i * (sh + 0.04);
    box(s, sx, sy, sw, sh, { fill: i % 2 === 0 ? "F9F9F9" : WHITE, border: LGRAY, lw: 0.7 });
    s.addText(st[0], {
      x: sx + 0.12, y: sy + 0.06, w: 2.4, h: sh - 0.12,
      fontSize: 9.5, fontFace: FONT, color: BLACK, bold: true, valign: "top"
    });
    s.addText(st[1], {
      x: sx + 2.52, y: sy + 0.06, w: sw - 2.64, h: sh - 0.12,
      fontSize: 9, fontFace: FONT, color: GRAY, valign: "top", wrap: true
    });
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 8 – Training Setup
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  slideTitle(s, "Training Setup & Anti-Overfitting Measures");

  // Two columns
  const col1 = [
    ["Loss Function", "Cross-entropy with label smoothing ε = 0.1. Prevents overconfident predictions on NDVI proxy satellite labels. For full_fusion_weighted: additional cross-scale KL consistency regulariser between leaf and UAV auxiliary logits (T=2.0, λ=0.2)."],
    ["Optimizer", "AdamW with decoupled weight decay (1e-4). Differential LRs: backbone 1e-4, head/fusion 1e-3. CosineAnnealingLR scheduler with η_min = 1e-6."],
    ["Training Protocol", "12 epochs, early stopping patience 10. Batch size 8 (4 GB VRAM constraint). Random seed 42. Google Colab Tesla T4, PyTorch 2.5.1 + CUDA 12.1. Best-val-loss checkpoint restored for evaluation."],
    ["Hardware", "NVIDIA Tesla T4 (Google Colab). 4 GB VRAM at batch size 8. Single-triplet inference < 200 ms. Flask inference dashboard at localhost:5000."]
  ];

  const anti = [
    "Backbone freezing (most layers) — preserves ImageNet pre-trained features",
    "Aggressive data augmentation — random crop, flip, rotation, colour jitter",
    "Label smoothing (ε = 0.1) — prevents overconfident predictions on proxy labels",
    "Dropout — p = 0.5 (FC layer 1), p = 0.3 (FC layer 2)",
    "BatchNorm — before each activation in classification head",
    "Weight decay (L2) — 1e-4 via AdamW",
    "Gradient clipping — max ℓ₂ norm 1.0",
    "Early stopping — patience 10 on validation loss",
    "CosineAnnealingLR — prevents learning rate plateaus",
    "Train/Val gap monitoring — warning at 15% accuracy divergence",
  ];

  // Left column
  const LX = PAD, LW = 5.1;
  col1.forEach((item, i) => {
    const cy = 0.7 + i * 1.1;
    s.addText(item[0], {
      x: LX, y: cy, w: LW, h: 0.28,
      fontSize: 10.5, fontFace: FONT, color: BLACK, bold: true
    });
    s.addText(item[1], {
      x: LX, y: cy + 0.28, w: LW, h: 0.75,
      fontSize: 9, fontFace: FONT, color: GRAY, wrap: true
    });
    if (i < col1.length - 1) hRule(s, cy + 1.05);
  });

  // Right column – anti-overfitting
  const RX = 5.7, RW = W - RX - PAD;
  box(s, RX, 0.68, RW, H - 0.68 - 0.35, { fill: "F2F2F2", border: BLACK, lw: 0.8 });
  s.addText("Anti-Overfitting Measures", {
    x: RX + 0.12, y: 0.74, w: RW - 0.24, h: 0.3,
    fontSize: 10.5, fontFace: FONT, color: BLACK, bold: true, align: "center"
  });
  anti.forEach((a, i) => {
    s.addText([{ text: a, options: { bullet: true } }], {
      x: RX + 0.15, y: 1.1 + i * 0.38, w: RW - 0.27, h: 0.36,
      fontSize: 9, fontFace: FONT, color: GRAY
    });
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 9 – Ablation Results Table
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  slideTitle(s, "Ablation Study Results — 10-Configuration Comparison");

  // Table header + data
  const tableData = [
    [
      { text: "Configuration", options: { bold: true, fontFace: FONT, fontSize: 10, fill: { color: "000000" }, color: "FFFFFF" } },
      { text: "Acc.", options: { bold: true, fontFace: FONT, fontSize: 10, fill: { color: "000000" }, color: "FFFFFF", align: "center" } },
      { text: "Prec.", options: { bold: true, fontFace: FONT, fontSize: 10, fill: { color: "000000" }, color: "FFFFFF", align: "center" } },
      { text: "Rec.", options: { bold: true, fontFace: FONT, fontSize: 10, fill: { color: "000000" }, color: "FFFFFF", align: "center" } },
      { text: "F1 Macro", options: { bold: true, fontFace: FONT, fontSize: 10, fill: { color: "000000" }, color: "FFFFFF", align: "center" } },
      { text: "Category", options: { bold: true, fontFace: FONT, fontSize: 10, fill: { color: "000000" }, color: "FFFFFF", align: "center" } }
    ],
    // Single modality
    [
      { text: "Satellite Only", options: { fontFace: FONT, fontSize: 9.5 } },
      { text: "0.5199", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "0.5551", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "0.5199", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "0.4810", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "Single", options: { fontFace: FONT, fontSize: 9.5, align: "center", color: "595959" } }
    ],
    [
      { text: "UAV Only", options: { fontFace: FONT, fontSize: 9.5 } },
      { text: "0.9142", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "0.9134", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "0.9142", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "0.9137", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "Single ★", options: { fontFace: FONT, fontSize: 9.5, align: "center", color: "595959" } }
    ],
    [
      { text: "Leaf Only", options: { fontFace: FONT, fontSize: 9.5 } },
      { text: "0.7338", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "0.8047", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "0.7338", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "0.7149", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "Single", options: { fontFace: FONT, fontSize: 9.5, align: "center", color: "595959" } }
    ],
    // Dual modality
    [
      { text: "Satellite + UAV", options: { fontFace: FONT, fontSize: 9.5 } },
      { text: "0.9328", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "0.9336", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "0.9328", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "0.9322", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "Dual", options: { fontFace: FONT, fontSize: 9.5, align: "center", color: "595959" } }
    ],
    [
      { text: "UAV + Leaf", options: { fontFace: FONT, fontSize: 9.5 } },
      { text: "0.9490", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "0.9514", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "0.9490", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "0.9493", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "Dual ★", options: { fontFace: FONT, fontSize: 9.5, align: "center", color: "595959" } }
    ],
    [
      { text: "Satellite + Leaf", options: { fontFace: FONT, fontSize: 9.5 } },
      { text: "0.7774", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "0.8210", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "0.7774", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "0.7708", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "Dual", options: { fontFace: FONT, fontSize: 9.5, align: "center", color: "595959" } }
    ],
    // Full fusion variants
    [
      { text: "Full Fusion (Concat)", options: { fontFace: FONT, fontSize: 9.5 } },
      { text: "0.9490", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "0.9512", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "0.9490", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "0.9494", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "Full", options: { fontFace: FONT, fontSize: 9.5, align: "center", color: "595959" } }
    ],
    [
      { text: "Full Fusion (Weighted)  ★ BEST", options: { fontFace: FONT, fontSize: 9.5, bold: true } },
      { text: "0.9577", options: { fontFace: FONT, fontSize: 9.5, align: "center", bold: true } },
      { text: "0.9584", options: { fontFace: FONT, fontSize: 9.5, align: "center", bold: true } },
      { text: "0.9577", options: { fontFace: FONT, fontSize: 9.5, align: "center", bold: true } },
      { text: "0.9578", options: { fontFace: FONT, fontSize: 9.5, align: "center", bold: true } },
      { text: "Full ★", options: { fontFace: FONT, fontSize: 9.5, align: "center", bold: true } }
    ],
    [
      { text: "Full Fusion (Learned Gating)", options: { fontFace: FONT, fontSize: 9.5, italic: true } },
      { text: "0.7637", options: { fontFace: FONT, fontSize: 9.5, align: "center", italic: true } },
      { text: "0.8144", options: { fontFace: FONT, fontSize: 9.5, align: "center", italic: true } },
      { text: "0.7637", options: { fontFace: FONT, fontSize: 9.5, align: "center", italic: true } },
      { text: "0.7536", options: { fontFace: FONT, fontSize: 9.5, align: "center", italic: true } },
      { text: "Full (collapse)", options: { fontFace: FONT, fontSize: 9.5, align: "center", italic: true, color: "595959" } }
    ],
    [
      { text: "Full Fusion (Attention)", options: { fontFace: FONT, fontSize: 9.5 } },
      { text: "0.9515", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "0.9531", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "0.9515", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "0.9509", options: { fontFace: FONT, fontSize: 9.5, align: "center" } },
      { text: "Full", options: { fontFace: FONT, fontSize: 9.5, align: "center", color: "595959" } }
    ]
  ];

  s.addTable(tableData, {
    x: PAD, y: 0.66,
    w: W - PAD * 2,
    colW: [3.1, 0.95, 0.95, 0.95, 1.05, 1.55],
    border: { pt: 0.8, color: "000000" },
    rowH: 0.36
  });

  s.addText("★ Best single modality: UAV Only (F1 0.9137)  |  ★ Best dual: UAV+Leaf (F1 0.9493)  |  ★ Best overall: Full Fusion Weighted (F1 0.9578)  |  Learned Gating collapses to F1 0.7536", {
    x: PAD, y: H - 0.52, w: W - PAD * 2, h: 0.2,
    fontSize: 8, fontFace: FONT, color: MGRAY, italic: true
  });
  s.addText("All results: balanced test set, 268 samples/class, 804 total  |  Single seed 42  |  Single split  |  outputs/metrics/ablation_results.csv", {
    x: PAD, y: H - 0.34, w: W - PAD * 2, h: 0.18,
    fontSize: 7.5, fontFace: FONT, color: MGRAY, italic: true
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 10 – Per-Class Results & Confusion Matrix (text)
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  slideTitle(s, "Per-Class Results — Full Fusion (Scalar-Weighted)");

  // Per-class table
  const perClassData = [
    [
      { text: "Class", options: { bold: true, fontFace: FONT, fontSize: 11, fill: { color: "000000" }, color: "FFFFFF" } },
      { text: "Precision", options: { bold: true, fontFace: FONT, fontSize: 11, fill: { color: "000000" }, color: "FFFFFF", align: "center" } },
      { text: "Recall", options: { bold: true, fontFace: FONT, fontSize: 11, fill: { color: "000000" }, color: "FFFFFF", align: "center" } },
      { text: "F1-Score", options: { bold: true, fontFace: FONT, fontSize: 11, fill: { color: "000000" }, color: "FFFFFF", align: "center" } },
      { text: "Support", options: { bold: true, fontFace: FONT, fontSize: 11, fill: { color: "000000" }, color: "FFFFFF", align: "center" } }
    ],
    [
      { text: "Healthy", options: { fontFace: FONT, fontSize: 11 } },
      { text: "1.0000", options: { fontFace: FONT, fontSize: 11, align: "center" } },
      { text: "0.9701", options: { fontFace: FONT, fontSize: 11, align: "center" } },
      { text: "0.9848", options: { fontFace: FONT, fontSize: 11, align: "center" } },
      { text: "268", options: { fontFace: FONT, fontSize: 11, align: "center" } }
    ],
    [
      { text: "Stressed", options: { fontFace: FONT, fontSize: 11 } },
      { text: "0.9432", options: { fontFace: FONT, fontSize: 11, align: "center" } },
      { text: "0.9291", options: { fontFace: FONT, fontSize: 11, align: "center" } },
      { text: "0.9361", options: { fontFace: FONT, fontSize: 11, align: "center" } },
      { text: "268", options: { fontFace: FONT, fontSize: 11, align: "center" } }
    ],
    [
      { text: "Diseased", options: { fontFace: FONT, fontSize: 11 } },
      { text: "0.9321", options: { fontFace: FONT, fontSize: 11, align: "center" } },
      { text: "0.9739", options: { fontFace: FONT, fontSize: 11, align: "center" } },
      { text: "0.9526", options: { fontFace: FONT, fontSize: 11, align: "center" } },
      { text: "268", options: { fontFace: FONT, fontSize: 11, align: "center" } }
    ],
    [
      { text: "Macro Average", options: { bold: true, fontFace: FONT, fontSize: 11 } },
      { text: "0.9584", options: { bold: true, fontFace: FONT, fontSize: 11, align: "center" } },
      { text: "0.9577", options: { bold: true, fontFace: FONT, fontSize: 11, align: "center" } },
      { text: "0.9578", options: { bold: true, fontFace: FONT, fontSize: 11, align: "center" } },
      { text: "804", options: { bold: true, fontFace: FONT, fontSize: 11, align: "center" } }
    ]
  ];

  s.addTable(perClassData, {
    x: PAD, y: 0.68,
    w: 5.4,
    colW: [1.5, 1.0, 1.0, 1.0, 0.9],
    border: { pt: 0.8, color: "000000" },
    rowH: 0.42
  });

  // Confusion matrix (text-rendered)
  const CMX = 6.0, CMY = 0.68, CMW = W - CMX - PAD;
  s.addText("Confusion Matrix (Predicted →)", {
    x: CMX, y: CMY, w: CMW, h: 0.3,
    fontSize: 9.5, fontFace: FONT, color: BLACK, bold: true, align: "center"
  });

  // Draw confusion matrix manually
  const labels = ["Healthy", "Stressed", "Diseased"];
  const cmValues = [[260, 8, 0], [0, 249, 19], [0, 7, 261]];
  const cellSize = 0.72;
  const cmStartX = CMX + 0.6;
  const cmStartY = CMY + 0.62;

  // Column headers
  labels.forEach((l, j) => {
    s.addText(l, {
      x: cmStartX + j * cellSize, y: cmStartY - 0.28, w: cellSize, h: 0.26,
      fontSize: 8.5, fontFace: FONT, color: BLACK, align: "center", bold: true
    });
  });

  // Row headers + cells
  labels.forEach((rowLabel, i) => {
    s.addText(rowLabel, {
      x: CMX, y: cmStartY + i * cellSize, w: 0.58, h: cellSize,
      fontSize: 8.5, fontFace: FONT, color: BLACK, align: "right", valign: "middle", bold: true
    });
    cmValues[i].forEach((val, j) => {
      const isDiag = i === j;
      box(s, cmStartX + j * cellSize, cmStartY + i * cellSize, cellSize, cellSize,
        { fill: isDiag ? "D9D9D9" : WHITE, border: BLACK, lw: 0.8 });
      s.addText(val.toString(), {
        x: cmStartX + j * cellSize, y: cmStartY + i * cellSize,
        w: cellSize, h: cellSize,
        fontSize: isDiag ? 14 : 12, fontFace: FONT, color: BLACK,
        bold: isDiag, align: "center", valign: "middle"
      });
    });
  });

  // True label annotation
  s.addText("True Label ↓", {
    x: CMX, y: cmStartY + cellSize * 0.8, w: 0.55, h: 0.6,
    fontSize: 8, fontFace: FONT, color: BLACK, align: "center", italic: true
  });

  // Key observations
  const obsY = cmStartY + 3 * cellSize + 0.15;
  s.addText("Key Observations", {
    x: PAD, y: obsY, w: W - PAD * 2, h: 0.27,
    fontSize: 10.5, fontFace: FONT, color: BLACK, bold: true
  });

  const obs = [
    "Healthy achieves perfect precision (1.0000) — zero false-positive predictions for healthy class.",
    "Residual confusion concentrates between Stressed and Diseased (19 Stressed→Diseased; 7 Diseased→Stressed) — semantically adjacent classes.",
    "Satellite equal-weight fusion adds no measurable gain over UAV+Leaf. Scalar weighting learns to down-weight noisy NDVI satellite proxy."
  ];
  obs.forEach((o, i) => {
    s.addText([{ text: o, options: { bullet: true } }], {
      x: PAD, y: obsY + 0.3 + i * 0.3, w: W - PAD * 2, h: 0.28,
      fontSize: 9, fontFace: FONT, color: GRAY
    });
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 11 – Training Dynamics
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  slideTitle(s, "Training Dynamics & Model Integrity");

  // Training curve data (native bar/line chart)
  const epochs = ["Ep 1", "Ep 5", "Ep 7", "Ep 8", "Ep 12"];
  const trainLoss = [0.5682, 0.3812, 0.3662, 0.3585, 0.3369];
  const valLoss = [0.3940, 0.3508, 0.3062, 0.4217, 0.3199];
  const valF1 = [0.9449, 0.9813, 0.9975, 0.9205, 0.9838];

  s.addChart(pres.charts.LINE, [
    { name: "Train Loss", labels: epochs, values: trainLoss },
    { name: "Val Loss", labels: epochs, values: valLoss }
  ], {
    x: PAD, y: 0.68, w: 4.5, h: 2.3,
    showTitle: true, title: "Loss: Full Fusion Weighted",
    titleFontSize: 10, titleFontFace: FONT,
    chartColors: ["000000", "595959"],
    lineSize: 2,
    catAxisLabelColor: GRAY, valAxisLabelColor: GRAY,
    valGridLine: { color: "E0E0E0", size: 0.5 },
    catGridLine: { style: "none" },
    chartArea: { fill: { color: "FFFFFF" } },
    showLegend: true, legendFontFace: FONT, legendFontSize: 8, legendPos: "b"
  });

  s.addChart(pres.charts.LINE, [
    { name: "Val F1", labels: epochs, values: valF1 }
  ], {
    x: PAD, y: 3.1, w: 4.5, h: 2.1,
    showTitle: true, title: "Validation F1: Full Fusion Weighted",
    titleFontSize: 10, titleFontFace: FONT,
    chartColors: ["000000"],
    lineSize: 2,
    catAxisLabelColor: GRAY, valAxisLabelColor: GRAY,
    valGridLine: { color: "E0E0E0", size: 0.5 },
    catGridLine: { style: "none" },
    chartArea: { fill: { color: "FFFFFF" } },
    showLegend: false
  });

  // Right: integrity notes
  const RX = 5.1, RW = W - RX - PAD, RY = 0.68;
  box(s, RX, RY, RW, 2.1, { fill: "F2F2F2", border: BLACK, lw: 0.8 });
  s.addText("Model Integrity Checks", {
    x: RX + 0.12, y: RY + 0.08, w: RW - 0.24, h: 0.28,
    fontSize: 10.5, fontFace: FONT, color: BLACK, bold: true
  });

  const integrityPts = [
    "Sequential UAV isolation: video frames sorted chronologically before 70/15/15 split — no adjacent-frame leakage.",
    "Taxonomic hardening: PlantVillage 38-class → 3-class biological taxonomy. Leaf-only scores 73.38% (not 99%), confirming no dataset memorisation shortcut.",
    "Satellite ceiling: Satellite-only F1 0.4810 (accuracy 51.99%) — reflects genuine NDVI labeling difficulty at 10m resolution, confirming no data artefact leakage.",
    "Zero cross-split leakage: image pools split per class per modality before any triplet sampling."
  ];
  integrityPts.forEach((pt, i) => {
    s.addText([{ text: pt, options: { bullet: true } }], {
      x: RX + 0.15, y: RY + 0.42 + i * 0.38, w: RW - 0.27, h: 0.36,
      fontSize: 8.5, fontFace: FONT, color: GRAY
    });
  });

  // Training dynamics explanation
  box(s, RX, RY + 2.2, RW, 2.1, { fill: WHITE, border: BLACK, lw: 0.8 });
  s.addText("Training Dynamics Notes", {
    x: RX + 0.12, y: RY + 2.27, w: RW - 0.24, h: 0.28,
    fontSize: 10.5, fontFace: FONT, color: BLACK, bold: true
  });
  const dynPts = [
    "Training accuracy < Validation accuracy is expected: aggressive augmentation makes training images harder; frozen backbones generalise from ImageNet from epoch 1.",
    "Validation spike at Epoch 8 (Val Loss 0.4217 vs 0.3062 at Ep 7) — late-stage instability motivates best-checkpoint restoration.",
    "Best checkpoint: Epoch 7 (Val Loss 0.3062, Val F1 0.9975). Test evaluation uses this checkpoint, not final epoch weights.",
    "Single seed 42, single split. Results are preliminary point estimates; repeated-seed evaluation needed for robust statistical claims."
  ];
  dynPts.forEach((pt, i) => {
    s.addText([{ text: pt, options: { bullet: true } }], {
      x: RX + 0.15, y: RY + 2.62 + i * 0.38, w: RW - 0.27, h: 0.36,
      fontSize: 8.5, fontFace: FONT, color: GRAY
    });
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 12 – F1 Bar Chart (ablation comparison)
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  slideTitle(s, "Ablation Study — Macro F1-Score Comparison");

  const configs = ["Sat Only","UAV Only","Leaf Only","Sat+UAV","UAV+Leaf","Sat+Leaf","Concat","Weighted","Gating","Attention"];
  const f1vals = [0.4810, 0.9137, 0.7149, 0.9322, 0.9493, 0.7708, 0.9494, 0.9578, 0.7536, 0.9509];

  s.addChart(pres.charts.BAR, [{
    name: "F1 Macro",
    labels: configs,
    values: f1vals
  }], {
    x: PAD, y: 0.68, w: W - PAD * 2, h: 4.2,
    barDir: "bar",
    chartColors: ["000000", "000000", "000000", "595959", "595959", "595959", "888888", "000000", "BBBBBB", "888888"],
    chartArea: { fill: { color: "FFFFFF" } },
    catAxisLabelColor: "000000", catAxisLabelFontFace: FONT, catAxisLabelFontSize: 9.5,
    valAxisLabelColor: "595959", valAxisLabelFontFace: FONT, valAxisLabelFontSize: 8,
    valGridLine: { color: "E0E0E0", size: 0.5 },
    catGridLine: { style: "none" },
    showValue: true,
    dataLabelColor: "000000", dataLabelFontFace: FONT, dataLabelFontSize: 9,
    showLegend: false,
    valAxisMinVal: 0.4,
    valAxisMaxVal: 1.0
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 13 – Limitations & Future Work
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  slideTitle(s, "Limitations & Future Work");

  const limits = [
    ["Proxy Satellite Labels", "NDVI is a vegetation vigor index — cannot disambiguate etiology (pathogen vs. drought vs. nutrient). Satellite results reflect proxy canopy-health, not confirmed pathogen detection."],
    ["Non-Co-Registered Triplets", "Modalities are from independent public datasets. Triplets are semantically (label) aligned but not spatially/temporally co-registered. Results characterise cross-dataset fusion, not farm-scale monitoring."],
    ["UAV Pool Repetition", "MH-SoyaHealthVision UAV pool (2,840 images) is the smallest modality. After 70/15/15 split, UAV training images recur heavily due to oversampling. Effect on representations not isolated."],
    ["Single Seed & Split", "All results from seed 42, one split. No repeated-seed confidence intervals or significance tests. Preliminary point estimates only."],
    ["ImageNet Transfer Gap", "UAV and satellite ResNet50 branches are fully frozen ImageNet models — no agricultural domain pre-training. General-purpose features may be suboptimal."],
    ["Learned Gating Instability", "full_fusion_learned_gating collapses to near-leaf-only (F1 0.7536) due to modality weight collapse. Requires gate-entropy regularisation or larger training corpus."]
  ];

  const future = [
    "Replace NDVI satellite partitions with ground-truth acquisitions from Sen4AgriNet or NASA Harvest",
    "Collect or identify co-registered leaf/UAV/satellite observations from the same agronomic scene",
    "Run repeated-seed evaluation (e.g., seeds 42/123/999) and report mean ± std with significance tests",
    "Unfreeze UAV and satellite backbone upper layers with larger GPU resources",
    "Add domain-generalization experiments across geographies and crop species",
    "Integrate temporal satellite sequences (ConvLSTM) for disease progression modeling",
    "Dedicated ablation to isolate cross-scale consistency regulariser contribution"
  ];

  // Left: limitations
  const LX = PAD, LW = 4.8;
  s.addText("Current Limitations", {
    x: LX, y: 0.7, w: LW, h: 0.3,
    fontSize: 12, fontFace: FONT, color: BLACK, bold: true
  });
  limits.forEach((l, i) => {
    const ly = 1.05 + i * 0.73;
    s.addText(l[0], {
      x: LX, y: ly, w: LW, h: 0.26,
      fontSize: 10, fontFace: FONT, color: BLACK, bold: true
    });
    s.addText(l[1], {
      x: LX, y: ly + 0.26, w: LW, h: 0.42,
      fontSize: 8.5, fontFace: FONT, color: GRAY, wrap: true
    });
  });

  // Right: future work
  const RX = 5.4, RW = W - RX - PAD;
  s.addText("Future Directions", {
    x: RX, y: 0.7, w: RW, h: 0.3,
    fontSize: 12, fontFace: FONT, color: BLACK, bold: true
  });
  future.forEach((f, i) => {
    s.addText([{ text: f, options: { bullet: true } }], {
      x: RX, y: 1.05 + i * 0.57, w: RW, h: 0.52,
      fontSize: 9.5, fontFace: FONT, color: GRAY
    });
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 14 – Conclusion
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  slideTitle(s, "Conclusion");

  const conclusions = [
    ["1", "Architecture", "Proposed MultiScaleCropNet — a modular hierarchical fusion framework integrating EfficientNet-B0 (leaf, partially fine-tuned) and ResNet50 × 2 (UAV & satellite, fully frozen) with four configurable fusion strategies for three-class crop health classification."],
    ["2", "NDVI Satellite Labeling", "Replaced photometric proxy generation with NDVI-based percentile partitioning on EuroSATallBands Sentinel-2 TIFFs (B08/B04), providing a physically grounded health-state proxy for satellite tiles."],
    ["3", "Ablation Study", "Conducted a complete 10-configuration ablation (3 single, 3 dual, 4 full-fusion variants) under identical hyperparameters with strict pre-triplet 70/15/15 split isolation on a balanced 804-sample test set."],
    ["4", "Best Result", "Full Fusion (Scalar-Weighted) achieves 95.77% accuracy and F1-macro 0.9578 — scalar weighting outperforms equal concatenation by learning to down-weight the noisy NDVI satellite proxy signal."],
    ["5", "Key Finding", "Equal-weight full fusion (F1 0.9494) numerically matches UAV+Leaf (F1 0.9493) — satellite adds no gain without learned modality weighting. Learned gating collapses (F1 0.7536). Attention fusion close to best (F1 0.9509)."]
  ];

  conclusions.forEach((c, i) => {
    const cy = 0.72 + i * 0.85;
    // Number
    box(s, PAD, cy + 0.1, 0.5, 0.5, { fill: BLACK, border: BLACK });
    s.addText(c[0], {
      x: PAD, y: cy + 0.1, w: 0.5, h: 0.5,
      fontSize: 13, fontFace: FONT, color: WHITE, bold: true, align: "center", valign: "middle"
    });
    s.addText(c[1], {
      x: PAD + 0.62, y: cy + 0.08, w: W - PAD * 2 - 0.62, h: 0.28,
      fontSize: 11, fontFace: FONT, color: BLACK, bold: true
    });
    s.addText(c[2], {
      x: PAD + 0.62, y: cy + 0.35, w: W - PAD * 2 - 0.62, h: 0.42,
      fontSize: 9.5, fontFace: FONT, color: GRAY, wrap: true
    });
    if (i < conclusions.length - 1) hRule(s, cy + 0.83);
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 15 – References
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  slideTitle(s, "References");

  const refs = [
    "[1]  Food and Agriculture Organization, \"The State of Food and Agriculture 2019,\" FAO, Rome, 2019.",
    "[2]  D. P. Hughes and M. Salathe, \"An open access repository of images on plant health,\" arXiv:1511.08060, 2015.",
    "[3]  S. P. Mohanty et al., \"Using deep learning for image-based plant disease detection,\" Front. Plant Sci., vol. 7, p. 1419, 2016.",
    "[4]  K. He et al., \"Deep residual learning for image recognition,\" in Proc. IEEE CVPR, 2016, pp. 770–778.",
    "[5]  M. Tan and Q. V. Le, \"EfficientNet: Rethinking model scaling for CNNs,\" in Proc. ICML, 2019, pp. 6105–6114.",
    "[6]  Y. Toda and F. Okura, \"How CNNs diagnose plant disease,\" Plant Phenomics, 2019.",
    "[7]  J. Albetis et al., \"Detection of Flavescence doree using UAV multispectral imagery,\" Remote Sensing, vol. 9, p. 308, 2017.",
    "[8]  P. Helber et al., \"EuroSAT: A novel dataset and DL benchmark for land use classification,\" IEEE JSTARS, vol. 12, pp. 2217–2226, 2019.",
    "[9]  M. Schmitt and X. X. Zhu, \"Data fusion and remote sensing,\" IEEE GRSM, vol. 4, pp. 6–23, 2016.",
    "[10]  Y. Chen et al., \"Deep fusion of remote sensing data,\" IEEE GRSL, vol. 14, pp. 1253–1257, 2017.",
    "[11]  S. Shinde et al., \"MH-SoyaHealthVision: An Indian UAV and leaf image dataset,\" Data in Brief, vol. 53, p. 110177, 2023.",
    "[12]  I. Loshchilov and F. Hutter, \"Decoupled weight decay regularization,\" in Proc. ICLR, 2019.",
    "[13]  P. S. Thakur et al., \"Vision transformer meets CNN for plant disease classification,\" Ecol. Inform., vol. 77, 2023.",
    "[14]  M. Kerkech et al., \"Deep learning for vineyard detection from UAV-based monitoring,\" Comput. Electron. Agric., vol. 155, 2018.",
    "[15]  J. W. Rouse Jr. et al., \"Monitoring vegetation systems with ERTS,\" in Proc. Third ERTS Symposium, vol. 1, 1974.",
    "[16]  N. Kussul et al., \"DL classification of land cover using remote sensing data,\" IEEE GRSL, vol. 14, pp. 778–782, 2017.",
    "[17]  T. Zhang et al., \"Multiscale CNN-SSM with feature fusion for UAV crop disease detection,\" Front. Plant Sci., 2025."
  ];

  // Two columns
  const half = Math.ceil(refs.length / 2);
  const col1 = refs.slice(0, half);
  const col2 = refs.slice(half);
  const colW = (W - PAD * 2 - 0.2) / 2;
  const RH = (H - 0.72 - 0.38) / half;

  col1.forEach((r, i) => {
    s.addText(r, {
      x: PAD, y: 0.68 + i * RH, w: colW, h: RH,
      fontSize: 7.8, fontFace: FONT, color: GRAY, wrap: true, valign: "top"
    });
  });
  col2.forEach((r, i) => {
    s.addText(r, {
      x: PAD + colW + 0.2, y: 0.68 + i * RH, w: colW, h: RH,
      fontSize: 7.8, fontFace: FONT, color: GRAY, wrap: true, valign: "top"
    });
  });
}

pres.writeFile({ fileName: "MultiScaleCropNet_FirstReview_Updated.pptx" })
  .then(() => console.log("Done: MultiScaleCropNet_FirstReview_Updated.pptx"))
  .catch(err => console.error(err));