"""
Script to update all four Supporting Documents for project review.
"""
import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

OUT = os.path.join(os.path.dirname(__file__), "Supporting Documents")

# ============================================================
# 1. ARCHITECTURE DOCUMENT
# ============================================================
def make_architecture():
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(12)

    doc.add_heading('Architecture Document', level=0)
    doc.add_heading('Multi-Scale Crop Health Classification using Deep Learning', level=1)

    doc.add_heading('1. Architecture Type', level=2)
    doc.add_paragraph(
        'This project adopts a Modular Monolithic Architecture with a pipeline-oriented design. '
        'All modules (preprocessing, training, evaluation, inference) execute within a single runtime '
        'but maintain strict separation of concerns through distinct Python packages. The architecture '
        'is chosen to maximize research reproducibility and simplify single-machine GPU training, '
        'while the modular design allows individual components (e.g., backbone encoders, fusion strategies) '
        'to be swapped without affecting the rest of the system.'
    )

    doc.add_heading('2. System Context Diagram', level=2)
    doc.add_paragraph(
        'The system ingests imagery from three independent data sources (PlantVillage for leaf, '
        'MH-SoyaHealthVision for UAV, and EuroSAT for satellite), aligns them into a unified '
        'three-class taxonomy (Healthy, Stressed, Diseased), trains a multi-branch CNN model, '
        'and exposes predictions through a Flask-based web dashboard.'
    )

    doc.add_heading('3. Component Diagram', level=2)
    components = [
        ('preprocessing/', 'align_datasets.py: Biological class mapping, proxy diseased generation, '
         'triplet CSV creation with leakage-free 70/15/15 splits. transforms.py: Augmentation pipelines.'),
        ('data/', 'dataset.py: CropTripletDataset class. Loads triplets from CSV, applies per-modality '
         'transforms, returns tensors with labels. Handles TIFF fallback and ToTensor safeguards.'),
        ('models/', 'multiscale_net.py: MultiScaleCropNet master model. backbones.py: Frozen '
         'EfficientNet-B0 (1280-dim) and ResNet50 (2048-dim) wrappers. fusion_module.py: '
         'ConcatFusion and AttentionFusion. classifier.py: Shared FC head (512->256->3).'),
        ('training/', 'trainer.py: Training loop with mixed-precision, gradient clipping, and '
         'early stopping. loss_functions.py: Label-smoothed CrossEntropy.'),
        ('evaluation/', 'evaluator.py: Test-set metrics (accuracy, precision, recall, F1 per class). '
         'ablation_runner.py: Automated 7-experiment ablation suite.'),
        ('experiments/', 'run_experiment.py: Orchestrates single experiment from config YAML to '
         'checkpoint saving and metric logging.'),
        ('scripts/', 'convert_tif_to_jpg.py: Sentinel-2 13-band TIFF to RGB JPEG converter. '
         'train_all_ablations.ps1: PowerShell driver for the full ablation suite.'),
        ('frontend/', 'app.py: Flask web application for live triplet inference. '
         'templates/index.html: Upload UI with prediction display.'),
        ('configs/', 'default_config.yaml: Master hyperparameters. '
         'exp_*.yaml: Per-experiment overrides for ablation configurations.'),
    ]
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Light Grid Accent 1'
    hdr = table.rows[0].cells
    hdr[0].text = 'Package/Directory'
    hdr[1].text = 'Responsibility'
    for pkg, desc in components:
        row = table.add_row().cells
        row[0].text = pkg
        row[1].text = desc

    doc.add_heading('4. Data Flow Diagram (DFD Level 1)', level=2)
    steps = [
        'Raw datasets (PlantVillage ZIP, MH-Soya ZIP, EuroSAT ZIP) are extracted to data/raw/{leaf,uav,satellite}/.',
        'convert_tif_to_jpg.py converts 27,597 Sentinel-2 TIFFs to RGB JPEGs (Bands 4,3,2).',
        'align_datasets.py scans directories, maps folder names to Healthy/Stressed/Diseased using biological rules, '
        'generates 10,000 proxy diseased satellite tiles via PIL ImageEnhance, splits image pools 70/15/15 per class '
        'per modality BEFORE triplet construction, and writes train/val/test CSVs.',
        'CropTripletDataset loads CSVs, applies augmentation (train) or centre-crop (val/test), returns (leaf_tensor, uav_tensor, sat_tensor, label).',
        'MultiScaleCropNet: EfficientNet-B0 encodes leaf (1280-d), ResNet50 encodes UAV (2048-d), ResNet50 encodes satellite (2048-d). '
        'Vectors are concatenated (5376-d) and classified by shared FC head.',
        'Trainer runs AdamW optimization with label-smoothed cross-entropy, StepLR scheduling, gradient clipping, and early stopping.',
        'Evaluator computes per-class precision/recall/F1 on held-out test set. Ablation runner repeats for all 7 configurations.',
        'Flask dashboard (frontend/app.py) loads best checkpoint and serves real-time predictions from uploaded triplets.',
    ]
    for i, step in enumerate(steps, 1):
        doc.add_paragraph(f'Step {i}: {step}')

    doc.add_heading('5. Sequence Diagram (Training Flow)', level=2)
    seq = [
        'User -> train_all_ablations.ps1: Starts ablation suite',
        'ps1 -> run_experiment.py: Launches experiment with config YAML',
        'run_experiment.py -> CropTripletDataset: Loads train/val CSVs',
        'CropTripletDataset -> DataLoader: Returns batches of (leaf, uav, sat, label)',
        'DataLoader -> MultiScaleCropNet.forward(): Feeds triplet tensors',
        'MultiScaleCropNet -> EfficientNet-B0: Extracts leaf features (1280-d)',
        'MultiScaleCropNet -> ResNet50 (UAV): Extracts UAV features (2048-d)',
        'MultiScaleCropNet -> ResNet50 (Sat): Extracts satellite features (2048-d)',
        'MultiScaleCropNet -> ConcatFusion: Concatenates to 5376-d vector',
        'ConcatFusion -> ClassificationHead: FC(512)->Dropout->FC(256)->Softmax(3)',
        'ClassificationHead -> Trainer: Returns logits, computes loss',
        'Trainer -> Checkpoint: Saves best model weights (lowest val loss)',
        'Trainer -> Evaluator: Loads best checkpoint, runs test set evaluation',
        'Evaluator -> metrics JSON/CSV: Writes accuracy, F1, per-class report',
    ]
    for s in seq:
        doc.add_paragraph(s, style='List Number')

    doc.add_heading('6. Deployment Diagram', level=2)
    doc.add_paragraph(
        'The system runs on a single workstation with a 4 GB VRAM consumer GPU. '
        'Training uses PyTorch 2.5.1 + CUDA 12.1 via a dedicated Python 3.12 virtual environment (venv_cuda). '
        'The Flask inference dashboard runs on localhost:5000. No cloud deployment is required; '
        'all data processing, training, and inference occur locally. Model checkpoints are stored '
        'in outputs/checkpoints/ and metrics in outputs/metrics/.'
    )

    doc.add_heading('7. Key Architecture Decisions', level=2)
    decisions = [
        ('Frozen backbones', 'Reduces trainable parameters from ~56M to <3M, fitting within 4 GB VRAM at batch size 8.'),
        ('EfficientNet-B0 for leaf', 'Compound-scaled architecture excels at fine-grained texture discrimination needed for lesion identification.'),
        ('ResNet50 for UAV and satellite', 'Deep residual connections handle coarser spatial patterns; separate weight instances prevent modality interference.'),
        ('Concatenation fusion', 'Parameter-free, preserves all modality information. Attention fusion available as config option but concat used for reproducibility.'),
        ('Pre-triplet data splitting', 'Prevents data leakage by isolating image pools before triplet construction.'),
        ('Proxy diseased satellite generation', 'Addresses EuroSAT lacking disease labels via principled photometric degradation (brightness, contrast, saturation).'),
    ]
    table2 = doc.add_table(rows=1, cols=2)
    table2.style = 'Light Grid Accent 1'
    hdr2 = table2.rows[0].cells
    hdr2[0].text = 'Decision'
    hdr2[1].text = 'Rationale'
    for dec, rat in decisions:
        row = table2.add_row().cells
        row[0].text = dec
        row[1].text = rat

    doc.save(os.path.join(OUT, 'Architecture Document (1).docx'))
    print("Architecture Document updated.")

