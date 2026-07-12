"""
Exercise 3 Solution: Machine Learning Domain Prompts
=======================================================

This solution creates 3 prompts for common ML workflows:
model evaluation, feature engineering, and hyperparameter tuning.

These prompts are designed for data scientists who want
structured guidance from an LLM during their ML workflow.
"""

from mcp.server.fastmcp import FastMCP

# Step 1: Create the MCP server
server = FastMCP("MLDomainSolution")


# ---- Prompt 1: Model Evaluation ----
# This prompt helps evaluate an ML model's performance.
# It asks for interpretation of metrics and improvement ideas.
@server.prompt()
def model_evaluation(
    model_name: str,
    metrics: str,
    dataset_description: str,
) -> str:
    """Evaluate an ML model's performance and suggest improvements."""
    return (
        f"Please evaluate the following machine learning model:\n\n"
        f"Model: {model_name}\n"
        f"Dataset: {dataset_description}\n"
        f"Metrics:\n{metrics}\n\n"
        f"Please provide:\n"
        f"1. Interpretation of each metric:\n"
        f"   - Is the performance good, average, or poor?\n"
        f"   - What does each metric tell us?\n"
        f"2. Potential issues to investigate:\n"
        f"   - Overfitting or underfitting signs\n"
        f"   - Class imbalance effects\n"
        f"   - Data leakage concerns\n"
        f"3. Suggestions for improvement:\n"
        f"   - Feature engineering ideas\n"
        f"   - Model architecture changes\n"
        f"   - Hyperparameter tuning directions\n"
        f"   - Data augmentation strategies\n"
        f"4. Python code using sklearn to:\n"
        f"   - Generate a classification report\n"
        f"   - Plot a confusion matrix\n"
        f"   - Plot ROC curve (if applicable)\n"
        f"5. Next steps recommendation"
    )


# ---- Prompt 2: Feature Engineering ----
# This prompt suggests new features to improve model performance.
# It considers the existing features and the prediction target.
@server.prompt()
def feature_engineering(
    dataset_description: str,
    target_variable: str,
    current_features: str,
) -> str:
    """Suggest new features for an ML model."""
    return (
        f"Please suggest feature engineering ideas for the "
        f"following ML problem:\n\n"
        f"Dataset: {dataset_description}\n"
        f"Target Variable: {target_variable}\n"
        f"Current Features: {current_features}\n\n"
        f"Please provide:\n"
        f"1. Analysis of current features:\n"
        f"   - Which features are likely most important?\n"
        f"   - Which might be redundant?\n"
        f"2. New feature suggestions:\n"
        f"   - Mathematical combinations (ratios, products, logs)\n"
        f"   - Temporal features (if dates are present)\n"
        f"   - Categorical encodings\n"
        f"   - Interaction features\n"
        f"   - Aggregation features\n"
        f"3. Python code using pandas to create each new feature:\n"
        f"   - Show the exact code for each transformation\n"
        f"   - Include comments explaining the intuition\n"
        f"4. Feature selection strategy:\n"
        f"   - How to evaluate which new features help\n"
        f"   - Code for feature importance analysis\n"
        f"5. Warning about potential pitfalls:\n"
        f"   - Data leakage risks\n"
        f"   - Multicollinearity concerns"
    )


# ---- Prompt 3: Hyperparameter Tuning ----
# This prompt suggests better hyperparameters for a model.
# The performance parameter defaults to "not measured"
# for when the user hasn't benchmarked yet.
@server.prompt()
def hyperparameter_tuning(
    model_name: str,
    current_params: str,
    performance: str = "not measured",
) -> str:
    """Suggest hyperparameter tuning strategies for an ML model."""
    return (
        f"Please suggest a hyperparameter tuning strategy for:\n\n"
        f"Model: {model_name}\n"
        f"Current Parameters:\n{current_params}\n"
        f"Current Performance: {performance}\n\n"
        f"Please provide:\n"
        f"1. Analysis of current parameters:\n"
        f"   - Are the current values reasonable?\n"
        f"   - Which parameters have the most impact?\n"
        f"2. Recommended search space:\n"
        f"   - For each key parameter, suggest a range to try\n"
        f"   - Explain why each range was chosen\n"
        f"3. Tuning strategy recommendation:\n"
        f"   - Grid Search vs Random Search vs Bayesian\n"
        f"   - How many iterations to try\n"
        f"   - Cross-validation strategy\n"
        f"4. Python code using sklearn:\n"
        f"   - GridSearchCV or RandomizedSearchCV setup\n"
        f"   - Parameter grid definition\n"
        f"   - Fitting and evaluating results\n"
        f"   - Extracting best parameters\n"
        f"5. Tips for {model_name} specifically:\n"
        f"   - Common pitfalls\n"
        f"   - Parameters that interact with each other\n"
        f"   - When to stop tuning"
    )


# ---- Run the server ----
if __name__ == "__main__":
    server.run()
