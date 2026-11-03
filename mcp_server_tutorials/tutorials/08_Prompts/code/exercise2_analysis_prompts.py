"""
Exercise 2: Data Analysis Prompts
====================================

TASK:
Create an MCP server with 3 prompts for data analysis:

1. describe_dataset(dataset_name, columns, row_count)
   - Asks the LLM to describe a dataset
   - Include column names, row count, and expected data types
   - Ask for a summary of what the dataset likely contains

2. find_outliers(column_name, data_description, method)
   - Asks the LLM to help find outliers in a column
   - The "method" parameter defaults to "IQR"
   - Should suggest Python code using pandas

3. correlation_analysis(column1, column2, dataset_description)
   - Asks the LLM to analyze correlation between two columns
   - Should suggest appropriate correlation methods
   - Should recommend visualizations

HINTS:
- Think about what a data scientist needs to know
- Include specific instructions for Python code generation
- Use default values where it makes sense
- Return clear, structured prompts

Try it yourself before looking at exercise2_solution.py!
"""

from mcp.server.fastmcp import FastMCP

# Step 1: Create the MCP server
server = FastMCP("DataAnalysisExercise")

# ---- YOUR CODE HERE ----

# Prompt 1: describe_dataset
# TODO: Create a prompt for describing a dataset
# Parameters: dataset_name (str), columns (str), row_count (str)


# Prompt 2: find_outliers
# TODO: Create a prompt for finding outliers
# Parameters: column_name (str), data_description (str), method (str, default="IQR")


# Prompt 3: correlation_analysis
# TODO: Create a prompt for correlation analysis
# Parameters: column1 (str), column2 (str), dataset_description (str)


# ---- END YOUR CODE ----

# Run the server
if __name__ == "__main__":
    server.run()
