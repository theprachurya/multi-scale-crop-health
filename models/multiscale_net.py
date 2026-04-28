import torch
import torch.nn as nn
from models.backbones import ResNet50Backbone, EfficientNetB0Backbone
from models.fusion_module import ConcatFusion, AttentionFusion, LearnedGatingFusion, ScalarWeightedFusion
from models.classifier import ClassificationHead

class MultiScaleCropNet(nn.Module):
    """
    Master model. Configurable for ablation via active_modalities parameter.
    
    Args:
        active_modalities: list of str, subset of ['leaf', 'uav', 'satellite']
        freeze_backbones: bool, whether to freeze pretrained backbone layers
        dropout_rate: float
        num_classes: int
    """
    def __init__(self, active_modalities=['leaf', 'uav', 'satellite'], 
                 freeze_backbones=True, dropout_rate=0.5, num_classes=3,
                 fusion_method='concat', fusion_output_dim=512, fusion_hidden_dim=256):
        super().__init__()
        self.active_modalities = active_modalities
        self.fusion_method = fusion_method
        self.num_classes = num_classes
        
        input_dims = []
        
        # Instantiate requested branches
        if 'leaf' in self.active_modalities:
            self.leaf_branch = EfficientNetB0Backbone(pretrained=True, freeze_layers=freeze_backbones)
            self.leaf_out_dim = self.leaf_branch.out_dim
            input_dims.append(self.leaf_branch.out_dim)
            
        if 'uav' in self.active_modalities:
            self.uav_branch = ResNet50Backbone(pretrained=True, freeze_layers=freeze_backbones)
            self.uav_out_dim = self.uav_branch.out_dim
            input_dims.append(self.uav_branch.out_dim)
            
        if 'satellite' in self.active_modalities:
            self.satellite_branch = ResNet50Backbone(pretrained=True, freeze_layers=freeze_backbones)
            self.satellite_out_dim = self.satellite_branch.out_dim
            input_dims.append(self.satellite_branch.out_dim)
            
        # Fusion
        if fusion_method == 'concat':
            self.fusion = ConcatFusion(input_dims)
        elif fusion_method == 'attention':
            self.fusion = AttentionFusion(input_dims, embed_dim=fusion_output_dim)
        elif fusion_method in ['learned_gating', 'gated']:
            self.fusion = LearnedGatingFusion(
                input_dims,
                output_dim=fusion_output_dim,
                gate_hidden_dim=fusion_hidden_dim,
            )
        elif fusion_method in ['scalar_weighted', 'weighted']:
            self.fusion = ScalarWeightedFusion(input_dims, output_dim=fusion_output_dim)
        else:
            raise ValueError(
                f"Unsupported fusion_method '{fusion_method}'. "
                "Use one of: concat, attention, learned_gating, scalar_weighted"
            )
            
        # Classifier Head
        self.head = ClassificationHead(input_dim=self.fusion.output_dim, 
                                       num_classes=num_classes, 
                                       dropout_rate=dropout_rate)

        # Optional modality-specific auxiliary logits for consistency regularization.
        if 'leaf' in self.active_modalities:
            self.leaf_aux_head = nn.Linear(self.leaf_out_dim, num_classes)
        if 'uav' in self.active_modalities:
            self.uav_aux_head = nn.Linear(self.uav_out_dim, num_classes)
                                       
    def forward(self, leaf=None, uav=None, satellite=None, return_aux=False):
        features = []
        feature_map = {}
        
        if 'leaf' in self.active_modalities:
            if leaf is None:
                raise ValueError("Expected 'leaf' input for current modality configuration.")
            leaf_feat = self.leaf_branch(leaf)
            features.append(leaf_feat)
            feature_map['leaf'] = leaf_feat
            
        if 'uav' in self.active_modalities:
            if uav is None:
                raise ValueError("Expected 'uav' input for current modality configuration.")
            uav_feat = self.uav_branch(uav)
            features.append(uav_feat)
            feature_map['uav'] = uav_feat
            
        if 'satellite' in self.active_modalities:
            if satellite is None:
                raise ValueError("Expected 'satellite' input for current modality configuration.")
            sat_feat = self.satellite_branch(satellite)
            features.append(sat_feat)
            feature_map['satellite'] = sat_feat
            
        fused_features = self.fusion(features)
        logits = self.head(fused_features)

        if not return_aux:
            return logits

        aux = {}
        if 'leaf' in feature_map and hasattr(self, 'leaf_aux_head'):
            aux['leaf_logits'] = self.leaf_aux_head(feature_map['leaf'])
        if 'uav' in feature_map and hasattr(self, 'uav_aux_head'):
            aux['uav_logits'] = self.uav_aux_head(feature_map['uav'])
        return logits, aux

    def get_last_fusion_weights(self):
        if hasattr(self.fusion, 'get_last_weights'):
            return self.fusion.get_last_weights()
        return None
