from dependencies.modeling.compute_permutation_importances import (
    compute_permutation_importances,
)

# final_model is the output of optuna_train_final_model_and_log.py
importances = compute_permutation_importances(
    final_model,
    X,
    y,
)  # dict: feat -> importance
# Sort by absolute importance and keep top 10
sorted_feats = sorted(importances, key=lambda k: abs(importances[k]), reverse=True)
for feat in sorted_feats[:10]:
    mlflow.log_metric(f"perm_importance_{feat}", importances[feat])
