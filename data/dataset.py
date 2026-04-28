import os
import pandas as pd
from PIL import Image
import torch
import torchvision.transforms as transforms
import numpy as np
from torch.utils.data import Dataset

def _tif_to_rgb(img_array):
    """Convert common 13-band Sentinel-2 TIFF layouts to RGB uint8."""
    if img_array.ndim != 3:
        return None

    # Assumed EuroSATallBands order B01..B12(+B8A)
    # RGB uses Red=B04 (idx 3), Green=B03 (idx 2), Blue=B02 (idx 1)
    # CHW layout: (bands, height, width)
    if img_array.shape[0] <= 20 and img_array.shape[1] > 20 and img_array.shape[2] > 20:
        red = img_array[3]
        green = img_array[2]
        blue = img_array[1]
        rgb = np.stack([red, green, blue], axis=-1)
    # HWC layout: (height, width, bands)
    elif img_array.shape[-1] >= 4:
        red = img_array[:, :, 3]
        green = img_array[:, :, 2]
        blue = img_array[:, :, 1]
        rgb = np.stack([red, green, blue], axis=-1)
    else:
        return None

    rgb = rgb.astype(np.float32)
    max_val = float(np.max(rgb))
    if max_val > 0:
        rgb = (rgb / max_val) * 255.0
    return np.clip(rgb, 0, 255).astype(np.uint8)


def load_image(img_path):
    if img_path.lower().endswith(('.tif', '.tiff')):
        import tifffile
        img_array = tifffile.imread(img_path)
        rgb = _tif_to_rgb(img_array)
        if rgb is not None:
            return Image.fromarray(rgb)
        return Image.open(img_path).convert('RGB')
    return Image.open(img_path).convert('RGB')

class CropTripletDataset(Dataset):
    """
    Loads (leaf, uav, satellite, label) triplets from CSV.
    Applies separate transforms per modality if needed.
    """
    def __init__(self, csv_path, leaf_transform=None, uav_transform=None, sat_transform=None, base_dir='.'):
        self.data_frame = pd.read_csv(csv_path)
        self.leaf_transform = leaf_transform
        self.uav_transform = uav_transform
        self.sat_transform = sat_transform
        self.base_dir = base_dir

    def __len__(self):
        return len(self.data_frame)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        row = self.data_frame.iloc[idx]
        leaf_path = os.path.join(self.base_dir, row['leaf_path'].replace('\\', '/'))
        uav_path = os.path.join(self.base_dir, row['uav_path'].replace('\\', '/'))
        sat_path = os.path.join(self.base_dir, row['satellite_path'].replace('\\', '/'))
        label = int(row['label'])

        leaf_img = load_image(leaf_path)
        uav_img = load_image(uav_path)
        sat_img = load_image(sat_path)

        if self.leaf_transform: leaf_img = self.leaf_transform(leaf_img)
        else: leaf_img = transforms.ToTensor()(leaf_img)
        if self.uav_transform: uav_img = self.uav_transform(uav_img)
        else: uav_img = transforms.ToTensor()(uav_img)
        if self.sat_transform: sat_img = self.sat_transform(sat_img)
        else: sat_img = transforms.ToTensor()(sat_img)

        return leaf_img, uav_img, sat_img, label

class SingleModalityDataset(Dataset):
    """Used for baseline experiments. Returns (image_tensor, label)."""
    def __init__(self, csv_path, modality: str, transform=None, base_dir='.'):
        self.data_frame = pd.read_csv(csv_path)
        self.modality = modality
        self.transform = transform
        self.base_dir = base_dir
        
        # Mapping from modality name to column in CSV
        self.col_map = {
            'leaf': 'leaf_path',
            'uav': 'uav_path',
            'satellite': 'satellite_path'
        }
        
        if modality not in self.col_map:
            raise ValueError(f"Invalid modality {modality}")

    def __len__(self):
        return len(self.data_frame)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        row = self.data_frame.iloc[idx]
        img_path = os.path.join(self.base_dir, row[self.col_map[self.modality]].replace('\\', '/'))
        label = int(row['label'])

        img = load_image(img_path)

        if self.transform:
            img = self.transform(img)
        else:
            img = transforms.ToTensor()(img)

        return img, label
