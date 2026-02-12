import json
import sys
import os
import csv
from urllib.parse import urlencode

def extract_clean_trace(trace_data):
    """Extract only the essential fields from a trace"""
    attrs = trace_data['attributes']

    return {
        'id': trace_data['id'],
        'span_id': attrs['span_id'],
        'trace_id': attrs['trace_id'],
        'model_name': attrs.get('model_name', 'N/A'),
        'input_original': attrs['input']['value'],
        'output_original': attrs['output']['value'],
        'url': construct_trace_url(attrs['trace_id'], attrs['span_id']),
        'list_url': construct_list_url(attrs['span_id'], attrs.get('start_ns', 0))
    }

def construct_trace_url(trace_id, span_id):
    """Construct direct URL to the trace"""
    return f"https://app.datadoghq.com/llm/traces/trace/{trace_id}?selectedTab=overview&spanId={span_id}"

def construct_list_url(span_id, start_ns):
    """Construct the Datadog LLM Observability list URL"""
    # Convert nanoseconds to milliseconds for start/end times
    start_ms = start_ns
    end_ms = start_ns + (15 * 60 * 1000)  # 15 minutes window

    base_url = "https://app.datadoghq.com/llm/traces"

    # Build query parameters
    params = {
        'query': '@ml_app:graphing-backend-investigations @event_type:span @parent_id:undefined',
        'agg_m': '@metrics.estimated_total_cost',
        'agg_m_source': 'base',
        'agg_t': 'sum',
        'expanded-view': 'default',
        'fromUser': 'false',
        'selectedTab': 'overview',
        'spanId': span_id,
        'viz': 'stream',
        'start': start_ms,
        'end': end_ms,
        'paused': 'false'
    }

    return f"{base_url}?{urlencode(params)}"

# Read the full traces file
with open('/Users/omar.nema/Desktop/promptRefinement/llm_traces_full.json', 'r') as f:
    data = json.load(f)

# Extract clean data for all traces
clean_traces = []
for trace in data.get('data', []):
    clean_traces.append(extract_clean_trace(trace))

# Save clean traces
with open('/Users/omar.nema/Desktop/promptRefinement/llm_traces_clean.json', 'w') as f:
    json.dump(clean_traces, f, indent=2)

# Save most recent trace
if clean_traces:
    with open('/Users/omar.nema/Desktop/promptRefinement/most_recent_llm_trace.json', 'w') as f:
        json.dump(clean_traces[0], f, indent=2)

# Save recent 10 traces
recent_10 = clean_traces[:10]
with open('/Users/omar.nema/Desktop/promptRefinement/recent_10_traces.json', 'w') as f:
    json.dump(recent_10, f, indent=2)

print(f"Extracted {len(clean_traces)} clean traces")
print(f"\nMost recent trace:")
if clean_traces:
    recent = clean_traces[0]
    print(f"  ID: {recent['id']}")
    print(f"  Model: {recent['model_name']}")
    print(f"  Direct URL: {recent['url']}")
    print(f"  List URL: {recent['list_url']}")

# Check if recent_10_traces_modified.json exists and create comparison files
modified_file = '/Users/omar.nema/Desktop/promptRefinement/recent_10_traces_modified.json'
if os.path.exists(modified_file):
    with open(modified_file, 'r') as f:
        modified_traces = json.load(f)

    # Create markdown comparison file
    md_file = '/Users/omar.nema/Desktop/promptRefinement/trace_comparison.md'
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("# LLM Trace Output Comparison\n\n")
        f.write("This file compares the original LLM outputs with new prompt outputs for each trace.\n\n")
        f.write("---\n\n")

        for i, trace in enumerate(modified_traces, 1):
            # Header with trace ID
            f.write(f"## Trace {i}: `{trace['id']}`\n\n")

            # Add trace URL
            f.write(f"**[View in Datadog]({trace['url']})**\n\n")

            # Original output section
            f.write(f"### Original Output\n\n")
            f.write(f"{trace['output_original']}\n\n")

            # New prompt outputs (support multiple prompts)
            prompt_keys = sorted([k for k in trace.keys() if k.startswith('output_new_prompt')])
            for prompt_key in prompt_keys:
                # Extract prompt number from key (e.g., "output_new_prompt1" -> "1")
                prompt_num = prompt_key.replace('output_new_prompt', '')
                f.write(f"### New Prompt {prompt_num} Output\n\n")
                f.write(f"{trace[prompt_key]}\n\n")

            f.write("---\n\n")

    print(f"\nCreated comparison markdown: {md_file}")

    # Find all output_new_prompt* fields and concatenate them
    csv_file = '/Users/omar.nema/Desktop/promptRefinement/comparison.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['input_original', 'output_original', 'output_modified'])
        writer.writeheader()

        for trace in modified_traces:
            # Collect all output_new_prompt* values
            output_parts = []
            for key in sorted(trace.keys()):
                if key.startswith('output_new_prompt'):
                    output_parts.append(trace.get(key, ''))

            writer.writerow({
                'input_original': trace.get('input_original', ''),
                'output_original': trace.get('output_original', ''),
                'output_modified': ' | '.join(output_parts) if output_parts else ''
            })

    print(f"Created comparison CSV: {csv_file}")
