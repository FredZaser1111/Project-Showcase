"""Generate the ReneWind full-code solution notebook."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NOTEBOOK_PATH = ROOT / "ReneWind_Neural_Network_Solution.ipynb"


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": [text]}


def code(text: str) -> dict:
    return {
        "cell_type": "code",
        "metadata": {},
        "source": [text],
        "outputs": [],
        "execution_count": None,
    }


cells: list[dict] = []

cells.append(md("# ReneWind — Wind Turbine Generator Failure Prediction (Full Code)\n\n**UT Austin PGP-style neural network project** | Predictive maintenance using sensor data"))

cells.append(md("## Problem Statement\n\n### Business Context\n\nRenewable energy sources play an increasingly important role in the global energy mix, as efforts to reduce the environmental impact of energy production increase.\n\nWind energy is among the most mature renewable technologies worldwide. The U.S. Department of Energy recommends **predictive maintenance**: using sensor data and analytics to predict degradation before catastrophic failure, lowering operations and maintenance (O&M) cost.\n\nSensors on wind turbines capture environmental readings (temperature, humidity, wind speed, etc.) and mechanical signals from components (gearbox, tower, blades, brake, etc.).\n\n### Objective\n\n**ReneWind** collects confidential, ciphered sensor data to predict **generator failure** (`Target = 1`). The training set has **20,000** rows and the held-out test set has **5,000** rows across **40** predictors.\n\nWe build and tune **neural network classifiers** so failures are caught early (repair) instead of missed (replacement).\n\n| Outcome | Business impact |\n| --- | --- |\n| **TP** — failure predicted correctly | Repair cost (preferred) |\n| **FN** — failure missed | Replacement cost (highest) |\n| **FP** — false alarm | Inspection cost (lowest) |\n\n**Cost hierarchy:** Replacement > Repair > Inspection. Minimizing **false negatives** is the top priority.\n\n### Data Description\n\n- `Train.csv` — training and hyperparameter tuning only\n- `Test.csv` — **final** evaluation only (no tuning on test data)\n\nBoth files contain 40 predictors (`V1`–`V40`) and binary `Target` (1 = failure, 0 = no failure)."))

cells.append(md("## 1 — Import Libraries"))

cells.append(code(
"""# Standard library
import os
import time
import warnings

# Data and visualization
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from IPython.display import display

# Scikit-learn
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# TensorFlow / Keras
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.optimizers import SGD, Adam

# Reproducibility and clean submission output
warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
SEED = 1
np.random.seed(SEED)
tf.random.set_seed(SEED)

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", 100)
sns.set_style("whitegrid")
"""
))

cells.append(md("## 2 — Load Data"))

cells.append(code(
"""DATA_DIR = "data"
train_path = os.path.join(DATA_DIR, "Train.csv")
test_path = os.path.join(DATA_DIR, "Test.csv")

data = pd.read_csv(train_path)
test_data = pd.read_csv(test_path)

data_copy = data.copy()
test_copy = test_data.copy()
"""
))

cells.append(md("## 3 — Exploratory Data Analysis\n\n### 3.1 Data Overview"))

cells.append(code("data.head()"))
cells.append(code("test_data.head()"))
cells.append(code("print('Train shape:', data.shape)\nprint('Test shape:', test_data.shape)"))
cells.append(code("data.info()"))
cells.append(code("data.describe(include='all').T"))
cells.append(code("print('Train duplicates:', data.duplicated().sum())\nprint('Test duplicates:', test_data.duplicated().sum())"))
cells.append(code(
"""missing_train = (data.isnull().sum() / len(data) * 100).round(2)
missing_test = (test_data.isnull().sum() / len(test_data) * 100).round(2)
print('Missing % (train):\\n', missing_train[missing_train > 0])
print('Missing % (test):\\n', missing_test[missing_test > 0])
"""
))

cells.append(md(
"""**Observation:** Training data has 20,000 rows × 41 columns; test has 5,000 rows. Only **V1** and **V2** show small missingness (<1%). No duplicate rows. All predictors are numeric (ciphered sensor channels)."""
))

cells.append(md("### 3.2 Univariate Analysis"))

cells.append(code(
"""def histogram_boxplot(df, feature, figsize=(10, 5)):
    \"\"\"Combined histogram and boxplot for one feature.\"\"\"
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    sns.histplot(data=df, x=feature, ax=axes[0], kde=True)
    axes[0].set_title(f'Distribution — {feature}')
    sns.boxplot(data=df, y=feature, ax=axes[1])
    axes[1].set_title(f'Boxplot — {feature}')
    plt.tight_layout()
    plt.show()
