import os
import pandas as pd
import matplotlib.pyplot as plt
import subprocess

class AblationRunner:
    """
    Runs configured ablation experiments sequentially and compiles a comparison table.
    Expects configs/exp_*.yaml files to exist.
    """
    def __init__(self, base_dir='.', python_cmd=None):
        import sys
        self.base_dir = base_dir
        self.configs_dir = os.path.join(base_dir, 'configs')
        self.metrics_dir = os.path.join(base_dir, 'outputs', 'metrics')
        self.experiment_script = os.path.join(base_dir, 'experiments', 'run_experiment.py')
        self.python_cmd = python_cmd if python_cmd else sys.executable
        
        self.experiments = [
            'satellite_only',
            'uav_only',
            'leaf_only',
            'sat_uav',
            'uav_leaf',
            'sat_leaf',
            'full_fusion',
            'full_fusion_weighted',
            'full_fusion_learned_gating',
            'full_fusion_attention',
        ]
        
    def run_all(self):
        print(f"Starting Ablation Study for {len(self.experiments)} experiments...")
        os.makedirs(self.metrics_dir, exist_ok=True)
        
        for exp in self.experiments:
            config_path = os.path.join(self.configs_dir, f'exp_{exp}.yaml')
            if not os.path.exists(config_path):
                print(f"Skipping {exp}, config not found: {config_path}")
                continue
                
            print(f"\n{'='*50}")
            print(f"Running Experiment: {exp}")
            print(f"{'='*50}\n")
            
            # Subprocess call to the experiment script
            cmd = [self.python_cmd, self.experiment_script, "--config", config_path]
            try:
                subprocess.run(cmd, check=True)
                print(f"Experiment {exp} completed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Experiment {exp} failed: {e}")
                
        print("\nAll experiments completed. Compiling results...")
        df = self.compile_results()
        if not df.empty:
            self.plot_comparison(df)
            
    def compile_results(self):
        results = []
        for exp in self.experiments:
            # We assume each experiment saves a JSON of its best metrics
            json_path = os.path.join(self.metrics_dir, f"{exp}_metrics.json")
            if os.path.exists(json_path):
                import json
                with open(json_path, 'r') as f:
                    metrics = json.load(f)
                    
                results.append({
                    'experiment': exp,
                    'accuracy': metrics.get('accuracy', 0.0),
                    'precision_macro': metrics.get('precision_macro', 0.0),
                    'recall_macro': metrics.get('recall_macro', 0.0),
                    'f1_macro': metrics.get('f1_macro', 0.0)
                })
                
        if not results:
            print("No results found to compile.")
            return pd.DataFrame()
            
        df = pd.DataFrame(results)
        df = df.round(4)
        
        out_csv = os.path.join(self.metrics_dir, 'ablation_results.csv')
        df.to_csv(out_csv, index=False)
        print(f"Saved ablation results to {out_csv}")
        print("\nAbation Results Table:")
        print(df.to_string(index=False))
        
        return df
        
    def plot_comparison(self, df):
        # Bar chart comparison
        df.set_index('experiment', inplace=True)
        ax = df[['accuracy', 'f1_macro', 'precision_macro', 'recall_macro']].plot(kind='bar', figsize=(12, 6), colormap='viridis')
        
        plt.title('Ablation Study Comparison')
        plt.ylabel('Score')
        plt.ylim(0, 1.1)
        plt.legend(loc='lower right')
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        out_png = os.path.join(self.metrics_dir, 'ablation_comparison.png')
        plt.savefig(out_png, dpi=300)
        print(f"Saved bar chart to {out_png}")
        plt.close()
