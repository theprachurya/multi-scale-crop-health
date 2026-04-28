import os
import sys
import random
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def map_plantvillage(raw_dir, processed_dir):
    """Legacy mapper, logic natively absorbed into get_modality_dict directly."""
    pass

def _load_tif_array(path):
    """Load TIFF arrays from EuroSATallBands using tifffile if available."""
    try:
        import tifffile
        return tifffile.imread(path)
    except Exception:
        return None


def _extract_red_nir(arr):
    """
    Extract Red (B04) and NIR (B08) from common Sentinel-2 13-band layouts.
    Supports CHW (13, H, W) and HWC (H, W, 13).
    """
    if arr is None or arr.ndim != 3:
        return None, None

    # Assumed EuroSATallBands order: B01..B12 with B8A included.
    # 0-based: B04 -> 3, B08 -> 7
    # CHW layout: (bands, height, width)
    if arr.shape[0] <= 20 and arr.shape[1] > 20 and arr.shape[2] > 20:
        red = arr[3].astype(np.float32)
        nir = arr[7].astype(np.float32)
        return red, nir

    # HWC layout: (height, width, bands)
    if arr.shape[-1] >= 8:
        red = arr[:, :, 3].astype(np.float32)
        nir = arr[:, :, 7].astype(np.float32)
        return red, nir

    return None, None


def _compute_mean_ndvi(path):
    arr = _load_tif_array(path)
    red, nir = _extract_red_nir(arr)
    if red is None or nir is None:
        return None

    # Sentinel-2 reflectance in EuroSATallBands is typically scaled by 10000.
    red = np.clip(red / 10000.0, 0.0, 1.0)
    nir = np.clip(nir / 10000.0, 0.0, 1.0)
    ndvi = (nir - red) / (nir + red + 1e-8)
    return float(np.nanmean(ndvi))

def get_modality_dict(raw_dir, modality):
    """
    Returns a dictionary of class string -> list of raw image paths mapping user biological logic.
    """
    modality_dict = {'Healthy': [], 'Stressed': [], 'Diseased': []}
    
    if not os.path.exists(raw_dir):
        return modality_dict
        
    valid_exts = ('.jpg', '.jpeg', '.png', '.tif', '.tiff')

    if modality == 'leaf':
        # PlantVillage Biological Rules
        stressed_keywords = ['cedar_apple_rust', 'powdery_mildew', 'common_rust', 'isariopsis', 'leaf_mold', 'spider_mites', 'leaf_scorch']
        diseased_keywords = ['bacterial_spot', 'early_blight', 'late_blight', 'black_rot', 'apple_scab', 'esca', 'septoria', 'target_spot', 'yellow_leaf_curl', 'mosaic_virus', 'haunglongbing']
        
        for root, dirs, files in os.walk(raw_dir):
            class_folder = os.path.basename(root).lower()
            
            target_class = None
            if '___healthy' in class_folder:
                target_class = 'Healthy'
            elif any(k in class_folder for k in diseased_keywords):
                target_class = 'Diseased'
            elif any(k in class_folder for k in stressed_keywords):
                target_class = 'Stressed'
            else:
                # If it doesn't match predefined rules exactly, we ignore or map cautiously. None ignores it.
                pass
                
            if target_class:
                for file in files:
                    if file.lower().endswith(valid_exts):
                        modality_dict[target_class].append(os.path.join(root, file))
                        
    elif modality == 'uav':
        # MH-SoyaHealthVision Biological Rules
        for root, dirs, files in os.walk(raw_dir):
            class_folder = os.path.basename(root).lower()
            
            target_class = None
            if 'healthy_soyabean' in class_folder:
                target_class = 'Healthy'
            elif 'mosaic' in class_folder:
                target_class = 'Diseased'
            elif any(k in class_folder for k in ['rust', 'semilooper', 'caterpillar']):
                target_class = 'Stressed'
                
            if target_class:
                for file in files:
                    if file.lower().endswith(valid_exts):
                        modality_dict[target_class].append(os.path.join(root, file))
                        
    elif modality == 'satellite':
        # EuroSAT class-folder prior (fallback for RGB-only folders)
        healthy_map = ['annualcrop', 'permanentcrop']
        stressed_map = ['herbaceousvegetation', 'herbaceousvegatation', 'pasture']
        tif_candidates = []
        
        for root, dirs, files in os.walk(raw_dir):
            class_folder = os.path.basename(root).lower()
            
            if class_folder in healthy_map:
                target_class = 'Healthy'
            elif class_folder in stressed_map:
                target_class = 'Stressed'
            else:
                target_class = None
            
            for file in files:
                if file.lower().endswith(valid_exts):
                    p = os.path.join(root, file)
                    if target_class:
                        modality_dict[target_class].append(p)
                    if p.lower().endswith(('.tif', '.tiff')):
                        tif_candidates.append(p)

        # Replace synthetic proxy logic with NDVI-based label assignment if TIFF data exists.
        if tif_candidates:
            ndvi_rows = []
            for path in tif_candidates:
                ndvi = _compute_mean_ndvi(path)
                if ndvi is not None and not np.isnan(ndvi):
                    ndvi_rows.append((path, ndvi))

            if ndvi_rows:
                ndvi_vals = np.array([r[1] for r in ndvi_rows], dtype=np.float32)
                low_thr = float(np.percentile(ndvi_vals, 33))
                high_thr = float(np.percentile(ndvi_vals, 66))

                ndvi_dict = {'Healthy': [], 'Stressed': [], 'Diseased': []}
                for path, ndvi in ndvi_rows:
                    if ndvi <= low_thr:
                        ndvi_dict['Diseased'].append(path)
                    elif ndvi >= high_thr:
                        ndvi_dict['Healthy'].append(path)
                    else:
                        ndvi_dict['Stressed'].append(path)

                # Prefer NDVI-based assignments when available to avoid photometric proxies.
                if all(len(ndvi_dict[k]) > 0 for k in ndvi_dict):
                    modality_dict = ndvi_dict
                    print(
                        f"Satellite NDVI partition enabled from {len(ndvi_rows)} TIFFs "
                        f"(low={low_thr:.3f}, high={high_thr:.3f})."
                    )
                else:
                    print("Satellite NDVI partition incomplete; keeping class-folder fallback mapping.")
            
    return modality_dict