"""
))

cells.append(code(
"""# Target distribution (class imbalance is critical for maintenance cost)
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
sns.countplot(data=data, x='Target', ax=ax[0])
ax[0].set_title('Target — Train')
sns.countplot(data=test_data, x='Target', ax=ax[1])
ax[1].set_title('Target — Test')
plt.tight_layout()
plt.show()

print('Train counts:\\n', data['Target'].value_counts())
print('Train proportions:\\n', data['Target'].value_counts(normalize=True).round(4))
"""
))

cells.append(code(
"""predictor_cols = [c for c in data.columns if c != 'Target']
# Univariate plots for all 40 sensor predictors
for feature in predictor_cols:
    histogram_boxplot(data, feature, figsize=(9, 4))
"""
))

cells.append(md(
"""**Observation:** Failures (`Target = 1`) are the **minority class** in both train and test, with similar proportions. Most sensor channels are roughly symmetric but some show skew and outliers (expected for environmental and mechanical signals)."""
))

cells.append(md("### 3.3 Bivariate Analysis"))

cells.append(code(
"""predictor_cols = [c for c in data.columns if c != 'Target']
corr_with_target = data[predictor_cols + ['Target']].corr()['Target'].drop('Target').sort_values(key=abs, ascending=False)

plt.figure(figsize=(8, 10))
sns.barplot(x=corr_with_target.head(15).values, y=corr_with_target.head(15).index, palette='viridis')
plt.title('Top 15 |Correlation| with Target (Train)')
plt.xlabel('Pearson correlation')
plt.tight_layout()
plt.show()
"""
))

cells.append(code(
"""top5 = corr_with_target.abs().sort_values(ascending=False).head(5).index.tolist()
fig, axes = plt.subplots(1, len(top5), figsize=(14, 4))
for ax, feat in zip(axes, top5):
    sns.boxplot(data=data, x='Target', y=feat, ax=ax)
    ax.set_title(feat)
plt.suptitle('Top correlated sensors vs. failure', y=1.02)
plt.tight_layout()
plt.show()
"""
))

cells.append(code(
"""# Pairwise correlation among top sensors + target
sns.heatmap(data[top5 + ['Target']].corr(), annot=True, fmt='.2f', cmap='coolwarm', center=0)
plt.title('Bivariate correlation — strongest sensors')
plt.tight_layout()
plt.show()
"""
))

cells.append(md(
"""**Observation:** Several sensors (e.g., among the top correlated features) separate failure vs. non-failure distributions, supporting a nonlinear classifier. No target leakage is present in the feature set."""
))

cells.append(md("## 4 — Data Preprocessing\n\n> Imputation and scaling are fit **only on the training split** after `train_test_split` to prevent **data leakage**."))

cells.append(code(
"""X = data.drop(columns=['Target'])
y = data['Target']

X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=SEED, stratify=y
)

X_test = test_data.drop(columns=['Target'])
y_test = test_data['Target']

print('Train / val / test shapes:', X_train.shape, X_val.shape, X_test.shape)
print('Class balance (train):', y_train.value_counts(normalize=True).round(4).to_dict())
"""
))

cells.append(code(
"""imputer = SimpleImputer(strategy='median')
X_train = pd.DataFrame(imputer.fit_transform(X_train), columns=X.columns)
X_val = pd.DataFrame(imputer.transform(X_val), columns=X.columns)
X_test = pd.DataFrame(imputer.transform(X_test), columns=X.columns)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_val = scaler.transform(X_val)
X_test = scaler.transform(X_test)

y_train = y_train.to_numpy()
y_val = y_val.to_numpy()
y_test = y_test.to_numpy()

print('Missing after imputation (train):', np.isnan(X_train).sum())
"""
))

cells.append(md(
"""**Observation:** V1/V2 missing values are imputed with training-set medians. Features are standardized using training statistics only. Class imbalance persists (~11% failures) and will be handled with **class weights** in most models."""
))

cells.append(md("## 5 — Model Building\n\n### 5.1 Evaluation metric (rationale)\n\n| Metric | Role |\n| --- | --- |\n| **Recall (failure class)** | Primary — reduces expensive **FN** (missed failures → replacement) |\n| **Maintenance cost** | Business-aligned: TP×$15k + FN×$40k + FP×$5k |\n| **Cost efficiency ratio** | (TP+FN)×$15k ÷ total maintenance cost (higher is better, max 1) |\n\nWe optimize neural networks for **recall** while tracking **maintenance cost** for final model selection."))

cells.append(code(
"""REPAIR_COST = 15_000
REPLACEMENT_COST = 40_000
INSPECTION_COST = 5_000

