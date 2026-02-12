#!/usr/bin/env python3
"""
Complete pipeline to collect LLM outputs from spawned agents.

WORKFLOW:
1. Spawn agents manually using Claude Code Task tool with prompts from user_input/trace_prompt.md
2. Update AGENT_MAPPING below with the agent IDs
3. Run this script: python get-prompt-outputs/run_pipeline.py
4. Outputs saved to datasets/recent_10_traces_modified.json

Usage:
    python get-prompt-outputs/run_pipeline.py [--prompt N]

    --prompt N: Optional. Collect outputs only for prompt N (e.g., --prompt 2)
                Default: collect for all prompts

Run from project root: python get-prompt-outputs/run_pipeline.py
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASETS = PROJECT_ROOT / 'datasets'

# ============================================================================
# AGENT ID MAPPING
# ============================================================================
# Update this mapping after spawning agents via Task tool.
# Format: 'agent_id': (trace_index, prompt_number)
#
# 10 traces × 4 prompts = 40 agents
#
AGENT_MAPPING = {
    # Trace 0 (prompt1 updated 2026-02-12)
    'ae5df6b': (0, 1), 'ad7e040': (0, 2), 'a4e24b9': (0, 3), 'a057b2a': (0, 4),
    # Trace 1 (prompt1 updated 2026-02-12)
    'aec9571': (1, 1), 'a9d337c': (1, 2), 'ab8f246': (1, 3), 'af3be3b': (1, 4),
    # Trace 2 (prompt1 updated 2026-02-12)
    'a5d3486': (2, 1), 'a93d7a2': (2, 2), 'a37d8f7': (2, 3), 'a4cc3af': (2, 4),
    # Trace 3 (prompt1 updated 2026-02-12)
    'af63e33': (3, 1), 'a0c4e35': (3, 2), 'a24362b': (3, 3), 'a1cb546': (3, 4),
    # Trace 4 (prompt1 updated 2026-02-12)
    'ae4d0bf': (4, 1), 'a1ebda7': (4, 2), 'a08fe41': (4, 3), 'a947a27': (4, 4),
    # Trace 5 (prompt1 updated 2026-02-12)
    'a85cf71': (5, 1), 'ad4f628': (5, 2), 'a6a2b86': (5, 3), 'a8df2a4': (5, 4),
    # Trace 6 (prompt1 updated 2026-02-12)
    'abf876d': (6, 1), 'a8330d7': (6, 2), 'a2560dc': (6, 3), 'a8ee598': (6, 4),
    # Trace 7 (prompt1 updated 2026-02-12)
    'a059e18': (7, 1), 'ad679f8': (7, 2), 'a1af480': (7, 3), 'a2d69a0': (7, 4),
    # Trace 8 (prompt1 updated 2026-02-12)
    'a2a66bd': (8, 1), 'aec0c8d': (8, 2), 'a1a8f55': (8, 3), 'a156f84': (8, 4),
    # Trace 9 (prompt1 updated 2026-02-12)
    'a10c561': (9, 1), 'a1744bc': (9, 2), 'a404313': (9, 3), 'a23c42a': (9, 4),
}

# ============================================================================
# OUTPUT EXTRACTION
# ============================================================================

def extract_assistant_output(jsonl_path):
    """
    Extract the last assistant message with end_turn from a JSONL file.

    Agent outputs are stored in ~/.claude/projects/-Users-omar-nema-Desktop-promptRefinement/agent-{id}.jsonl
    Each JSONL line contains message data. We extract the final assistant text response.
    """
    try:
        with open(jsonl_path, 'r') as f:
            lines = f.readlines()

        # Parse all JSONL lines
        messages = [json.loads(line) for line in lines if line.strip()]

        # Find the last assistant message with stop_reason="end_turn"
        for msg in reversed(messages):
            if msg.get('type') == 'assistant':
                message_data = msg.get('message', {})
                if message_data.get('stop_reason') in ['end_turn', None]:
                    content = message_data.get('content', [])
                    if isinstance(content, list):
                        # Extract text from content blocks
                        text_parts = []
                        for block in content:
                            if block.get('type') == 'text':
                                text_parts.append(block.get('text', ''))
                        result = '\n'.join(text_parts).strip()
                        if result:
                            return result

        return ''
    except Exception as e:
        print(f"Error reading {jsonl_path}: {e}")
        return ''

# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main():
    # Parse command line arguments
    filter_prompt = None
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv):
            if arg == '--prompt' and i + 1 < len(sys.argv):
                try:
                    filter_prompt = int(sys.argv[i + 1])
                except ValueError:
                    print(f"Error: --prompt requires an integer value")
                    sys.exit(1)

    print("=" * 80)
    print("PROMPT OUTPUT COLLECTION PIPELINE")
    print("=" * 80)

    if filter_prompt is not None:
        print(f"Filtering to PROMPT{filter_prompt} only")

    # Load existing modified file if it exists, otherwise load source
    modified_file = DATASETS / 'recent_10_traces_modified.json'
    source_file = DATASETS / 'recent_10_traces.json'

    if modified_file.exists():
        print(f"\nLoading existing data from {modified_file}...")
        with open(modified_file, 'r') as f:
            traces = json.load(f)
    else:
        print(f"\nLoading source data from {source_file}...")
        with open(source_file, 'r') as f:
            traces = json.load(f)

    # Initialize output fields (only for missing ones)
    for trace in traces:
        for i in range(1, 5):
            field = f'output_new_prompt{i}'
            if field not in trace:
                trace[field] = ''

    base_path = Path.home() / '.claude' / 'projects' / '-Users-omar-nema-Desktop-promptRefinement'

    # Filter AGENT_MAPPING if specific prompt requested
    filtered_mapping = AGENT_MAPPING
    if filter_prompt is not None:
        filtered_mapping = {k: v for k, v in AGENT_MAPPING.items() if v[1] == filter_prompt}

    print(f"Collecting outputs from {len(filtered_mapping)} agents...")
    print("=" * 80)

    collected = 0
    failed = []

    for agent_id, (trace_idx, prompt_num) in sorted(filtered_mapping.items(), key=lambda x: (x[1][0], x[1][1])):
        jsonl_file = base_path / f'agent-{agent_id}.jsonl'

        if jsonl_file.exists():
            output = extract_assistant_output(jsonl_file)
            if output:
                field_name = f'output_new_prompt{prompt_num}'
                traces[trace_idx][field_name] = output
                collected += 1

                preview = output[:80].replace('\n', ' ')
                print(f"✓ Trace {trace_idx+1} P{prompt_num}: {len(output):4d} chars | {preview}...")
            else:
                print(f"✗ Trace {trace_idx+1} P{prompt_num}: No output found in {jsonl_file.name}")
                failed.append(agent_id)
        else:
            print(f"✗ Trace {trace_idx+1} P{prompt_num}: File not found: {jsonl_file.name}")
            failed.append(agent_id)

    print("=" * 80)
    print(f"\nCollected: {collected}/{len(filtered_mapping)} outputs")
    if failed:
        print(f"Failed: {len(failed)} agents: {failed}")
    print("=" * 80)

    # Save the modified JSON
    output_file = DATASETS / 'recent_10_traces_modified.json'
    print(f"\nSaving to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(traces, f, indent=2)

    print("✓ Done!")

    # Verify all fields are populated
    print("\nVerification:")
    print("-" * 80)
    for i, trace in enumerate(traces, 1):
        p1_len = len(trace.get('output_new_prompt1', ''))
        p2_len = len(trace.get('output_new_prompt2', ''))
        p3_len = len(trace.get('output_new_prompt3', ''))
        p4_len = len(trace.get('output_new_prompt4', ''))
        status = '✓' if all([p1_len > 0, p2_len > 0, p3_len > 0, p4_len > 0]) else '✗'
        print(f'Trace {i}: {status} P1={p1_len:4d} P2={p2_len:4d} P3={p3_len:4d} P4={p4_len:4d}')

    print("=" * 80)
    print("\nNEXT STEPS:")
    print("1. Review outputs in datasets/recent_10_traces_modified.json")
    print("2. Run extract_llm_traces.py to regenerate comparison files")
    print("3. View results in index.html")
    print("=" * 80)

if __name__ == '__main__':
    main()
