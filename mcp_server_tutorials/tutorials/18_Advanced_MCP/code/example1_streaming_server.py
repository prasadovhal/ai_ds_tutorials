"""
Example 1: Streaming MCP Server
================================
This server demonstrates how to send incremental results
while a long-running task is processing.

Instead of making the client wait for the entire result,
this server builds up results step by step and returns
a detailed progress report.

What you will learn:
    - How to simulate streaming with progress updates
    - How to build up results incrementally
    - How async/await works at a basic level in MCP
    - How to handle long-running tool operations

Why async is needed here:
    MCP's FastMCP framework uses async internally.
    When we use "async def" for a tool, it means:
    "This tool might need to wait for something."
    When we use "await", it means:
    "Pause here, let other things happen, then continue."

    Think of it like ordering food at a restaurant:
    - You place your order (start the task)
    - You chat with friends while waiting (other work happens)
    - The waiter brings your food (result arrives)
    - You eat (process the result)

How to run:
    poetry run mcp dev example1_streaming_server.py

How to test:
    Open MCP Inspector in your browser
    Go to the Tools tab
    Call "analyze_files" with files = "report.csv,data.json,log.txt"
    Watch the result build up with progress info
"""

# ============================================================
# STEP 1: Import required libraries
# ============================================================
# FastMCP is the main class for building MCP servers.
from mcp.server.fastmcp import FastMCP

# asyncio lets us use "await asyncio.sleep()" to simulate
# time-consuming work without blocking the entire program.
import asyncio

# time module to measure how long things take.
import time

# json module to format our results nicely.
import json

# ============================================================
# STEP 2: Create the server
# ============================================================
# We give our server a descriptive name.
# This name is sent to clients during initialization.
server = FastMCP("StreamingServer")

# ============================================================
# STEP 3: Define a helper function to simulate file processing
# ============================================================
# This function pretends to process a single file.
# In a real server, this might:
#   - Read a file from disk
#   - Parse its contents
#   - Run analysis (count lines, find patterns, etc.)
#   - Return a summary
#
# We use "async def" because we need "await asyncio.sleep()"
# to simulate the delay without blocking other operations.
async def process_single_file(file_name):
    """
    Simulate processing a single file.
    Returns a dictionary with file analysis results.
    """

    # Simulate processing time (0.5 seconds per file)
    # In a real server, this would be actual file processing.
    # await means "pause here for 0.5 seconds, but let other
    # things happen during that time."
    await asyncio.sleep(0.5)

    # Simulate different results based on file extension.
    # This is just for demonstration purposes.
    # In a real server, you would actually read and analyze the file.

    # Get the file extension (e.g., ".csv" from "report.csv")
    extension = ""
    if "." in file_name:
        extension = file_name.split(".")[-1]

    # Create a simulated result based on file type
    result = {}
    result["file_name"] = file_name
    result["status"] = "processed"

    if extension == "csv":
        result["type"] = "CSV Data File"
        result["rows"] = 1500
        result["columns"] = 12
        result["size_kb"] = 245

    elif extension == "json":
        result["type"] = "JSON Data File"
        result["objects"] = 89
        result["nested_depth"] = 3
        result["size_kb"] = 128

    elif extension == "txt":
        result["type"] = "Text File"
        result["lines"] = 340
        result["words"] = 5200
        result["size_kb"] = 42

    elif extension == "log":
        result["type"] = "Log File"
        result["entries"] = 2800
        result["errors"] = 15
        result["warnings"] = 42
        result["size_kb"] = 890

    elif extension == "py":
        result["type"] = "Python Script"
        result["lines"] = 150
        result["functions"] = 8
        result["classes"] = 2
        result["size_kb"] = 12

    else:
        result["type"] = "Unknown File Type"
        result["size_kb"] = 100

    return result


