import os
import glob
import numpy as np
from PIL import Image

try:
    import tifffile
except ImportError:
    print("Please install tifffile: pip install tifffile")
    exit(1)

def convert_tifs_to_jpgs(satellite_dir):
    print(f"Scanning {satellite_dir} for .tif/.tiff files...")
    search_pattern = os.path.join(satellite_dir, '**', '*.[tT][iI][fF]*')
    tif_files = glob.glob(search_pattern, recursive=True)
    
    if not tif_files:
        print("No .tif files found!")
        return

    print(f"Found {len(tif_files)} TIF files. Converting to RGB JPG...")
    
    success_count = 0
    fail_count = 0
    
    for tif_path in tif_files:
        try:
            img_array = tifffile.imread(tif_path)
            
            # EuroSAT Sentinel-2 13-band uses bands index 3(R), 2(G), 1(B)
            if img_array.ndim == 3 and img_array.shape[2] >= 13:
                rgb = img_array[:, :, [3, 2, 1]]
                max_val = np.max(rgb)
                if max_val > 0:
                    rgb = (rgb / max_val * 255)
                rgb = np.clip(rgb, 0, 255).astype(np.uint8)
            else:
                # If not 13-band, just grab first 3 bands if possible, or fallback
                if img_array.ndim == 3 and img_array.shape[2] >= 3:
                    rgb = img_array[:, :, :3]
                    max_val = np.max(rgb)
                    if max_val > 0: rgb = (rgb / max_val * 255)
                    rgb = np.clip(rgb, 0, 255).astype(np.uint8)
                else:
                    # grayscale or other formats
                    rgb = np.clip(img_array / np.max(img_array) * 255, 0, 255).astype(np.uint8)
            
            jpg_path = os.path.splitext(tif_path)[0] + '.jpg'
            
            img = Image.fromarray(rgb)
            img = img.convert("RGB")
            img.save(jpg_path, 'JPEG', quality=90)
            
            # Remove the original TIF to save disk space
            os.remove(tif_path)
            success_count += 1
            
            if success_count % 5000 == 0:
                print(f"  Processed {success_count}/{len(tif_files)} files...")
                
        except Exception as e:
            print(f"Failed to convert {tif_path}: {e}")
            fail_count += 1

    print(f"Conversion complete! Converted: {success_count}, Failed: {fail_count}")

if __name__ == '__main__':
    # Assuming script runs from project root
    raw_sat_dir = os.path.join('data', 'raw', 'satellite')
    convert_tifs_to_jpgs(raw_sat_dir)
