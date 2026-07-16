# ReneWind — Neural Network Predictive Maintenance

**UT Austin McCombs PGP · AI & Machine Learning** — full-code neural network project.

Classify wind-turbine **generator failure** from 40 ciphered sensor features and choose models by **maintenance dollars**, not vanity metrics.

| | |
| --- | --- |
| **Problem** | Imbalanced failure detection; missed failures are expensive |
| **Approach** | Leakage-safe preprocessing → SGD baseline NN → six tuned variants → validation cost selection |
| **Business KPI** | Maximize validation **cost efficiency**, then minimize **maintenance cost** |
| **Stack** | Python, TensorFlow/Keras, scikit-learn, pandas, Jupyter |

Relevant for **business technology solutions** and applied ML roles: thresholding and model selection are tied to repair ($15k), replacement ($40k), and inspection ($5k) costs.

## Browse artifacts

| File | Purpose |
| --- | --- |
| [`INN_ReneWind_Main_Project_FullCode_Notebook.html`](INN_ReneWind_Main_Project_FullCode_Notebook.html) | Course-template HTML submission |
| [`INN_ReneWind_Main_Project_FullCode_Notebook.ipynb`](INN_ReneWind_Main_Project_FullCode_Notebook.ipynb) | Source notebook (INN template) |
| [`ReneWind_Neural_Network_Solution.html`](ReneWind_Neural_Network_Solution.html) | Alternate HTML build |
| `data/Train.csv`, `data/Test.csv` | Training and held-out test data |

## Setup

```bash
cd projects/renewind
pip install -r requirements.txt
python build_notebook.py
jupyter nbconvert --to notebook --execute ReneWind_Neural_Network_Solution.ipynb
jupyter nbconvert --to html ReneWind_Neural_Network_Solution_executed.ipynb --output ReneWind_Neural_Network_Solution.html
```

## Rubric coverage

- **EDA:** overview, univariate (V1–V40), bivariate correlations vs. `Target`
- **Preprocessing:** stratified split, median imputation, standardization (fit on train only)
- **Models:** baseline **SGD** NN + six variants (depth, Adam, dropout, class weights)
- **Selection:** validation cost efficiency + maintenance cost; threshold tuned on validation; one test evaluation
- **Insights:** business recommendations in notebook markdown

## Agent notes

See [`AGENTS.md`](AGENTS.md) for regeneration checklist and conventions.
