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
# 10 traces × 5 prompts = 50 agents
#
AGENT_MAPPING = {
    # Trace 0 (updated 2026-02-12 - complete pipeline re-run)
    'ad9268a': (0, 1), 'a0deb0a': (0, 2), 'a7d224b': (0, 3), 'a6bf1ed': (0, 4), 'a2828f5': (0, 5),
    # Trace 1 (updated 2026-02-12 - complete pipeline re-run)
    'a390db0': (1, 1), 'a177a46': (1, 2), 'a93f190': (1, 3), 'a741813': (1, 4), 'ad22b75': (1, 5),
    # Trace 2 (updated 2026-02-12 - complete pipeline re-run)
    'a211a0e': (2, 1), 'a072aab': (2, 2), 'ae0507f': (2, 3), 'af37efa': (2, 4), 'ab7574e': (2, 5),
    # Trace 3 (updated 2026-02-12 - complete pipeline re-run)
    'aed204d': (3, 1), 'ade34dd': (3, 2), 'afb4948': (3, 3), 'acc6716': (3, 4), 'a683820': (3, 5),
    # Trace 4 (updated 2026-02-12 - complete pipeline re-run)
    'a10ac2a': (4, 1), 'a33f086': (4, 2), 'a0811f5': (4, 3), 'afb0a34': (4, 4), 'a3c1ddf': (4, 5),
    # Trace 5 (updated 2026-02-12 - complete pipeline re-run)
    'a1a3114': (5, 1), 'ae68436': (5, 2), 'a0f2c1b': (5, 3), 'a3c5b0f': (5, 4), 'a09e27c': (5, 5),
    # Trace 6 (updated 2026-02-12 - complete pipeline re-run)
    'af0526e': (6, 1), 'ae10815': (6, 2), 'ade3a8d': (6, 3), 'a01a07e': (6, 4), 'aa36ee0': (6, 5),
    # Trace 7 (updated 2026-02-12 - complete pipeline re-run)
    'a72f168': (7, 1), 'a3089e0': (7, 2), 'a79fe9e': (7, 3), 'a4eff0f': (7, 4), 'a944b37': (7, 5),
    # Trace 8 (updated 2026-02-12 - complete pipeline re-run)
    'aefd0ef': (8, 1), 'a356834': (8, 2), 'ae5fbfe': (8, 3), 'afb0106': (8, 4), 'a0f6e70': (8, 5),
    # Trace 9 (updated 2026-02-12 - complete pipeline re-run)
    'adee186': (9, 1), 'a95a2d8': (9, 2), 'a370e8c': (9, 3), 'a6d88cf': (9, 4), 'a1671ac': (9, 5),
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
        for i in range(1, 6):
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
        p5_len = len(trace.get('output_new_prompt5', ''))
        status = '✓' if all([p1_len > 0, p2_len > 0, p3_len > 0, p4_len > 0, p5_len > 0]) else '✗'
        print(f'Trace {i}: {status} P1={p1_len:4d} P2={p2_len:4d} P3={p3_len:4d} P4={p4_len:4d} P5={p5_len:4d}')

    print("=" * 80)
    print("\nNEXT STEPS:")
    print("1. Review outputs in datasets/recent_10_traces_modified.json")
    print("2. Run extract_llm_traces.py to regenerate comparison files")
    print("3. View results in index.html")
    print("=" * 80)

if __name__ == '__main__':
    main()
