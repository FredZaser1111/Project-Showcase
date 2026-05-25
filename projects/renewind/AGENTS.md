# ReneWind — Cursor agent guide

## Project goal

Full-code submission for **ReneWind** wind-turbine **generator failure** classification (UT Austin PGP neural networks module). Deliverable: **one HTML file** exported from the solution Jupyter notebook.

## Rubric checklist

| Section | Requirements |
| --- | --- |
| EDA | Data overview, univariate (all V1–V40), bivariate (target correlations) |
| Preprocessing | Train/val split, median imputation + scaling fit on train only, no leakage |
| Model building | Metric rationale (recall + maintenance cost), **baseline NN with SGD** |
| Tuning | **≥6** variants using: extra hidden layers, **SGD/Adam**, **dropout**, **class weights** |
| Selection | Compare validation metrics; test set only for final model |
| Insights | Actionable business recommendations |

## Key files

- `data/Train.csv`, `data/Test.csv` — do not tune on test labels
- `build_notebook.py` — regenerates `ReneWind_Neural_Network_Solution.ipynb`
- `ReneWind_Neural_Network_Solution.html` — submission artifact

## Commands

```bash
cd projects/renewind
pip install -r requirements.txt
python build_notebook.py
jupyter nbconvert --to notebook --execute ReneWind_Neural_Network_Solution.ipynb
jupyter nbconvert --to html ReneWind_Neural_Network_Solution.ipynb --output ReneWind_Neural_Network_Solution.html
```

## Conventions

- Target: `1` = failure, `0` = no failure
- Costs: repair $15k, replacement $40k, inspection $5k
- Prefer **recall** on validation; tie-break with **cost efficiency**
- Comment code and markdown observations in business language (PGP style)
