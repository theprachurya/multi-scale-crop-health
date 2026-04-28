import os

def find():
    for root, dirs, files in os.walk(r'C:\Users\zen\Desktop'):
        if 'venv' in root or '.git' in root:
            continue
        for f in files:
            if f.endswith('.zip') and any(k in f.lower() for k in ['eurosat', 'plant', 'soya']):
                print(os.path.join(root, f))

find()
