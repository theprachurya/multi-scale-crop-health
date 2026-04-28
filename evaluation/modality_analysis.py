import numpy as np
import torch


def _build_model_kwargs(batch, active_modalities, device):
	leaf, uav, satellite, labels = batch
	kwargs = {}
	if 'leaf' in active_modalities:
		kwargs['leaf'] = leaf.to(device)
	if 'uav' in active_modalities:
		kwargs['uav'] = uav.to(device)
	if 'satellite' in active_modalities:
		kwargs['satellite'] = satellite.to(device)
	labels = labels.to(device)
	return kwargs, labels


@torch.no_grad()
def compute_modality_contributions(model, test_loader, active_modalities, device):
	"""
	Leave-one-modality-out confidence-drop analysis.
	Returns global and per-class contribution scores.
	"""
	model.eval()

	per_modality_scores = {mod: [] for mod in active_modalities}
	per_class_scores = {}

	for batch in test_loader:
		kwargs, labels = _build_model_kwargs(batch, active_modalities, device)

		full_logits = model(**kwargs)
		full_probs = torch.softmax(full_logits, dim=1)
		full_conf = full_probs.max(dim=1).values

		for mod in active_modalities:
			dropped_kwargs = dict(kwargs)
			dropped_kwargs[mod] = torch.zeros_like(dropped_kwargs[mod])
			dropped_logits = model(**dropped_kwargs)
			dropped_probs = torch.softmax(dropped_logits, dim=1)
			dropped_conf = dropped_probs.max(dim=1).values

			conf_drop = (full_conf - dropped_conf).detach().cpu().numpy()
			per_modality_scores[mod].extend(conf_drop.tolist())

			label_np = labels.detach().cpu().numpy()
			for i, class_id in enumerate(label_np):
				class_id = int(class_id)
				if class_id not in per_class_scores:
					per_class_scores[class_id] = {m: [] for m in active_modalities}
				per_class_scores[class_id][mod].append(float(conf_drop[i]))

	summary = {
		'global': {
			mod: {
				'mean_confidence_drop': float(np.mean(scores)) if scores else 0.0,
				'std_confidence_drop': float(np.std(scores)) if scores else 0.0,
			}
			for mod, scores in per_modality_scores.items()
		},
		'per_class': {
			str(class_id): {
				mod: float(np.mean(scores)) if scores else 0.0
				for mod, scores in mod_scores.items()
			}
			for class_id, mod_scores in per_class_scores.items()
		},
	}

	return summary


@torch.no_grad()
def summarize_fusion_weights(model, test_loader, active_modalities, device):
	"""
	Aggregates fusion module weights if supported by current fusion method.
	"""
	if not hasattr(model, 'get_last_fusion_weights'):
		return {}

	model.eval()
	all_weights = []

	for batch in test_loader:
		kwargs, _ = _build_model_kwargs(batch, active_modalities, device)
		_ = model(**kwargs)
		weights = model.get_last_fusion_weights()
		if weights is None:
			continue

		# AttentionFusion stores [B, M, M]. Convert to modality importance [B, M].
		if weights.dim() == 3:
			weights = weights.mean(dim=1)

		all_weights.append(weights.detach().cpu())

	if not all_weights:
		return {}

	stacked = torch.cat(all_weights, dim=0).numpy()
	result = {}
	for idx, mod in enumerate(active_modalities):
		result[mod] = {
			'mean_weight': float(np.mean(stacked[:, idx])),
			'std_weight': float(np.std(stacked[:, idx])),
		}

	return result
