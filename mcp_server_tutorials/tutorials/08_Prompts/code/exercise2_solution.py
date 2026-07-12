"""
Exercise 2 Solution: Data Analysis Prompts
=============================================

This solution creates 3 prompts for common data analysis tasks:
describing datasets, finding outliers, and correlation analysis.

Each prompt returns structured instructions that guide the LLM
to provide useful data science guidance with Python code.
"""

from mcp.server.fastmcp import FastMCP

# Step 1: Create the MCP server
server = FastMCP("DataAnalysisSolution")


# ---- Prompt 1: Describe Dataset ----
# This prompt helps a data scientist understand a new dataset.
# It asks the LLM to provide a thorough description.
@server.prompt()
def describe_dataset(dataset_name: str, columns: str, row_count: str) -> str:
    """Describe a dataset based on its metadata."""
    return (
        f"Please describe the following dataset:\n\n"
        f"Dataset Name: {dataset_name}\n"
        f"Number of Rows: {row_count}\n"
        f"Columns: {columns}\n\n"
        f"Please provide:\n"
        f"1. A summary of what this dataset likely contains\n"
        f"2. Expected data types for each column\n"
        f"3. Potential relationships between columns\n"
        f"4. Suggested exploratory data analysis (EDA) steps\n"
        f"5. Python code using pandas to load and inspect the data:\n"
        f"   - df.head(), df.info(), df.describe()\n"
        f"   - Check for missing values\n"
        f"   - Check for duplicates\n"
        f"6. Potential use cases for this dataset"
    )


# ---- Prompt 2: Find Outliers ----
# This prompt helps find outliers in a specific column.
# The method parameter defaults to "IQR" but can be changed
# to "z-score", "isolation-forest", etc.
@server.prompt()
def find_outliers(
    column_name: str,
    data_description: str,
    method: str = "IQR",
) -> str:
    """Find outliers in a dataset column."""
    return (
        f"Please help me find outliers in the following data:\n\n"
        f"Column: {column_name}\n"
        f"Data Description: {data_description}\n"
        f"Preferred Method: {method}\n\n"
        f"Please provide:\n"
        f"1. An explanation of the {method} method for detecting outliers\n"
        f"2. Python code using pandas to detect outliers:\n"
        f"   - Calculate the boundaries\n"
        f"   - Identify outlier rows\n"
        f"   - Print summary statistics\n"
        f"3. A visualization using matplotlib or seaborn:\n"
        f"   - Box plot of the column\n"
        f"   - Histogram with outlier boundaries marked\n"
        f"4. Recommendations for handling the outliers:\n"
        f"   - Remove them\n"
        f"   - Cap/clip them\n"
        f"   - Transform the data\n"
        f"   - Keep them (if they are valid)"
    )


# ---- Prompt 3: Correlation Analysis ----
# This prompt helps analyze the correlation between two columns.
# It suggests appropriate methods and visualizations.
@server.prompt()
def correlation_analysis(
    column1: str,
    column2: str,
    dataset_description: str,
) -> str:
    """Analyze correlation between two columns."""
    return (
        f"Please analyze the correlation between two variables:\n\n"
        f"Variable 1: {column1}\n"
        f"Variable 2: {column2}\n"
        f"Dataset: {dataset_description}\n\n"
        f"Please provide:\n"
        f"1. Which correlation method to use and why:\n"
        f"   - Pearson (linear, continuous data)\n"
        f"   - Spearman (monotonic, ordinal data)\n"
        f"   - Kendall (small datasets, ordinal data)\n"
        f"2. Python code to calculate the correlation:\n"
        f"   - Using pandas .corr() method\n"
        f"   - Using scipy.stats for p-value\n"
        f"3. Visualization code:\n"
        f"   - Scatter plot with trend line\n"
        f"   - Joint plot using seaborn\n"
        f"4. How to interpret the results:\n"
        f"   - Correlation strength (weak/moderate/strong)\n"
        f"   - Statistical significance (p-value)\n"
        f"   - Correlation vs causation warning"
    )


# ---- Run the server ----
if __name__ == "__main__":
    server.run()
