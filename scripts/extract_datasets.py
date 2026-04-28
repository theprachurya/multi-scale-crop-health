import os
import zipfile
import shutil
import tempfile
import sys

def extract_zip(zip_path, extract_to, desc="Extracting"):
    print(f"\n[{desc}] Extracting {zip_path} to {extract_to}...")
    if not os.path.exists(zip_path):
        print(f"ERROR: File not found: {zip_path}")
        return False
        
    os.makedirs(extract_to, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(extract_to)
        print(f"[{desc}] Successfully extracted {zip_path}")
        return True
    except Exception as e:
        print(f"[{desc}] ERROR extracting {zip_path}: {e}")
        return False

def extract_mhsoyahealthvision(zip_path, extract_to, temp_dir):
    print(f"\n[Soya UAV] Scanning {zip_path} for UAV nested zips...")
    if not os.path.exists(zip_path):
        print(f"ERROR: File not found: {zip_path}")
        return False
        
    os.makedirs(extract_to, exist_ok=True)
    target_pattern = "Soyabean_UAV-Based_Image_Dataset"
    internal_zips_found = []
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for file_info in zf.infolist():
                if target_pattern in file_info.filename and file_info.filename.endswith('.zip'):
                    internal_zips_found.append(file_info.filename)
            
            if not internal_zips_found:
                print(f"[Soya UAV] No UAV internal zips found in {zip_path} matching pattern '{target_pattern}'. Check the zip structure.")
                return False
                
            print(f"[Soya UAV] Found {len(internal_zips_found)} UAV nested zips. Beginning extraction to temp...")
            
            for index, izip_name in enumerate(internal_zips_found, 1):
                temp_izip_path = os.path.join(temp_dir, os.path.basename(izip_name))
                print(f"  ({index}/{len(internal_zips_found)}) Extracting {izip_name} from parent archive...")
                
                # Extract the internal zip
                with zf.open(izip_name) as source, open(temp_izip_path, 'wb') as target:
                    shutil.copyfileobj(source, target)
                
                # Unzip the internal zip
                print(f"  ({index}/{len(internal_zips_found)}) Unpacking {temp_izip_path} to {extract_to}...")
                with zipfile.ZipFile(temp_izip_path, 'r') as izf:
                    izf.extractall(extract_to)
                    
                # Clean up extracted temp zip file
                os.remove(temp_izip_path)
                
        print(f"[Soya UAV] Successfully processed all UAV nested zips.")
        return True
        
    except Exception as e:
        print(f"[Soya UAV] ERROR processing {zip_path}: {e}")
        return False

def main():
    # Paths are relative to standard run from multi-scale-crop-health/
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    minor_project_root = os.path.abspath(os.path.join(project_root, '..'))
    
    eurosat_zip = os.path.join(project_root, 'eurosat.zip')
    plantv_zip = os.path.join(project_root, 'plantvillage.zip')
    mhsoya_zip = os.path.join(project_root, 'mhsoyahealthvision.zip')
    
    sat_dest = os.path.join(project_root, 'data', 'raw', 'satellite')
    leaf_dest = os.path.join(project_root, 'data', 'raw', 'leaf')
    uav_dest = os.path.join(project_root, 'data', 'raw', 'uav')
    
    print("starting extraction pipeline...")
    
    # 1. Extract EuroSAT
    extract_zip(eurosat_zip, sat_dest, desc="Satellite")
    
    # 2. Extract PlantVillage
    extract_zip(plantv_zip, leaf_dest, desc="Leaf")
    
    # 3. Extract MH-Soya UAV
    temp_dir = os.path.join(project_root, 'data', 'raw', 'temp_extract')
    os.makedirs(temp_dir, exist_ok=True)
    extract_mhsoyahealthvision(mhsoya_zip, uav_dest, temp_dir)
    
    # Clean temp immediately
    try:
        shutil.rmtree(temp_dir)
    except Exception:
        pass
        
    print("\nExtraction script completed. Ready for 'python preprocessing/align_datasets.py'")

if __name__ == '__main__':
    main()