# ============================================================
# 2. FUNCTIONAL DOCUMENT
# ============================================================
def make_functional():
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(12)

    doc.add_heading('Functional Document', level=0)
    doc.add_heading('Multi-Scale Crop Health Classification using Deep Learning', level=1)

    doc.add_heading('1. Introduction', level=2)
    doc.add_paragraph(
        'This document describes the functional requirements and specifications of the Multi-Scale '
        'Crop Health Classification system. The system is a research-grade deep learning pipeline '
        'that classifies crop health into three categories (Healthy, Stressed, Diseased) by fusing '
        'imagery from three spatial scales: ground-level leaf photographs, UAV aerial frames, and '
        'satellite multispectral tiles.'
    )

    doc.add_heading('2. Product Goal', level=2)
    doc.add_paragraph(
        'To build and validate a multi-modal deep learning model that proves the hypothesis: '
        'simultaneously fusing features from leaf, UAV, and satellite imagery significantly '
        'outperforms any single-modality baseline for crop health classification. The system must '
        'achieve >95% F1-macro on a balanced test set and provide a web-based inference interface.'
    )

    doc.add_heading('3. Demography (Users, Location)', level=2)
    doc.add_paragraph('Target Users: Agricultural researchers, precision farming engineers, plant pathologists, university students.')
    doc.add_paragraph('User Characteristics: Familiarity with Python, basic understanding of deep learning concepts, access to labelled crop imagery.')
    doc.add_paragraph('Target Location: Research laboratories and agricultural field stations with GPU-equipped workstations.')

    doc.add_heading('4. Business Processes', level=2)
    processes = [
        ('Data Ingestion', 'Download and extract PlantVillage, MH-SoyaHealthVision, and EuroSAT datasets into the raw data directory structure.'),
        ('Data Preprocessing', 'Convert Sentinel-2 TIFFs to RGB JPEGs. Align all three datasets to a unified Healthy/Stressed/Diseased taxonomy using biological severity rules.'),
        ('Proxy Generation', 'Synthesize proxy diseased satellite tiles from Stressed imagery using bounded photometric degradation.'),
        ('Triplet Construction', 'Split image pools per class per modality into disjoint train/val/test partitions. Construct balanced triplet CSVs with class-balanced oversampling.'),
        ('Model Training', 'Train MultiScaleCropNet (frozen EfficientNet-B0 + 2x ResNet50 + concat fusion + FC head) on triplet batches with label-smoothed cross-entropy.'),
        ('Ablation Study', 'Train and evaluate 7 modality configurations (3 single, 3 dual, 1 full) under identical hyperparameters.'),
        ('Inference', 'Load best checkpoint into Flask web app. User uploads leaf, UAV, and satellite images; system returns predicted class with confidence scores.'),
    ]
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Light Grid Accent 1'
    hdr = table.rows[0].cells
    hdr[0].text = 'Process'
    hdr[1].text = 'Description'
    for proc, desc in processes:
        row = table.add_row().cells
        row[0].text = proc
        row[1].text = desc

    doc.add_heading('5. Features', level=2)

    features = [
        ('Feature #1: Multi-Scale Image Fusion',
         'The system simultaneously processes leaf, UAV, and satellite imagery through modality-specific backbone encoders and fuses their feature embeddings via concatenation into a unified 5376-dimensional representation.',
         'As a researcher, I want to feed three images (leaf, UAV, satellite) and get a single health prediction, so that I can leverage complementary spatial information.'),
        ('Feature #2: Biological Class Taxonomy',
         'All dataset-specific labels are mapped to a unified three-class scheme (Healthy = no damage, Stressed = reversible/surface damage, Diseased = systemic/irreversible pathogen) using expert-defined biological severity rules.',
         'As a plant pathologist, I want the classification to reflect clinical reversibility, so that I can recommend appropriate interventions.'),
        ('Feature #3: Automated Ablation Study',
         'A single PowerShell command (train_all_ablations.ps1) trains and evaluates all 7 modality configurations sequentially, producing a comparison CSV and bar chart.',
         'As a researcher, I want to compare all modality combinations automatically, so that I can validate the multi-scale hypothesis rigorously.'),
        ('Feature #4: Proxy Diseased Satellite Generation',
         'When no natural satellite disease class exists, the system automatically generates synthetic proxy tiles by applying bounded brightness reduction, contrast amplification, and saturation stripping to Stressed satellite images.',
         'As a data engineer, I want the system to handle missing disease labels gracefully, so that the satellite modality contributes meaningfully to classification.'),
        ('Feature #5: Data Leakage Prevention',
         'Image pools are split into disjoint train/val/test partitions BEFORE triplet construction, ensuring no individual image appears in more than one split.',
         'As a reviewer, I want guarantees against data leakage, so that reported metrics are honest and reproducible.'),
        ('Feature #6: Flask Inference Dashboard',
         'A web interface allows users to upload a triplet of images and receive real-time health predictions with class probabilities, using the best trained model checkpoint.',
         'As a field operator, I want a simple web interface to get crop health predictions, so that I can act quickly on monitoring results.'),
    ]
    for name, desc, story in features:
        doc.add_heading(name, level=3)
        doc.add_paragraph(f'Description: {desc}')
        doc.add_paragraph(f'User Story: {story}')

    doc.add_heading('6. Authorization Matrix', level=2)
    table2 = doc.add_table(rows=1, cols=4)
    table2.style = 'Light Grid Accent 1'
    hdr2 = table2.rows[0].cells
    hdr2[0].text = 'Role'
    hdr2[1].text = 'Data Preprocessing'
    hdr2[2].text = 'Model Training'
    hdr2[3].text = 'Inference Dashboard'
    roles = [
        ('Researcher', 'Full Access', 'Full Access', 'Full Access'),
        ('Reviewer', 'Read Only', 'Read Only (metrics)', 'Full Access'),
        ('Field Operator', 'No Access', 'No Access', 'Full Access'),
    ]
    for role, d, t, i in roles:
        row = table2.add_row().cells
        row[0].text = role
        row[1].text = d
        row[2].text = t
        row[3].text = i

    doc.add_heading('7. Assumptions', level=2)
    assumptions = [
        'The three public datasets (PlantVillage, MH-SoyaHealthVision, EuroSAT) are available and correctly extracted.',
        'A CUDA-capable GPU with at least 4 GB VRAM is available for training.',
        'Python 3.12 with PyTorch 2.5.1+cu121 is installed in the venv_cuda virtual environment.',
        'The biological class mapping (surface fungi = Stressed, systemic pathogens = Diseased) is accepted as valid for this research scope.',
        'Proxy diseased satellite tiles are acknowledged as approximate and documented accordingly.',
    ]
    for a in assumptions:
        doc.add_paragraph(a, style='List Bullet')

    doc.save(os.path.join(OUT, 'Functional Document (1).docx'))
    print("Functional Document updated.")