# ============================================================
# STEP 4: Define the streaming tool
# ============================================================
# This tool takes a comma-separated list of file names,
# processes each one, and builds up a progress report.
#
# KEY CONCEPT: Even though we cannot truly "stream" individual
# characters to the client in basic MCP, we CAN build up our
# result incrementally and return a detailed report that shows
# the progress of each step.
#
# We use "async def" because the tool needs to use "await"
# to call our async helper function.
@server.tool()
async def analyze_files(files: str) -> str:
    """
    Analyze a list of files and return a detailed progress report.

    Args:
        files: Comma-separated list of file names
               Example: "report.csv,data.json,log.txt"

    Returns:
        A detailed report showing progress and results for each file.
    """

    # Record the start time so we can measure total duration
    start_time = time.time()

    # Split the comma-separated string into a list of file names.
    # strip() removes any whitespace around each name.
    file_list = []
    for f in files.split(","):
        cleaned_name = f.strip()
        if cleaned_name:  # Skip empty strings
            file_list.append(cleaned_name)

    # Check if we got any files
    total_files = len(file_list)
    if total_files == 0:
        return "Error: No files provided. Please provide a comma-separated list of file names."

    # This list will hold the result from each processed file
    all_results = []

    # This list will hold the progress log
    progress_log = []

    # --------------------------------------------------------
    # Process each file one by one
    # --------------------------------------------------------
    for i in range(total_files):
        file_name = file_list[i]

        # Calculate progress percentage
        progress_percent = int(((i) / total_files) * 100)

        # Log the start of this file's processing
        log_entry = f"[{progress_percent}%] Processing file {i + 1}/{total_files}: {file_name}..."
        progress_log.append(log_entry)

        # Process the file (this is where the "waiting" happens)
        # await means "do this async operation and wait for it"
        result = await process_single_file(file_name)

        # Add the result to our collection
        all_results.append(result)

        # Log completion of this file
        done_entry = f"[{int(((i + 1) / total_files) * 100)}%] Completed: {file_name} ({result.get('type', 'Unknown')})"
        progress_log.append(done_entry)

    # --------------------------------------------------------
    # Build the final report
    # --------------------------------------------------------
    end_time = time.time()
    total_duration = round(end_time - start_time, 2)

    # Build the report as a formatted string
    report_lines = []

    # Header
    report_lines.append("=" * 60)
    report_lines.append("FILE ANALYSIS REPORT")
    report_lines.append("=" * 60)
    report_lines.append("")

    # Progress log section
    report_lines.append("--- Progress Log ---")
    for log_line in progress_log:
        report_lines.append(log_line)
    report_lines.append("")

    # Results section
    report_lines.append("--- File Details ---")
    for result in all_results:
        report_lines.append(f"\nFile: {result['file_name']}")
        report_lines.append(f"  Type: {result.get('type', 'Unknown')}")
        report_lines.append(f"  Size: {result.get('size_kb', 'N/A')} KB")
        report_lines.append(f"  Status: {result.get('status', 'Unknown')}")

        # Add type-specific details
        if result.get("type") == "CSV Data File":
            report_lines.append(f"  Rows: {result.get('rows', 'N/A')}")
            report_lines.append(f"  Columns: {result.get('columns', 'N/A')}")
        elif result.get("type") == "JSON Data File":
            report_lines.append(f"  Objects: {result.get('objects', 'N/A')}")
            report_lines.append(f"  Nesting Depth: {result.get('nested_depth', 'N/A')}")
        elif result.get("type") == "Text File":
            report_lines.append(f"  Lines: {result.get('lines', 'N/A')}")
            report_lines.append(f"  Words: {result.get('words', 'N/A')}")
        elif result.get("type") == "Log File":
            report_lines.append(f"  Entries: {result.get('entries', 'N/A')}")
            report_lines.append(f"  Errors: {result.get('errors', 'N/A')}")
            report_lines.append(f"  Warnings: {result.get('warnings', 'N/A')}")
        elif result.get("type") == "Python Script":
            report_lines.append(f"  Lines: {result.get('lines', 'N/A')}")
            report_lines.append(f"  Functions: {result.get('functions', 'N/A')}")
            report_lines.append(f"  Classes: {result.get('classes', 'N/A')}")

    # Summary section
    report_lines.append("")
    report_lines.append("--- Summary ---")
    report_lines.append(f"Total files processed: {total_files}")
    report_lines.append(f"Total duration: {total_duration} seconds")
    report_lines.append(f"Average time per file: {round(total_duration / total_files, 2)} seconds")
    report_lines.append("=" * 60)

    # Join all lines into one big string
    final_report = "\n".join(report_lines)

    return final_report


