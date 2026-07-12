"""
Exercise 3: Machine Learning Domain Prompts
==============================================

TASK:
Create an MCP server with 3 prompts for ML workflows:

1. model_evaluation(model_name, metrics, dataset_description)
   - Asks the LLM to evaluate an ML model
   - Include the model name, metrics (accuracy, F1, etc.)
   - Ask for interpretation and improvement suggestions

2. feature_engineering(dataset_description, target_variable, current_features)
   - Asks the LLM to suggest new features
   - Include dataset context and existing features
   - Ask for Python code to create the features

3. hyperparameter_tuning(model_name, current_params, performance)
   - Asks the LLM to suggest better hyperparameters
   - Include current parameters and their performance
   - Default performance parameter to "not measured"
   - Ask for a tuning strategy

HINTS:
- Think about what an ML engineer needs at each stage
- Include specific Python library suggestions (sklearn, etc.)
- Ask for both explanation AND code
- Use default values where appropriate

Try it yourself before looking at exercise3_solution.py!
"""

from mcp.server.fastmcp import FastMCP

# Step 1: Create the MCP server
server = FastMCP("MLDomainExercise")

# ---- YOUR CODE HERE ----

# Prompt 1: model_evaluation
# TODO: Create a prompt for evaluating ML models
# Parameters: model_name (str), metrics (str), dataset_description (str)


# Prompt 2: feature_engineering
# TODO: Create a prompt for suggesting new features
# Parameters: dataset_description (str), target_variable (str), current_features (str)


# Prompt 3: hyperparameter_tuning
# TODO: Create a prompt for hyperparameter tuning
# Parameters: model_name (str), current_params (str), performance (str, default="not measured")


# ---- END YOUR CODE ----

# Run the server
if __name__ == "__main__":
    server.run()
