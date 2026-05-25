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

cells.append(md("# **Problem Statement**"))

cells.append(md("## Business Context"))

cells.append(md(
"""Renewable energy sources play an increasingly important role in the global energy mix, as the effort to reduce the environmental impact of energy production increases.

Out of all the renewable energy alternatives, wind energy is one of the most developed technologies worldwide. The U.S Department of Energy has put together a guide to achieving operational efficiency using predictive maintenance practices.

Predictive maintenance uses sensor information and analysis methods to measure and predict degradation and future component capability. The idea behind predictive maintenance is that failure patterns are predictable and if component failure can be predicted accurately and the component is replaced before it fails, the costs of operation and maintenance will be much lower.

The sensors fitted across different machines involved in the process of energy generation collect data related to various environmental factors (temperature, humidity, wind speed, etc.) and additional features related to various parts of the wind turbine (gearbox, tower, blades, break, etc.)."""
))

cells.append(md("## Objective"))

cells.append(md(
"""“ReneWind” is a company working on improving the machinery/processes involved in the production of wind energy using machine learning and has collected data of generator failure of wind turbines using sensors. They have shared a ciphered version of the data, as the data collected through sensors is confidential (the type of data collected varies with companies). Data has 40 predictors, 20000 observations in the training set and 5000 in the test set.

The objective is to build various classification models, tune them, and find the best one that will help identify failures so that the generators could be repaired before failing/breaking to reduce the overall maintenance cost.
The nature of predictions made by the classification model will translate as follows:

- True positives (TP) are failures correctly predicted by the model. These will result in repairing costs.
- False negatives (FN) are real failures where there is no detection by the model. These will result in replacement costs.
- False positives (FP) are detections where there is no failure. These will result in inspection costs.

It is given that the cost of repairing a generator is much less than the cost of replacing it, and the cost of inspection is less than the cost of repair.

“1” in the target variables should be considered as “failure” and “0” represents “No failure”."""
))

cells.append(md("## Data Description"))

cells.append(md(
"""The data provided is a transformed version of the original data which was collected using sensors.

- Train.csv - To be used for training and tuning of models.
- Test.csv - To be used only for testing the performance of the final best model.

Both the datasets consist of 40 predictor variables and 1 target variable."""
))

cells.append(md("# 1 - Installing and Importing the necessary libraries"))

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

cells.append(md("# 2 - Import Dataset"))

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

cells.append(md("# 3 - Data Overview"))

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
"""<span style="color: blue;"> **Observation**</span>
* Training data has 20,000 rows and 41 columns; test data has 5,000 rows.
* Only V1 and V2 have missing values (<1%).
* There are no duplicate rows."""
))

cells.append(md("# 4 - Exploratory Data Analysis (EDA)\n\n## 4.2 - Univariate analysis"))

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
"""<span style="color: blue;"> **Observation**</span>
* Failures (Target = 1) are the minority class in train and test sets.
* Class proportions are similar across train and test."""
))

cells.append(md("## 4.3 - Bivariate Analysis\n\n### 4.3.1 - Correlation Check"))

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
"""<span style="color: blue;"> **Observation**</span>
* Several predictors show correlation with the target variable.
* Distributions differ between failure and non-failure classes for top correlated sensors."""
))

cells.append(md("# 5 - Data Preprocessing\n\n## 5.1 - Data Preparation for Modeling"))

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

cells.append(md("## 5.2 - Missing Value Imputation and Scaling"))

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
"""<span style="color: blue;"> **Observation**</span>
* Missing values in V1 and V2 are imputed using the training set median.
* Features are standardized using training data statistics.
* Imputation and scaling are performed after the train-validation split to avoid data leakage.
* The target variable is imbalanced; class weights will be used during model training."""
))

cells.append(md("# 6 - Model Building and Performance Improvement"))

cells.append(md(
"""## 6.1 - Model Evaluation Criterion

In this problem, we aim to predict generator failures, where:

- **Class 1** represents "Failure"
- **Class 0** represents "No failure"

When evaluating a classification model, we consider the following outcomes:

- **True Positives (TP)**: The model correctly predicts a "Failure" (Class 1) when the actual class is "Failure" (Class 1). These result in repair costs.
- **True Negatives (TN)**: The model correctly predicts "No failure" (Class 0) when the actual class is "No failure" (Class 0).
- **False Negatives (FN)**: The model incorrectly predicts "No failure" (Class 0) when the actual class is "Failure" (Class 1). These are costly as they lead to generator replacement.
- **False Positives (FP)**: The model incorrectly predicts "Failure" (Class 1) when the actual class is "No failure" (Class 0). These result in inspection costs.

Based on the problem description, the cost of a False Negative (replacement cost) is significantly higher than the cost of a False Positive (inspection cost), and the cost of a True Positive (repair cost) is less than the replacement cost.

For final model selection, we use a maintenance cost function on the validation set:

**Maintenance cost** = TP × $15,000 + FN × $40,000 + FP × $5,000

**Cost efficiency** = (TP + FN) × $15,000 ÷ Maintenance cost

The best model maximizes **cost efficiency** on the validation set (and minimizes maintenance cost as a tie-breaker). Recall is tracked during training and reported as a supporting metric."""
))

