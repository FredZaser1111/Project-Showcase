# Clinical AI Assistant — Project Brief

## Business Context

Healthcare professionals face information overload when diagnosing and treating patients. A RAG-based system over trusted medical references (Merck Manuals) can streamline decision-making, especially in time-sensitive settings.

## Objective

Build a **RAG-based AI solution** using the Merck Manuals to:

- Reduce information overload
- Support faster, evidence-based decisions
- Analyze impact on diagnostics and patient outcomes
- Evaluate potential to standardize care
- Deliver a working prototype

## Data Source

- **Merck Manuals** — 4,000+ page PDF, 23 sections
- Published by Merck & Co. since 1899
- Covers disorders, tests, diagnoses, and drugs

## Questions the Model Must Answer

1. What is the protocol for managing sepsis in a critical care unit?
2. What are the common symptoms of appendicitis, and can it be cured via medicine? If not, what surgical procedure should be followed?
3. What are effective treatments for sudden patchy hair loss (localized bald spots), and what are possible causes?
4. What treatments are recommended for physical injury to brain tissue (temporary or permanent impairment)?
5. What precautions and treatment steps apply to a leg fracture during a hiking trip, and what should be considered for care and recovery?

## Runtime

- Google Colab with **T4 GPU**
- Runtime → Change runtime type → Hardware accelerator → GPU

## Submission Options

| Path | Deliverable | Format |
|------|-------------|--------|
| **Full-code** | Solution notebook with code + insights | `.html` |
| **Low-code** | Business presentation with insights | `.pdf` |

**Important:** Submit only ONE file. If you submit a presentation, only the presentation is evaluated.

## Full-Code Best Practices

- Well-documented notebook (markdown insights + inline comments)
- Run sequentially start-to-finish before export
- No warnings or errors
- Export as HTML, not `.ipynb`

## Low-Code Best Practices

- Audience: Data Science lead
- Cover: business overview, key findings, recommendations, implementation benefits
- Avoid copying code from notebook unless code is the focal point
