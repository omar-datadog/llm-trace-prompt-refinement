#!/usr/bin/env python3
"""Generate prompts only for new traces (indices 3, 5-9)."""

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASETS = PROJECT_ROOT / 'datasets'
USER_INPUT = PROJECT_ROOT / 'user_input'

# Only process these trace indices (0-based)
NEW_TRACE_INDICES = [3, 5, 6, 7, 8, 9]

def extract_prompts(trace_prompt_file):
    """Extract all PROMPT sections from trace_prompt.md."""
    with open(trace_prompt_file, 'r') as f:
        content = f.read()

    prompts = {}
    pattern = r'<PROMPT(\d+)>(.*?)</PROMPT\1>'
    matches = re.findall(pattern, content, re.DOTALL)

    for num, prompt_text in matches:
        prompts[int(num)] = prompt_text.strip()

    return prompts

def main():
    print("=" * 80)
    print("GENERATING PROMPTS FOR 6 NEW TRACES")
    print("=" * 80)

    # Load prompts
    prompts = extract_prompts(USER_INPUT / 'trace_prompt.md')
    print(f"\nFound {len(prompts)} prompt templates")

    # Load traces
    with open(DATASETS / 'recent_10_traces.json', 'r') as f:
        traces = json.load(f)
    print(f"Total traces: {len(traces)}")
    print(f"Processing trace indices: {NEW_TRACE_INDICES}\n")

    # Generate prompts only for new traces
    for trace_idx in NEW_TRACE_INDICES:
        trace = traces[trace_idx]
        for prompt_num in sorted(prompts.keys()):
            prompt_template = prompts[prompt_num]
            full_prompt = prompt_template + "\n\n" + trace['input_original']

            print(f"{'=' * 80}")
            print(f"TRACE {trace_idx} | PROMPT {prompt_num}")
            print(f"{'=' * 80}")
            print(f"Trace ID: {trace['id']}")
            print(f"Dashboard: {trace['input_original'].split('**Dashboard name:**')[1].split('\\n')[0].strip() if '**Dashboard name:**' in trace['input_original'] else 'Unknown'}")
            print(f"Character count: {len(full_prompt)}")
            print()

if __name__ == '__main__':
    main()