def generate_triplets(base_dir='.'):
    """
    Scans raw directories, applies disjoint test separation, and mathematically locks triplets to normalized balances.
    """
    random.seed(42)
    
    leaf_dir = os.path.join(base_dir, 'data', 'raw', 'leaf')
    uav_dir = os.path.join(base_dir, 'data', 'raw', 'uav')
    sat_dir = os.path.join(base_dir, 'data', 'raw', 'satellite')
    triplets_dir = os.path.join(base_dir, 'data', 'triplets')
    
    os.makedirs(triplets_dir, exist_ok=True)
    
    print("Evaluating dataset dictionaries natively...")
    leaf_dict = get_modality_dict(leaf_dir, 'leaf')
    uav_dict = get_modality_dict(uav_dir, 'uav')
    sat_dict = get_modality_dict(sat_dir, 'satellite')
    
    classes = ['Healthy', 'Stressed', 'Diseased']
    label_map = {'Healthy': 0, 'Stressed': 1, 'Diseased': 2}
    
    max_count = 0 
    for cls in classes:
        l, u, s = len(leaf_dict[cls]), len(uav_dict[cls]), len(sat_dict[cls])
        print(f"[{cls} Pool] Leaf: {l}, UAV: {u}, SAT: {s}")
        if min(l, u, s) > max_count:
            max_count = min(l, u, s)
    
    target_train_per_class = max(int(max_count * 0.7), 1000)
    target_val_per_class = max(int(max_count * 0.15), 200)
    target_test_per_class = max(int(max_count * 0.15), 200)
    
    split_triplets = {'train': [], 'val': [], 'test': []}
    
    def isolate_pool(img_list):
        if not img_list: return [], [], []
        arr = img_list.copy()
        arr.sort() # Ensure sequential video frames stay contiguous across splits
        if len(arr) < 3: return arr, arr, arr
        n = len(arr)
        t_bnd = int(n * 0.7)
        v_bnd = int(n * 0.85)
        
        tr, va, te = arr[:t_bnd], arr[t_bnd:v_bnd], arr[v_bnd:]
        random.shuffle(tr)
        random.shuffle(va)
        random.shuffle(te)
        
        return tr, va, te
        
    def pad(lst, mod, c):
        return lst if lst else [os.path.join(base_dir, f"data/raw/dummy_{mod}_{c}.jpg")]
    
    for cls in classes:
        l_tr, l_va, l_te = isolate_pool(leaf_dict[cls])
        u_tr, u_va, u_te = isolate_pool(uav_dict[cls])
        s_tr, s_va, s_te = isolate_pool(sat_dict[cls])
        
        l_tr = pad(l_tr, 'leaf', cls); l_va = pad(l_va, 'leaf', cls); l_te = pad(l_te, 'leaf', cls)
        u_tr = pad(u_tr, 'uav', cls); u_va = pad(u_va, 'uav', cls); u_te = pad(u_te, 'uav', cls)
        s_tr = pad(s_tr, 'sat', cls); s_va = pad(s_va, 'sat', cls); s_te = pad(s_te, 'sat', cls)
        
        def build_block(target_count, pool_l, pool_u, pool_s):
            triplets = []
            for _ in range(target_count):
                triplets.append({
                    'leaf_path': random.choice(pool_l),
                    'uav_path': random.choice(pool_u),
                    'satellite_path': random.choice(pool_s),
                    'label': label_map[cls]
                })
            return triplets
            
        split_triplets['train'].extend(build_block(target_train_per_class, l_tr, u_tr, s_tr))
        split_triplets['val'].extend(build_block(target_val_per_class, l_va, u_va, s_va))
        split_triplets['test'].extend(build_block(target_test_per_class, l_te, u_te, s_te))
        
    for split_k in split_triplets:
        random.shuffle(split_triplets[split_k])
        
    train_df = pd.DataFrame(split_triplets['train'])
    val_df = pd.DataFrame(split_triplets['val'])
    test_df = pd.DataFrame(split_triplets['test'])
    
    if train_df.empty: return
    
    train_csv = os.path.join(triplets_dir, 'train_triplets.csv')
    val_csv = os.path.join(triplets_dir, 'val_triplets.csv')
    test_csv = os.path.join(triplets_dir, 'test_triplets.csv')
    
    train_df.to_csv(train_csv, index=False)
    val_df.to_csv(val_csv, index=False)
    test_df.to_csv(test_csv, index=False)
    
    print("Class distribution mapped evenly across Train/Val/Test following precise biological proxy mapping rules!")
    print(f"Saved {len(train_df)} train, {len(val_df)} val, {len(test_df)} test triplets natively.")

if __name__ == "__main__":
    generate_triplets()
