# ReneWind — Neural Network Predictive Maintenance

Full-code capstone (UT Austin PGP style): classify wind-turbine **generator failure** from 40 ciphered sensor features and minimize maintenance cost.

## Submission artifact

| File | Purpose |
| --- | --- |
| `ReneWind_Neural_Network_Solution.html` | **Submit this** (nbconvert from executed notebook) |
| `ReneWind_Neural_Network_Solution.ipynb` | Source notebook (regenerate with `build_notebook.py`) |
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

- EDA: overview, univariate (V1–V40), bivariate correlations vs. `Target`
- Preprocessing: stratified split, median imputation, standardization (no leakage)
- Models: baseline **SGD** NN + six tuned variants (depth, Adam, dropout, class weights)
- Selection: validation **cost efficiency** + **maintenance cost**; threshold tuned on validation; single test evaluation
- Business insights and recommendations in markdown

## Cursor agents

See `AGENTS.md` for vibe-coding rules and checklist.