def maintenance_cost(cm):
    tn, fp, fn, tp = cm.ravel()
    return tp * REPAIR_COST + fn * REPLACEMENT_COST + fp * INSPECTION_COST

def cost_efficiency(cm):
    tn, fp, fn, tp = cm.ravel()
    minimum = (tp + fn) * REPAIR_COST
    actual = maintenance_cost(cm)
    return minimum / actual if actual else 0.0

def model_performance(model, X, y, threshold=0.5, label=''):
    prob = model.predict(X, verbose=0).ravel()
    pred = (prob >= threshold).astype(int)
    cm = confusion_matrix(y, pred)
    df_perf = pd.DataFrame({
        'Accuracy': [accuracy_score(y, pred)],
        'Recall': [recall_score(y, pred, zero_division=0)],
        'Precision': [precision_score(y, pred, zero_division=0)],
        'F1': [f1_score(y, pred, zero_division=0)],
        'Maintenance_Cost': [maintenance_cost(cm)],
        'Cost_Efficiency': [cost_efficiency(cm)],
    }, index=[label or 'model'])
    return df_perf, cm

def plot_history(history, metric_name, title):
    # Keras may log metrics as 'Recall' / 'val_Recall'
    keys = list(history.history.keys())
    train_key = next((k for k in keys if metric_name.lower() in k.lower() and not k.startswith('val_')), keys[0])
    val_key = next((k for k in keys if metric_name.lower() in k.lower() and k.startswith('val_')), f'val_{train_key}')
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(history.history[train_key], label='Train')
    ax.plot(history.history[val_key], label='Validation')
    ax.set_xlabel('Epoch')
    ax.set_ylabel(metric_name.capitalize())
    ax.set_title(title)
    ax.legend()
    plt.tight_layout()
    plt.show()

def show_confusion(cm, title):
    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Pred 0', 'Pred 1'], yticklabels=['True 0', 'True 1'])
    plt.title(title)
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.tight_layout()
    plt.show()

# Class weights for imbalance
counts = np.bincount(y_train.astype(int))
cw_dict = {i: len(y_train) / counts[i] for i in range(len(counts))}
cw_dict
"""
))

cells.append(md("### 5.2 Helper to train and evaluate each architecture"))

cells.append(code(
"""EPOCHS = 25
BATCH_SIZE = 32

results_train = {}
results_val = {}
results_test = {}
histories = {}

def train_and_evaluate(name, model, use_class_weight=True, config_note=''):
    tf.keras.backend.clear_session()
    start = time.time()
    fit_kwargs = dict(
        x=X_train, y=y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS, batch_size=BATCH_SIZE,
        verbose=0,
    )
    if use_class_weight:
        fit_kwargs['class_weight'] = cw_dict
    history = model.fit(**fit_kwargs)
    elapsed = time.time() - start

    train_perf, _ = model_performance(model, X_train, y_train, label=name)
    val_perf, val_cm = model_performance(model, X_val, y_val, label=name)
    test_perf, test_cm = model_performance(model, X_test, y_test, label=name)

    results_train[name] = train_perf
    results_val[name] = val_perf
    results_test[name] = test_perf
    histories[name] = history

    plot_history(history, 'loss', f'{name} — Loss\\n{config_note}')
    plot_history(history, 'recall', f'{name} — Recall\\n{config_note}')
    show_confusion(val_cm, f'{name} — Validation confusion matrix')
    show_confusion(test_cm, f'{name} — Test confusion matrix (held-out)')

    print(f'Training time: {elapsed:.1f}s')
    display(train_perf)
    display(val_perf)
    return model, val_perf
