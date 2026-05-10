import joblib
import os

model_path = r'c:\Users\Dimas\.gemini\antigravity\scratch\banking_anomaly_ml\ml\models\banking_model.pkl'

if os.path.exists(model_path):
    print(f"Inspecting {model_path}...")
    bundle = joblib.load(model_path)
    print(f"Type: {type(bundle)}")
    if isinstance(bundle, dict):
        print(f"Keys: {list(bundle.keys())}")
        for k, v in bundle.items():
            if k != 'model':
                print(f"  {k}: {v}")
            else:
                print(f"  model type: {type(v)}")
                if hasattr(v, 'named_steps'):
                    print(f"  Pipeline steps: {list(v.named_steps.keys())}")
                    preprocessor = v.named_steps.get('preprocessor')
                    if preprocessor:
                        print(f"  Transformers: {[t[0] for t in preprocessor.transformers_]}")
                        for name, trans, cols in preprocessor.transformers_:
                            print(f"    {name}: {cols}")
    else:
        print("Not a dictionary.")
else:
    print("File not found.")