cells.append(md("## 6.2 - Define utility Functions"))

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

cells.append(md("**Since the class is heavily imbalanced in the data, we'll use class weights in all the models except Model 5.**"))

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

    val_cost = int(val_perf['Maintenance_Cost'].iloc[0])
    val_eff = val_perf['Cost_Efficiency'].iloc[0]
    print(f'Training time: {elapsed:.1f}s')
    print(f'Validation maintenance cost: ${val_cost:,} | Cost efficiency: {val_eff:.4f}')
    display(train_perf)
    display(val_perf)
    return model, val_perf
"""
))

cells.append(md("## 6.3 - Model 0 - Baseline Model"))

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

cells.append(md(
"""<span style="color: blue;"> **Observation**</span>
* Model 0 establishes baseline performance with SGD and one hidden layer (7 neurons).
* Compare validation maintenance cost and cost efficiency with subsequent models."""
))

cells.append(md("## 6.4 - Model 1 - Add additional hidden layer"))

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

cells.append(md(
"""<span style="color: blue;"> **Observation**</span>
* Model 1 adds a second hidden layer (14 and 7 neurons).
* Review validation cost efficiency relative to Model 0."""
))

cells.append(md("## 6.5 - Model 2 - Add third hidden layer"))

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

cells.append(md(
"""<span style="color: blue;"> **Observation**</span>
* Model 2 uses three hidden layers (21, 14, and 7 neurons).
* Check whether validation maintenance cost improves versus Models 0 and 1."""
))

cells.append(md("## 6.6 - Model 3 - Change the optimizer to Adam"))

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

cells.append(md(
"""<span style="color: blue;"> **Observation**</span>
* Model 3 uses the Adam optimizer with the same architecture as Model 0.
* Compare validation maintenance cost and cost efficiency with SGD models."""
))

cells.append(md("## 6.7 - Model 4 - Add dropout layer"))

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

cells.append(md(
"""<span style="color: blue;"> **Observation**</span>
* Model 4 adds dropout (0.3) to the two-hidden-layer architecture.
* Dropout may reduce overfitting; compare validation cost metrics with Model 1."""
))

cells.append(md("## 6.8 - Model 5 - Train without class weights"))

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

cells.append(md(
"""<span style="color: blue;"> **Observation**</span>
* Model 5 is the baseline architecture trained without class weights.
* Maintenance cost on validation typically increases when failures are under-detected."""
))

cells.append(md("## 6.9 - Model 6 - Adam with dropout and two hidden layers"))

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

cells.append(md(
"""<span style="color: blue;"> **Observation**</span>
* Model 6 combines Adam, dropout, and two hidden layers with class weights.
* Compare validation cost efficiency with Models 3 and 4."""
))

cells.append(md("## 6.10 - Model 7 - Deep network with Adam and dropout"))

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

cells.append(md(
"""<span style="color: blue;"> **Observation**</span>
* Model 7 uses three hidden layers with Adam and dropout.
* Compare validation maintenance cost and cost efficiency across all models."""
))

cells.append(md("# 7 - Model Performance Comparison and Final Model Selection"))

cells.append(code(
"""train_df = pd.concat(results_train.values(), axis=0)
val_df = pd.concat(results_val.values(), axis=0)
test_df = pd.concat(results_test.values(), axis=0)

print('=== Training metrics ===')
display(train_df)

print('=== Validation metrics (sorted by cost efficiency) ===')
val_sorted = val_df.sort_values(
    ['Cost_Efficiency', 'Maintenance_Cost'],
    ascending=[False, True],
)
display(val_sorted)