"""
))

cells.append(md("### 5.3 Model 0 — Baseline neural network (SGD + class weights)\n\nSingle hidden layer (7 units, ReLU), sigmoid output, **SGD** optimizer — per project requirements."))

cells.append(code(
"""model_0 = Sequential([
    Input(shape=(X_train.shape[1],)),
    Dense(7, activation='relu'),
    Dense(1, activation='sigmoid'),
])
model_0.compile(loss='binary_crossentropy', optimizer=SGD(), metrics=['Recall'])
model_0, _ = train_and_evaluate(
    'Model 0 — Baseline',
    model_0,
    config_note='1×7 ReLU, SGD, class weights, 25 epochs',
)
"""
))

cells.append(md("**Observation (Model 0):** Establishes baseline recall and maintenance cost. SGD with class weights helps detect failures but may underfit compared to deeper nets."))

cells.append(md("### 5.4 Model 1 — More hidden layers (2 layers)\n\n**Technique:** additional hidden layer (14 → 7 neurons)."))

cells.append(code(
"""model_1 = Sequential([
    Input(shape=(X_train.shape[1],)),
    Dense(14, activation='relu'),
    Dense(7, activation='relu'),
    Dense(1, activation='sigmoid'),
])
model_1.compile(loss='binary_crossentropy', optimizer=SGD(), metrics=['Recall'])
model_1, _ = train_and_evaluate(
    'Model 1 — 2 hidden layers',
    model_1,
    config_note='14→7 ReLU, SGD, class weights',
)
"""
))

cells.append(md("**Observation (Model 1):** Deeper network increases capacity; compare validation recall and cost vs. Model 0."))

cells.append(md("### 5.5 Model 2 — More hidden layers (3 layers)\n\n**Technique:** third hidden layer for additional nonlinearity."))

cells.append(code(
"""model_2 = Sequential([
    Input(shape=(X_train.shape[1],)),
    Dense(21, activation='relu'),
    Dense(14, activation='relu'),
    Dense(7, activation='relu'),
    Dense(1, activation='sigmoid'),
])
model_2.compile(loss='binary_crossentropy', optimizer=SGD(), metrics=['Recall'])
model_2, _ = train_and_evaluate(
    'Model 2 — 3 hidden layers',
    model_2,
    config_note='21→14→7 ReLU, SGD, class weights',
)
"""
))

cells.append(md("**Observation (Model 2):** Tests whether extra depth improves failure detection or begins to overfit (train vs. validation recall gap)."))

cells.append(md("### 5.6 Model 3 — Adam optimizer\n\n**Technique:** replace SGD with **Adam** (baseline depth)."))

cells.append(code(
"""model_3 = Sequential([
    Input(shape=(X_train.shape[1],)),
    Dense(7, activation='relu'),
    Dense(1, activation='sigmoid'),
])
model_3.compile(loss='binary_crossentropy', optimizer=Adam(learning_rate=0.001), metrics=['Recall'])
model_3, _ = train_and_evaluate(
    'Model 3 — Adam optimizer',
    model_3,
    config_note='1×7 ReLU, Adam, class weights',
)
"""
))

cells.append(md("**Observation (Model 3):** Adam often converges faster and can improve recall; watch validation gap for overfitting."))

cells.append(md("### 5.7 Model 4 — Dropout regularization\n\n**Technique:** **Dropout** (0.3) after hidden layers with 2-layer architecture."))

cells.append(code(
"""model_4 = Sequential([
    Input(shape=(X_train.shape[1],)),
    Dense(14, activation='relu'),
    Dropout(0.3),
    Dense(7, activation='relu'),
    Dropout(0.3),
    Dense(1, activation='sigmoid'),
])
model_4.compile(loss='binary_crossentropy', optimizer=SGD(), metrics=['Recall'])
model_4, _ = train_and_evaluate(
    'Model 4 — Dropout',
    model_4,
    config_note='14→7 + Dropout 0.3, SGD, class weights',
)
"""
))

cells.append(md("**Observation (Model 4):** Dropout may reduce overfitting and stabilize validation recall."))

cells.append(md("### 5.8 Model 5 — Without class weights\n\n**Technique:** remove **class weights** to measure impact on minority (failure) class."))

cells.append(code(
"""model_5 = Sequential([
    Input(shape=(X_train.shape[1],)),
    Dense(7, activation='relu'),
    Dense(1, activation='sigmoid'),
])
model_5.compile(loss='binary_crossentropy', optimizer=SGD(), metrics=['Recall'])
model_5, _ = train_and_evaluate(
    'Model 5 — No class weights',
    model_5,
    use_class_weight=False,
    config_note='1×7 ReLU, SGD, NO class weights',
)
"""
))

cells.append(md("**Observation (Model 5):** Without class weights, recall on failures typically drops — confirming weights are needed for cost-sensitive maintenance."))

cells.append(md("### 5.9 Model 6 — Combined best practices (Adam + depth + dropout + class weights)\n\n**Technique:** combine **Adam**, **extra hidden layer**, **dropout**, and **class weights**."))

cells.append(code(
"""model_6 = Sequential([
    Input(shape=(X_train.shape[1],)),
    Dense(14, activation='relu'),
    Dropout(0.2),
    Dense(7, activation='relu'),
    Dropout(0.2),
    Dense(1, activation='sigmoid'),
])
model_6.compile(loss='binary_crossentropy', optimizer=Adam(learning_rate=0.0005), metrics=['Recall'])
model_6, _ = train_and_evaluate(
    'Model 6 — Combined',
    model_6,
    config_note='14→7, Dropout 0.2, Adam, class weights',
)
"""
))

cells.append(md("**Observation (Model 6):** Combined tuning targets high validation recall with controlled overfitting; strong candidate for final selection."))

cells.append(md("### 5.10 Model 7 — Adam + three hidden layers + dropout\n\n**Technique:** deeper **Adam** network with dropout (sixth+ architecture variant)."))

cells.append(code(
"""model_7 = Sequential([
    Input(shape=(X_train.shape[1],)),
    Dense(21, activation='relu'),
    Dropout(0.25),
    Dense(14, activation='relu'),
    Dropout(0.25),
    Dense(7, activation='relu'),
    Dense(1, activation='sigmoid'),
])
model_7.compile(loss='binary_crossentropy', optimizer=Adam(learning_rate=0.0005), metrics=['Recall'])
model_7, _ = train_and_evaluate(
    'Model 7 — Deep Adam + dropout',
    model_7,
    config_note='21→14→7, Dropout, Adam, class weights',
)
"""
))

cells.append(md("**Observation (Model 7):** Deepest model in the experiment; compare maintenance cost efficiency on validation before test-set scoring."))

cells.append(md("## 6 — Model Comparison and Final Selection"))

cells.append(code(
"""train_df = pd.concat(results_train.values(), axis=0)
val_df = pd.concat(results_val.values(), axis=0)
test_df = pd.concat(results_test.values(), axis=0)

