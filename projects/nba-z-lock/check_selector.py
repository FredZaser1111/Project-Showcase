import pickle
from pathlib import Path
import config

models_dir = Path(config.MODELS_DIR)
selector_file = models_dir / 'feature_selector.pkl'
feature_names_file = models_dir / 'feature_names.json'

if selector_file.exists():
    with open(selector_file, 'rb') as f:
        selector = pickle.load(f)
    
    print(f"Selector type: {type(selector).__name__}")
    if hasattr(selector, 'n_features_in_'):
        print(f"Selector expects {selector.n_features_in_} input features")
    if hasattr(selector, 'n_features_'):
        print(f"Selector selects {selector.n_features_} features")
    if hasattr(selector, 'get_support'):
        support = selector.get_support()
        print(f"Selector mask: {support}")
        print(f"Number of selected features: {support.sum()}")

if feature_names_file.exists():
    import json
    with open(feature_names_file, 'r') as f:
        feature_names = json.load(f)
    print(f"\nFeature names file has {len(feature_names)} features")
    print(f"First 10: {feature_names[:10]}")
