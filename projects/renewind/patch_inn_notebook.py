"""Patch official INN learner notebook for local execution and dollar-based selection."""
from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = Path("/tmp/inn-renewind2/notebooks/INN_ReneWind_Main_Project_FullCode_Notebook_SohailH.ipynb")
DST = ROOT / "INN_ReneWind_Main_Project_FullCode_Notebook.ipynb"
HTML_OUT = ROOT / "INN_ReneWind_Main_Project_FullCode_Notebook.html"


def set_cell_source(cell: dict, text: str) -> None:
    cell["source"] = [text]
    cell["outputs"] = []
    cell["execution_count"] = None


def patch_notebook(nb: dict) -> dict:
    cells = nb["cells"]

    # 9: skip Colab-only pip (assume requirements.txt installed)
    set_cell_source(
        cells[9],
        "# Dependencies: pip install -r requirements.txt (run once in your environment)\n",
    )

    # 13-14: local data paths (no Google Drive)
    set_cell_source(
        cells[13],
        "*Training and test data are loaded from the `data/` folder (Train.csv, Test.csv).*",
    )
    cells[13]["cell_type"] = "markdown"
    set_cell_source(
        cells[14],
        'df = pd.read_csv("data/Train.csv")\n'
        'df_test = pd.read_csv("data/Test.csv")\n',
    )

    # 71: evaluation criterion — maintenance cost (project objective)
    set_cell_source(
        cells[71],
        """- **Primary metric: Maintenance cost / cost efficiency (validation set)**
  - Maintenance cost = TP × $15,000 + FN × $40,000 + FP × $5,000
  - Cost efficiency = (TP + FN) × $15,000 ÷ Maintenance cost (higher is better, max 1)
  - Aligns with ReneWind's goal to reduce overall O&M spend (repair vs. replacement vs. inspection).
- **Supporting metric: Recall**
  - Missing a failure (false negative) drives replacement cost ($40,000).
  - Recall is tracked during training (Keras metric) and reported alongside cost metrics.""",
    )

    # 75: extend performance helper with cost columns
    set_cell_source(
        cells[75],
        '''REPAIR_COST = 15_000
REPLACEMENT_COST = 40_000
INSPECTION_COST = 5_000

def maintenance_cost_from_cm(cm):
    tn, fp, fn, tp = cm.ravel()
    return tp * REPAIR_COST + fn * REPLACEMENT_COST + fp * INSPECTION_COST

def cost_efficiency_from_cm(cm):
    tn, fp, fn, tp = cm.ravel()
    minimum = (tp + fn) * REPAIR_COST
    actual = maintenance_cost_from_cm(cm)
    return minimum / actual if actual else 0.0

def model_performance_classification(
    model, predictors, target, threshold=0.5
):
    """
    Classification metrics plus maintenance cost for model comparison.
    """
    pred = model.predict(predictors, verbose=0) > threshold
    cm = confusion_matrix(target, pred)

    acc = accuracy_score(target, pred)
    recall = recall_score(target, pred, average='macro')
    precision = precision_score(target, pred, average='macro')
    f1 = f1_score(target, pred, average='macro')
    maint = maintenance_cost_from_cm(cm)
    eff = cost_efficiency_from_cm(cm)

    df_perf = pd.DataFrame(
        {
            "Accuracy": [acc],
            "Recall": [recall],
            "Precision": [precision],
            "F1 Score": [f1],
            "Maintenance_Cost": [maint],
            "Cost_Efficiency": [eff],
        },
        index=[0],
    )
    return df_perf
''',
    )

    # 201: remove hard-coded metrics table header (keep flow)
    set_cell_source(
        cells[201],
        "**Validation comparison includes maintenance cost and cost efficiency:**",
    )

    # 202: dynamic comparison + sort by cost efficiency
    set_cell_source(
        cells[202],
        '''models_val_comp_df = pd.concat(
    [
        model_0_val_perf.T,
        model_1_val_perf.T,
        model_2_val_perf.T,
        model_3_val_perf.T,
        model_4_val_perf.T,
        model_5_val_perf.T,
        model_6_val_perf.T,
    ],
    axis=1,
)
models_val_comp_df.columns = [
    "Model 0", "Model 1", "Model 2", "Model 3", "Model 4", "Model 5", "Model 6"
]
print("Validation set performance comparison:")
models_val_comp_df

models_val_comp_df_sorted = models_val_comp_df.T.sort_values(
    by=["Cost_Efficiency", "Maintenance_Cost", "Recall"],
    ascending=[False, True, False],
)
print("Sorted by cost efficiency (primary), then maintenance cost:")
models_val_comp_df_sorted
''',
    )

    # 204: select best model by validation cost efficiency
    set_cell_source(
        cells[204],
        '''# Best architecture: highest validation cost efficiency, then lowest maintenance cost
best_model_name = models_val_comp_df_sorted.index[0]
print("Selected model:", best_model_name)

model_lookup = {
    "Model 0": model_0,
    "Model 1": model_1,
    "Model 2": model_2,
    "Model 3": model_3,
    "Model 4": model_4,
    "Model 5": model_5,
    "Model 6": model_6,
}
best_model = model_lookup[best_model_name]

# Tune threshold on validation to minimize maintenance cost
threshold_grid = np.round(np.arange(0.10, 0.91, 0.05), 2)
best_threshold = 0.5
best_val_cost = float("inf")
for t in threshold_grid:
    pred = best_model.predict(X_val, verbose=0) > float(t)
    cm = confusion_matrix(y_val, pred)
    cost = maintenance_cost_from_cm(cm)
    if cost < best_val_cost:
        best_val_cost = cost
        best_threshold = float(t)
print(f"Optimal validation threshold: {best_threshold}")
print(f"Validation maintenance cost at threshold: ${int(best_val_cost):,}")
''',
    )

    # 205-206: test at tuned threshold
    set_cell_source(
        cells[205],
        "best_model_test_perf = model_performance_classification(best_model, X_test, y_test, threshold=best_threshold)\n"
        "best_model_test_perf\n",
    )
    set_cell_source(
        cells[206],
        '''y_test_pred_best = best_model.predict(X_test, verbose=0)
cr_test_best_model = classification_report(y_test, y_test_pred_best > best_threshold)
print(cr_test_best_model)
''',
    )

    set_cell_source(
        cells[208],
        """**Insights:**

- Models should be compared using **maintenance cost** and **cost efficiency** on the validation set, in addition to recall.
- Class imbalance strongly affects cost; **class weights** and **dropout** help improve failure detection and generalization.
- **Adam** often improves convergence versus SGD for deeper networks.
- Tuning the classification threshold on validation data can further reduce maintenance cost before deployment.""",
    )

    set_cell_source(
        cells[209],
        """**Recommendations:**

- Deploy the selected model with the validation-tuned probability threshold.
- Report TP/FN/FP and translated maintenance cost monthly for O&M leadership.
- Retrain as new sensor data is collected and re-tune the threshold on a validation fold.
- Prioritize instrumentation on sensors most associated with failures from EDA.""",
    )

    set_cell_source(
        cells[211],
        "!jupyter nbconvert --to html INN_ReneWind_Main_Project_FullCode_Notebook.ipynb\n",
    )

    # Clear all outputs for clean execute
    for c in cells:
        c.pop("outputs", None)
        c.pop("execution_count", None)
        if c["cell_type"] == "code":
            c["outputs"] = []
            c["execution_count"] = None

    for c in cells:
        if c["cell_type"] != "code":
            continue
        src = "".join(c.get("source", []))
        src = src.replace('drop(columns=["Target"], axis=1)', 'drop(columns=["Target"])')
        src = src.replace("drop(columns=['Target'], axis=1)", "drop(columns=['Target'])")
        set_cell_source(c, src)

    nb["cells"] = cells
    return nb


def main() -> None:
    if not SRC.exists():
        raise FileNotFoundError(f"Template not found: {SRC}")
    nb = json.loads(SRC.read_text())
    nb = patch_notebook(nb)
    nb["metadata"].setdefault("kernelspec", {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    })
    DST.write_text(json.dumps(nb, indent=1))
    print(f"Patched notebook written to {DST}")


if __name__ == "__main__":
    main()