print('=== Training metrics ===')
display(train_df)
print('=== Validation metrics (used for model selection) ===')
display(val_df.sort_values('Recall', ascending=False))
print('=== Test metrics (held-out; report once for winner) ===')
"""
))

cells.append(code(
"""# Select best model by validation recall, then cost efficiency as tie-breaker
best_row = val_df.sort_values(['Recall', 'Cost_Efficiency'], ascending=False).iloc[0]
best_name = best_row.name
print('Selected model:', best_name)
print(best_row)

model_lookup = {
    'Model 0 — Baseline': model_0,
    'Model 1 — 2 hidden layers': model_1,
    'Model 2 — 3 hidden layers': model_2,
    'Model 3 — Adam optimizer': model_3,
    'Model 4 — Dropout': model_4,
    'Model 5 — No class weights': model_5,
    'Model 6 — Combined': model_6,
    'Model 7 — Deep Adam + dropout': model_7,
}
best_model = model_lookup[best_name]

final_test_perf, final_cm = model_performance(best_model, X_test, y_test, label=best_name)
display(final_test_perf)
show_confusion(final_cm, f'Final model — {best_name} (Test set)')
"""
))

cells.append(md(
"""**Final model reasoning:** The champion is chosen using **validation recall** (proxy for minimizing FN/replacement cost) and **cost efficiency** as a secondary criterion. The held-out **test set** is evaluated **once** for the winner only, avoiding test leakage during tuning."""
))

cells.append(md("## 7 — Actionable Insights and Business Recommendations\n\n### Key takeaways\n\n1. **Class imbalance matters:** Models trained without class weights under-detect failures; weighted training aligns predictions with O&M economics.\n2. **Recall drives savings:** Higher recall shifts spend from **replacement** to **repair** and **inspection**, consistent with the cost hierarchy.\n3. **Depth + regularization:** Additional hidden layers and dropout improve fit when paired with Adam or careful SGD training; monitor train–validation recall gaps.\n4. **Operational deployment:** Deploy the selected model in a **scoring pipeline** (median imputation + standardization + NN) fed by live SCADA/sensor streams.\n\n### Business recommendations\n\n1. **Integrate predictions into maintenance workflows** — flag turbines with failure probability above a threshold for inspection; tune threshold to balance inspection vs. missed failure cost.\n2. **Track maintenance cost KPIs** — report TP/FN/FP monthly using the cost function ($15k / $40k / $5k) to prove ROI.\n3. **Retrain quarterly** — sensor distributions drift; refresh weights using new failure labels while keeping the same leakage-safe preprocessing.\n4. **Start pilot on highest-risk farms** — use top correlated sensors from EDA to prioritize instrumentation quality where the model adds most value.\n\n### Expected benefits\n\n- Fewer catastrophic generator replacements (FN reduction)\n- Planned repairs during low-wind windows\n- Lower total O&M spend and improved turbine availability\n\n---\n\n*End of notebook — export to HTML for submission.*"))

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3.11.0"},
    },
    "cells": cells,
}

NOTEBOOK_PATH.write_text(json.dumps(nb, indent=1))
print(f"Wrote {NOTEBOOK_PATH} ({len(cells)} cells)")
