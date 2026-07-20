"""Documented business rules used by the three workflow agents."""

# Churn Savior: escalate / draft retention offer when P(churn) exceeds this.
CHURN_HIGH_RISK = 0.80

# Loan Underwriting: gray zone routes to compliance investigator + HITL.
LOAN_GRAY_LOW = 0.40
LOAN_GRAY_HIGH = 0.60

# Predictive Maintenance: activate procurement path when days-to-failure <= this.
FAILURE_DAYS_THRESHOLD = 7
