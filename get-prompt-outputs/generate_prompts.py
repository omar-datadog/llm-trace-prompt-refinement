#!/usr/bin/env python3
"""
Generate full prompts for spawning agents from template and trace data.

This script:
1. Reads prompt templates from user_input/trace_prompt.md
2. Reads trace data from datasets/recent_10_traces.json
3. Generates complete prompts for all (trace, prompt) combinations
4. Outputs instructions for spawning agents

Usage:
    python get-prompt-outputs/generate_prompts.py [--prompt N]

    --prompt N: Optional. Generate prompts only for prompt N (e.g., --prompt 2)
                Default: generate for all prompts

Output:
    - Displays all prompts ready to be used with Task tool
    - Shows AGENT_MAPPING template to update in run_pipeline.py
"""

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASETS = PROJECT_ROOT / 'datasets'
USER_INPUT = PROJECT_ROOT / 'user_input'

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

def generate_full_prompt(prompt_template, trace_input):
    """Generate full prompt by substituting trace input."""
    # Check if placeholder exists in template
    placeholder = '[[use input from traces_sampled_for_ui.json]]'
    if placeholder in prompt_template:
        # Replace placeholder with actual trace input
        return prompt_template.replace(placeholder, trace_input)
    else:
        # Append trace input to the end of the prompt
        return f"{prompt_template}\n\n{trace_input}"

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
    print("PROMPT GENERATOR FOR AGENT SPAWNING")
    print("=" * 80)

    # Load prompts
    print("\nLoading prompt templates from user_input/trace_prompt.md...")
    prompts = extract_prompts(USER_INPUT / 'trace_prompt.md')
    print(f"Found {len(prompts)} prompt templates: {list(prompts.keys())}")

    if filter_prompt is not None:
        if filter_prompt not in prompts:
            print(f"Error: Prompt {filter_prompt} not found in templates")
            sys.exit(1)
        prompts = {filter_prompt: prompts[filter_prompt]}
        print(f"Filtering to PROMPT{filter_prompt} only")

    # Load traces
    print("\nLoading trace data from datasets/recent_10_traces.json...")
    with open(DATASETS / 'recent_10_traces.json', 'r') as f:
        traces = json.load(f)
    print(f"Found {len(traces)} traces")

    print("\n" + "=" * 80)
    print("GENERATED PROMPTS FOR AGENT SPAWNING")
    print("=" * 80)

    # Generate all prompts
    agent_count = 0
    for trace_idx, trace in enumerate(traces):
        for prompt_num in sorted(prompts.keys()):
            agent_count += 1
            full_prompt = generate_full_prompt(prompts[prompt_num], trace['input_original'])

            print(f"\n{'=' * 80}")
            print(f"TRACE {trace_idx} | PROMPT {prompt_num}")
            print(f"{'=' * 80}")
            print(f"Character count: {len(full_prompt)}")
            print(f"\nTo spawn this agent, use:")
            print(f"""
Task(
    subagent_type="general-purpose",
    description="Trace {trace_idx} Prompt {prompt_num}",
    model="haiku",
    run_in_background=True,
    prompt='''
{full_prompt}
'''
)
""")
            print(f"After spawning, save the agent ID for AGENT_MAPPING")
            print(f"Format: 'agent_id': ({trace_idx}, {prompt_num})")

    print("\n" + "=" * 80)
    print("AGENT_MAPPING TEMPLATE")
    print("=" * 80)
    print(f"\nTotal agents to spawn: {agent_count}")
    print("\nAfter spawning all agents, update run_pipeline.py with:")
    print("\nAGENT_MAPPING = {")

    for trace_idx in range(len(traces)):
        print(f"    # Trace {trace_idx}")
        agent_ids = ', '.join([f"'AGENT_ID_{trace_idx}_{p}': ({trace_idx}, {p})"
                               for p in sorted(prompts.keys())])
        print(f"    {agent_ids},")

    print("}")

    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("1. Spawn all agents using Task tool with prompts above")
    print("2. Replace AGENT_ID_X_Y placeholders with actual agent IDs")
    print("3. Update AGENT_MAPPING in run_pipeline.py")
    print("4. Run: python get-prompt-outputs/run_pipeline.py")
    print("=" * 80)

if __name__ == '__main__':
    main()