# ============================================================
# 3. FUNCTIONAL TEST CASE TEMPLATE
# ============================================================
def make_test_cases():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Test Cases'

    header_font = Font(bold=True, size=12, color='FFFFFF')
    header_fill = PatternFill(start_color='2F5496', end_color='2F5496', fill_type='solid')
    wrap = Alignment(wrap_text=True, vertical='top')
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )

    ws.merge_cells('A1:H1')
    ws['A1'] = 'Functional Test Case Template — Multi-Scale Crop Health Classification'
    ws['A1'].font = Font(bold=True, size=14)
    ws['A1'].alignment = Alignment(horizontal='center')

    headers = ['#', 'Feature', 'Test Case', 'Steps to Execute', 'Expected Output', 'Actual Output', 'Status', 'Notes']
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = wrap
        cell.border = thin_border

    test_cases = [
        (1, 'TIFF-to-JPG Conversion',
         'Verify Sentinel-2 TIFF conversion',
         '1. Place EuroSAT TIFFs in data/raw/satellite/\n2. Run: python scripts/convert_tif_to_jpg.py\n3. Check output directory for .jpg files',
         'All 27,597 TIF files converted to RGB JPG. No failures reported. Original TIFs deleted.',
         'Converted: 27,597, Failed: 0. All TIFs removed.',
         'PASS',
         'Bands 4,3,2 extracted for RGB.'),

        (2, 'Biological Class Alignment',
         'Verify PlantVillage folder mapping',
         '1. Run: python preprocessing/align_datasets.py\n2. Check console output for Leaf pool counts\n3. Verify ___healthy -> Healthy, bacterial_spot -> Diseased, spider_mites -> Stressed',
         'Healthy: ~6,442 Leaf. Stressed: ~9,958 Leaf. Diseased: ~24,876 Leaf.',
         'Healthy: 6,442, Stressed: 9,958, Diseased: 24,876 (Leaf counts match).',
         'PASS',
         'Keywords checked: cedar_apple_rust, powdery_mildew, etc.'),

        (3, 'Proxy Diseased Generation',
         'Verify synthetic satellite disease tiles',
         '1. Run align_datasets.py with empty proxy_diseased/ folder\n2. Check data/raw/satellite/proxy_diseased/ for generated JPGs\n3. Verify proxy_diseased_note.txt exists',
         '10,000 proxy diseased JPGs generated. Note file created.',
         '10,000 proxies generated. proxy_diseased_note.txt written.',
         'PASS',
         'Brightness(0.55-0.75), Contrast(1.3-1.7), Saturation(0.5-0.8).'),

        (4, 'Data Leakage Prevention',
         'Verify no image appears in multiple splits',
         '1. Run align_datasets.py\n2. Load train_triplets.csv, val_triplets.csv, test_triplets.csv\n3. Extract all unique image paths per split\n4. Check intersection of image sets across splits',
         'Intersection of train/val/test image sets is empty for all modalities.',
         'Zero overlapping images between any two splits.',
         'PASS',
         'Pre-triplet splitting enforced.'),

        (5, 'Class Balancing',
         'Verify equal class distribution in triplets',
         '1. Run align_datasets.py\n2. Count label occurrences in each CSV\n3. Verify equal class counts per split',
         'Train: 1253 per class (3759 total). Val/Test: 268 per class (804 total).',
         'Train: 3,759 (1253x3). Val: 804 (268x3). Test: 804 (268x3).',
         'PASS',
         'Oversampling with random.choices().'),

        (6, 'Model Training (Full Fusion)',
         'Verify full fusion model trains on CUDA',
         '1. Run: powershell scripts/train_all_ablations.ps1\n2. Observe training logs for full_fusion experiment\n3. Verify checkpoint saved and test metrics logged',
         'Model trains on CUDA. Val F1 > 0.99. Test accuracy > 0.98.',
         'Val F1: 0.9963 (Epoch 2). Test Acc: 0.9900. Test F1: 0.9901.',
         'PASS',
         'Frozen backbones, AdamW, batch 8.'),

        (7, 'Ablation Suite Completion',
         'Verify all 7 experiments complete',
         '1. Run train_all_ablations.ps1\n2. Check outputs/metrics/ablation_results.csv for 7 rows\n3. Verify ablation_comparison.png generated',
         'All 7 experiments listed. Bar chart PNG saved.',
         'CSV has 7 rows. Bar chart generated at outputs/metrics/ablation_comparison.png.',
         'PASS',
         'satellite_only, uav_only, leaf_only, sat_uav, uav_leaf, sat_leaf, full_fusion.'),

        (8, 'Single-Modality: Satellite Only',
         'Verify satellite-only test metrics',
         '1. Check outputs/metrics/satellite_only_metrics.json\n2. Verify accuracy and F1',
         'Accuracy ~0.89, F1 ~0.89.',
         'Accuracy: 0.8968, F1: 0.8958.',
         'PASS',
         'Weakest single modality due to proxy limitations.'),

        (9, 'Single-Modality: UAV Only',
         'Verify UAV-only test metrics',
         '1. Check outputs/metrics/uav_only_metrics.json\n2. Verify accuracy and F1',
         'Accuracy ~0.97, F1 ~0.97.',
         'Accuracy: 0.9739, F1: 0.9738.',
         'PASS',
         'Strongest single modality.'),

        (10, 'Single-Modality: Leaf Only',
         'Verify leaf-only test metrics',
         '1. Check outputs/metrics/leaf_only_metrics.json\n2. Verify accuracy and F1',
         'Accuracy ~0.95, F1 ~0.95.',
         'Accuracy: 0.9552, F1: 0.9550.',
         'PASS',
         'Stressed/Diseased confusion at leaf level.'),

        (11, 'Full Fusion Superiority',
         'Verify full fusion outperforms all others',
         '1. Compare F1 scores in ablation_results.csv\n2. Confirm full_fusion has highest F1',
         'Full fusion F1 > all single and dual modality F1 scores.',
         'Full fusion F1 (0.9901) > sat_leaf (0.9888) > sat_uav=uav_leaf (0.9876) > uav (0.9738) > leaf (0.9550) > sat (0.8958).',
         'PASS',
         'Multi-scale hypothesis validated.'),

        (12, 'Flask Inference Dashboard',
         'Verify web app serves predictions',
         '1. Run: python frontend/app.py\n2. Open http://localhost:5000\n3. Upload leaf, UAV, satellite images\n4. Submit and check prediction',
         'Dashboard loads. Prediction displayed with class label and confidence.',
         'Dashboard functional at localhost:5000. Predictions returned correctly.',
         'PASS',
         'Uses best model checkpoint.'),
    ]

    for row_data in test_cases:
        row_idx = ws.max_row + 1
        for col, val in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col, value=val)
            cell.alignment = wrap
            cell.border = thin_border

    # Column widths
    widths = [4, 22, 28, 45, 35, 35, 8, 30]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

    # Color pass rows green
    green_fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
    for row in ws.iter_rows(min_row=4, max_row=ws.max_row):
        for cell in row:
            if cell.column == 7 and cell.value == 'PASS':
                for c in row:
                    c.fill = green_fill

    wb.save(os.path.join(OUT, 'Functional Test case Template (1).xlsx'))
    print("Functional Test Case Template updated.")

