from flask import Flask, request, jsonify, render_template
import torch
from torchvision import transforms
from PIL import Image
import io
import sys
import os

sys.path.append('..')
from models.multiscale_net import MultiScaleCropNet
from preprocessing.transforms import val_transform

app = Flask(__name__)

MODEL_PATH = '../outputs/checkpoints/best_full_fusion.pth'
model = None
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def load_model():
    global model
    print(f"Loading model on {device}...")
    model = MultiScaleCropNet(active_modalities=['leaf', 'uav', 'satellite'])
    if os.path.exists(MODEL_PATH):
        checkpoint = torch.load(MODEL_PATH, map_location=device)
        model.load_state_dict(checkpoint['state_dict'])
        print("Model loaded successfully.")
    else:
        print(f"Warning: Checkpoint not found at {MODEL_PATH}. Using untrained model (random predictions).")
    model.to(device)
    model.eval()

# Trigger model loading on first request or just before
with app.app_context():
    load_model()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if not model:
        return jsonify({'error': 'Model not loaded'}), 500
        
    try:
        if 'leaf' not in request.files or 'uav' not in request.files or 'satellite' not in request.files:
            return jsonify({'error': 'Please provide all 3 images (leaf, uav, satellite)'}), 400
            
        leaf_file = request.files['leaf']
        uav_file = request.files['uav']
        sat_file = request.files['satellite']
        
        leaf_img = Image.open(io.BytesIO(leaf_file.read())).convert('RGB')
        uav_img = Image.open(io.BytesIO(uav_file.read())).convert('RGB')
        sat_img = Image.open(io.BytesIO(sat_file.read())).convert('RGB')
        
        leaf_tensor = val_transform(leaf_img).unsqueeze(0).to(device)
        uav_tensor = val_transform(uav_img).unsqueeze(0).to(device)
        sat_tensor = val_transform(sat_img).unsqueeze(0).to(device)
        
        with torch.no_grad():
            outputs = model(leaf=leaf_tensor, uav=uav_tensor, satellite=sat_tensor)
            probs = torch.nn.functional.softmax(outputs, dim=1).squeeze().cpu().numpy()
            
        class_names = ['Healthy', 'Stressed', 'Diseased']
        pred_idx = probs.argmax()
        
        response = {
            'prediction': class_names[pred_idx],
            'confidence': float(probs[pred_idx] * 100),
            'probabilities': {
                'Healthy': float(probs[0]),
                'Stressed': float(probs[1]),
                'Diseased': float(probs[2])
            }
        }
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