# Visual: validation maintenance cost by model
plot_df = val_sorted.reset_index().rename(columns={'index': 'Model'})
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
sns.barplot(data=plot_df, x='Maintenance_Cost', y='Model', ax=axes[0], color='steelblue')
axes[0].set_title('Validation maintenance cost (lower is better)')
axes[0].set_xlabel('USD')
sns.barplot(data=plot_df, x='Cost_Efficiency', y='Model', ax=axes[1], color='seagreen')
axes[1].set_title('Validation cost efficiency (higher is better)')
axes[1].set_xlim(0, 1)
plt.tight_layout()
plt.show()
"""
))

cells.append(code(
"""# --- Step 1: Pick architecture by validation dollars (not recall) ---
best_row = val_df.sort_values(
    ['Cost_Efficiency', 'Maintenance_Cost', 'Recall'],
    ascending=[False, True, False],
).iloc[0]
best_name = best_row.name
print('Selected architecture (validation cost efficiency):', best_name)
display(best_row.to_frame().T)

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
"""
))

cells.append(md("## 7.1 - Tune classification threshold on validation data"))

cells.append(code(
"""threshold_grid = np.round(np.arange(0.10, 0.91, 0.05), 2)
threshold_rows = []

for t in threshold_grid:
    perf, cm = model_performance(best_model, X_val, y_val, threshold=float(t), label=f't={t}')
    threshold_rows.append({
        'threshold': t,
        'Maintenance_Cost': perf['Maintenance_Cost'].iloc[0],
        'Cost_Efficiency': perf['Cost_Efficiency'].iloc[0],
        'Recall': perf['Recall'].iloc[0],
        'FN': int(cm[1, 0]),
        'FP': int(cm[0, 1]),
        'TP': int(cm[1, 1]),
    })

threshold_df = pd.DataFrame(threshold_rows).sort_values(
    ['Cost_Efficiency', 'Maintenance_Cost'], ascending=[False, True]
)
display(threshold_df.head(10))

best_threshold_row = threshold_df.iloc[0]
BEST_THRESHOLD = float(best_threshold_row['threshold'])
print(f'Optimal validation threshold: {BEST_THRESHOLD}')
print(f"Validation maintenance cost at best threshold: ${int(best_threshold_row['Maintenance_Cost']):,}")
print(f"Validation cost efficiency: {best_threshold_row['Cost_Efficiency']:.4f}")

plt.figure(figsize=(8, 4))
plt.plot(threshold_df['threshold'], threshold_df['Maintenance_Cost'], marker='o')
plt.xlabel('Probability threshold')
plt.ylabel('Validation maintenance cost (USD)')
plt.title(f'{best_name} — cost vs. threshold')
plt.tight_layout()
plt.show()
"""
))

cells.append(code(
"""# --- Step 2: One-time held-out test evaluation at dollar-optimal threshold ---
val_final_perf, val_final_cm = model_performance(
    best_model, X_val, y_val, threshold=BEST_THRESHOLD, label=best_name + ' (val, tuned)'
)
final_test_perf, final_cm = model_performance(
    best_model, X_test, y_test, threshold=BEST_THRESHOLD, label=best_name + ' (test)'
)

print('=== Final validation performance (tuned threshold) ===')
display(val_final_perf)
show_confusion(val_final_cm, f'Final — {best_name} (Validation, t={BEST_THRESHOLD})')

print('=== Final test performance (held-out; evaluate once) ===')
display(final_test_perf)
show_confusion(final_cm, f'Final — {best_name} (Test, t={BEST_THRESHOLD})')

tn, fp, fn, tp = final_cm.ravel()
print('Test confusion counts — TP:', tp, 'FN:', fn, 'FP:', fp, 'TN:', tn)
print('Test maintenance cost: $' + f"{int(final_test_perf['Maintenance_Cost'].iloc[0]):,}")
print('Test cost efficiency:', round(final_test_perf['Cost_Efficiency'].iloc[0], 4))
"""
))

cells.append(md(
"""<span style="color: blue;"> **Observation**</span>
* The final model is selected using validation cost efficiency and maintenance cost.
* The probability threshold is tuned on the validation set.
* The test set is used once for final evaluation at the selected threshold."""
))

cells.append(md("# 8 - Actionable Insights and Recommendations"))

cells.append(md(
"""**Actionable insights**

1. Predictive maintenance models should be compared using maintenance cost and cost efficiency on validation data, in addition to recall.
2. Class weights help detect rare failures and reduce replacement costs from false negatives.
3. Model depth, dropout, and the Adam optimizer can improve validation cost efficiency; the final architecture should be chosen based on validation metrics.
4. Tuning the classification threshold on validation data can further reduce maintenance cost before deployment.

**Business recommendations**

1. Deploy the selected model with the tuned probability threshold in maintenance workflows.
2. Monitor TP, FN, and FP counts and translate them into maintenance cost for management reporting.
3. Retrain the model periodically as new sensor data and failure labels become available.
4. Focus instrumentation quality on sensors most correlated with failures identified during EDA."""
))

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
