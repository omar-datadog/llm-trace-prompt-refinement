# LLM Trace Prompt Refinement

A tool for testing and comparing different prompts on LLM Observability traces from Datadog.

## Overview

This project fetches LLM traces from Datadog's LLM Observability product and tests different prompt formats against them to compare outputs. It's designed for prompt engineering and evaluation workflows.

## Features

- **Fetch LLM traces** from Datadog LLM Observability API
- **Extract clean trace data** with just the essential fields
- **Test multiple prompts** against the same traces
- **Generate comparison files** in JSON, CSV, and Markdown formats
- **Direct links** to traces in Datadog UI

## Setup

1. Copy `.env.example` to `.env` and add your Datadog credentials:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your Datadog API credentials:
   ```
   DD_API_KEY=your_api_key_here
   DD_APP_KEY=your_application_key_here
   DD_SITE=datadoghq.com
   ```

## Usage

### Fetching Traces

Run the extraction script to fetch the latest LLM traces:

```bash
python3 extract_llm_traces.py
```

This will generate:
- `llm_traces_full.json` - Raw API response
- `llm_traces_clean.json` - All traces with clean format
- `most_recent_llm_trace.json` - Just the most recent trace
- `recent_10_traces.json` - 10 most recent traces

### Testing Prompts

1. Define your prompts in `trace_prompt.md` following the format:
   ```
   PROMPT1:
       Your prompt text here
       Use [[use input from recent_10_traces.json]] as placeholder

   PROMPT2:
       Another prompt...
   ```

2. Run the prompts against traces (follow instructions in `trace_prompt.md`)

3. The script will generate:
   - `recent_10_traces_modified.json` - Traces with new prompt outputs
   - `trace_comparison.md` - Side-by-side comparison in readable format
   - `comparison.csv` - CSV export for analysis

## Output Format

### JSON Fields

Each trace includes:
- `id` - Trace ID
- `span_id` - Span ID
- `trace_id` - Full trace ID
- `model_name` - LLM model used
- `input_original` - Original input prompt
- `output_original` - Original LLM output
- `url` - Direct link to trace in Datadog
- `list_url` - Link to trace list view
- `output_new_prompt1` - Output from new prompt (when testing)

## Files

- `extract_llm_traces.py` - Main extraction and processing script
- `trace_prompt.md` - Prompt definitions and instructions
- `.env.example` - Template for environment variables
- `.gitignore` - Git ignore rules (excludes `.env`)

## Requirements

- Python 3.6+
- Datadog API credentials (API key + Application key)
- Access to Datadog LLM Observability

## License

MIT