# ============================================================
# STEP 5: Define a simpler streaming-style tool
# ============================================================
# This tool demonstrates streaming by counting items and
# reporting progress for each one.
@server.tool()
async def count_with_progress(count_to: int) -> str:
    """
    Count from 1 to a given number, reporting progress along the way.

    This demonstrates how a tool can take time and report
    incremental progress. Each count step takes 0.3 seconds.

    Args:
        count_to: The number to count up to (max 20)

    Returns:
        A progress report showing each step.
    """

    # Limit the count to prevent very long operations
    if count_to > 20:
        count_to = 20

    if count_to < 1:
        return "Error: count_to must be at least 1."

    # Build up the progress report step by step
    steps = []

    for i in range(1, count_to + 1):
        # Simulate work for each step
        await asyncio.sleep(0.3)

        # Calculate progress
        percent = int((i / count_to) * 100)

        # Create a visual progress bar
        bar_length = 20
        filled = int(bar_length * i / count_to)
        bar = "#" * filled + "-" * (bar_length - filled)

        # Add this step to our report
        step_report = f"Step {i:2d}/{count_to} [{bar}] {percent}%"
        steps.append(step_report)

    # Add completion message
    steps.append("")
    steps.append(f"Done! Counted from 1 to {count_to}.")

    return "\n".join(steps)


# ============================================================
# STEP 6: Define a data processing tool with chunked results
# ============================================================
@server.tool()
async def process_data_chunks(data: str, chunk_size: int) -> str:
    """
    Process a text by splitting it into chunks and analyzing each chunk.

    This simulates how a real data processing pipeline works:
    data comes in, gets split into manageable chunks, each chunk
    is processed, and results are aggregated.

    Args:
        data: The text data to process
        chunk_size: Number of words per chunk

    Returns:
        A chunk-by-chunk analysis report.
    """

    # Split data into words
    words = data.split()
    total_words = len(words)

    if total_words == 0:
        return "Error: No data provided."

    if chunk_size < 1:
        chunk_size = 1

    # Split words into chunks
    chunks = []
    for i in range(0, total_words, chunk_size):
        chunk = words[i:i + chunk_size]
        chunks.append(chunk)

    total_chunks = len(chunks)

    # Process each chunk
    report_lines = []
    report_lines.append("DATA PROCESSING REPORT")
    report_lines.append("=" * 50)
    report_lines.append(f"Total words: {total_words}")
    report_lines.append(f"Chunk size: {chunk_size} words")
    report_lines.append(f"Total chunks: {total_chunks}")
    report_lines.append("")

    total_characters = 0

    for i in range(total_chunks):
        chunk = chunks[i]

        # Simulate processing time
        await asyncio.sleep(0.2)

        # Analyze this chunk
        chunk_text = " ".join(chunk)
        char_count = len(chunk_text)
        word_count = len(chunk)
        total_characters = total_characters + char_count

        # Calculate progress
        percent = int(((i + 1) / total_chunks) * 100)

        # Add chunk result to report
        report_lines.append(f"Chunk {i + 1}/{total_chunks} [{percent}%]:")
        report_lines.append(f"  Words: {word_count}")
        report_lines.append(f"  Characters: {char_count}")
        report_lines.append(f"  Preview: \"{chunk_text[:50]}...\"" if len(chunk_text) > 50 else f"  Content: \"{chunk_text}\"")
        report_lines.append("")

    # Final summary
    report_lines.append("=" * 50)
    report_lines.append("PROCESSING COMPLETE")
    report_lines.append(f"Total words processed: {total_words}")
    report_lines.append(f"Total characters: {total_characters}")
    report_lines.append(f"Chunks processed: {total_chunks}")

    return "\n".join(report_lines)


# ============================================================
# STEP 7: Run the server
# ============================================================
# The if __name__ == "__main__" guard ensures the server only
# starts when you run this file directly.
if __name__ == "__main__":
    # Start the server
    # It will listen for MCP connections via stdio transport
    server.run()