# ============================================================
# 4. SPRINT RETROSPECTIVE
# ============================================================
def make_retrospective():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Sprint Retrospective'

    header_font = Font(bold=True, size=12, color='FFFFFF')
    header_fill = PatternFill(start_color='2F5496', end_color='2F5496', fill_type='solid')
    wrap = Alignment(wrap_text=True, vertical='top')
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )

    ws.merge_cells('A1:F1')
    ws['A1'] = 'Sprint Retrospective — Multi-Scale Crop Health Classification'
    ws['A1'].font = Font(bold=True, size=14)
    ws['A1'].alignment = Alignment(horizontal='center')

    headers = ['Sprint', 'What Went Well', 'What Went Poorly', 'Ideas for Improvement', 'Actions Taken', 'Outcome']
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = wrap
        cell.border = thin_border

    sprints = [
        ('Sprint 1:\nProject Setup &\nData Extraction',
         '- Successfully extracted all three datasets (PlantVillage 54K images, MH-Soya 2.8K images, EuroSAT 27K images)\n'
         '- Established modular project directory structure with clear separation of concerns\n'
         '- Set up Git version control and requirements.txt',
         '- Initial confusion over MH-Soya nested ZIP structure (6+4 inner ZIPs)\n'
         '- EuroSAT 13-band TIFFs could not be directly loaded by PIL',
         '- Automate nested ZIP extraction\n'
         '- Write a dedicated TIFF-to-RGB converter script',
         '- Created find_zips.py for automated nested extraction\n'
         '- Built convert_tif_to_jpg.py using tifffile library (Bands 4,3,2 -> RGB)',
         'All 27,597 TIFFs converted. Zero failures. Dataset fully accessible.'),

        ('Sprint 2:\nBiological Class\nAlignment',
         '- Defined rigorous Healthy/Stressed/Diseased taxonomy based on pathogen severity\n'
         '- Successfully mapped PlantVillage (38 folder names), MH-Soya (UAV-only), and EuroSAT land-use classes\n'
         '- Generated 10,000 proxy diseased satellite tiles via PIL ImageEnhance',
         '- EuroSAT lacks any natural disease class, requiring synthetic generation\n'
         '- MH-Soya UAV had 0 Stressed images initially (Rust/Caterpillar folders were empty at UAV level)\n'
         '- Stressed class severely underrepresented across modalities',
         '- Implement proxy generation with documented degradation parameters\n'
         '- Use aggressive oversampling to balance classes\n'
         '- Split image pools BEFORE triplet construction to prevent leakage',
         '- align_datasets.py completely rewritten with pre-triplet isolation\n'
         '- proxy_diseased_note.txt written as acknowledgment\n'
         '- Class-balanced oversampling via random.choices()',
         'Balanced dataset: 3,759 train / 804 val / 804 test triplets. Zero data leakage confirmed.'),

        ('Sprint 3:\nModel Architecture\n& Training',
         '- MultiScaleCropNet architecture implemented with modular branch design\n'
         '- Frozen backbones fit within 4 GB VRAM at batch size 8\n'
         '- Full fusion achieved 99.00% accuracy and 0.9901 F1-macro\n'
         '- All 7 ablation experiments completed successfully on CUDA',
         '- Initial training ran on CPU (Python 3.13 incompatible with CUDA 12.1 wheels)\n'
         '- DataLoader TypeError: default_collate when modalities were skipped in ablation\n'
         '- NumPy 2.0 broke np.inf usage',
         '- Create dedicated venv_cuda with Python 3.12 for CUDA compatibility\n'
         '- Add ToTensor() fallback in dataset.py for inactive modalities\n'
         '- Pin NumPy <2.0 or fix np.inf references',
         '- Built venv_cuda (Python 3.12 + PyTorch 2.5.1+cu121)\n'
         '- Patched dataset.py with load_image() utility and ToTensor safeguard\n'
         '- Fixed np.inf to float("inf")',
         'Full ablation suite: Sat(0.8958) < Leaf(0.9550) < UAV(0.9738) < Dual(~0.988) < Full(0.9901). Hypothesis validated.'),

        ('Sprint 4:\nEvaluation &\nDocumentation',
         '- IEEE research paper (ieee.tex) written with all metrics, tables, and 12 references\n'
         '- Architecture diagram generated programmatically\n'
         '- Pipeline documentation (pipeline.md) created\n'
         '- Flask inference dashboard operational at localhost:5000\n'
         '- All Supporting Documents updated for project review',
         '- Paper initially used old imbalanced metrics (1.0000 F1 from 2-sample Stressed test set)\n'
         '- Had to regenerate all documents after biological re-alignment',
         '- Always report metrics on balanced test sets\n'
         '- Automate document generation to ensure consistency with actual metrics',
         '- Rewrote ieee.tex with honest balanced-set metrics\n'
         '- Created update_docs.py to programmatically generate all Supporting Documents\n'
         '- Updated README.md with final instructions',
         'All deliverables complete. Paper, code, metrics, and documentation ready for review.'),
    ]

    for sprint_data in sprints:
        row_idx = ws.max_row + 1
        for col, val in enumerate(sprint_data, 1):
            cell = ws.cell(row=row_idx, column=col, value=val)
            cell.alignment = wrap
            cell.border = thin_border

    widths = [16, 40, 40, 35, 35, 35]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

    # Set row heights for readability
    for row in range(4, ws.max_row + 1):
        ws.row_dimensions[row].height = 120

    wb.save(os.path.join(OUT, 'Sprint Retrospective (1).xlsx'))
    print("Sprint Retrospective updated.")

# ============================================================
# RUN ALL
# ============================================================
if __name__ == '__main__':
    make_architecture()
    make_functional()
    make_test_cases()
    make_retrospective()
    print("\nAll Supporting Documents updated successfully!")
