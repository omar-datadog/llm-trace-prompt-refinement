# get-prompt-outputs

Scripts to run prompt variations against LLM traces and collect outputs for analysis.

## Overview

This folder contains the pipeline for testing multiple prompt formats against anomaly data. The workflow spawns LLM agents with different prompts, collects their outputs, and assembles them into a structured dataset for comparison.

## Files

### `generate_prompts.py`
**Helper script** - Generates complete prompts for spawning agents.

**Purpose:**
- Reads prompt templates from `user_input/trace_prompt.md`
- Reads trace data from `datasets/recent_10_traces.json`
- Generates all (trace × prompt) combinations with full prompts
- Outputs Task tool commands ready to use for spawning agents
- Provides AGENT_MAPPING template for run_pipeline.py

**Usage:**
```bash
# Run from project root
python get-prompt-outputs/generate_prompts.py
```

**Output:**
- Displays all prompts with Task tool commands
- Shows AGENT_MAPPING template to update in run_pipeline.py
- No files created - output is display-only for copy-paste

---

### `run_pipeline.py`
**Main script** - Collects agent outputs from spawned agents and assembles into `datasets/recent_10_traces_modified.json`.

**Purpose:**
- Extracts LLM outputs from agent JSONL files in `~/.claude/projects/`
- Maps agent IDs to (trace_index, prompt_number) pairs
- Populates `output_new_prompt1`, `output_new_prompt2`, `output_new_prompt3`, `output_new_prompt4` fields for each trace
- Verifies all outputs collected successfully

**Usage:**
```bash
# Run from project root
python get-prompt-outputs/run_pipeline.py
```

**Prerequisites:**
1. Agents must be spawned first using Claude Code Task tool
2. Update `AGENT_MAPPING` in script with actual agent IDs
3. Agent outputs stored in `~/.claude/projects/-Users-omar-nema-Desktop-promptRefinement/agent-*.jsonl`

---

## Workflow

### Step 1: Prepare Prompts
Edit `user_input/trace_prompt.md` with your prompt variations:
- `<PROMPT1>...</PROMPT1>` - First format variation
- `<PROMPT2>...</PROMPT2>` - Second format variation
- `<PROMPT3>...</PROMPT3>` - Third format variation
- `<PROMPT4>...</PROMPT4>` - Fourth format variation

Each prompt should include the placeholder:
```
Anomaly input: [[use input from traces_sampled_for_ui.json]]
```

### Step 2: Generate Full Prompts
Run the helper script to generate all prompts:

```bash
python get-prompt-outputs/generate_prompts.py
```

This displays:
- Complete prompts for all (trace × prompt) combinations
- Task tool commands ready to copy-paste
- AGENT_MAPPING template for step 4

### Step 3: Spawn Agents
Copy-paste the Task tool commands from generate_prompts.py output into Claude Code.

Example output from script:
```python
Task(
    subagent_type="general-purpose",
    description="Trace 0 Prompt 1",
    model="haiku",
    run_in_background=True,
    prompt='''
[Full PROMPT1 with trace 0's input_original substituted]
'''
)
```

**Save agent IDs** returned by each Task call (format: `a1b2c3d`)

Repeat for all combinations (e.g., 4 traces × 4 prompts = 16 agents)

### Step 4: Update Agent Mapping
Edit `run_pipeline.py` and update the `AGENT_MAPPING` dictionary with actual agent IDs:

```python
AGENT_MAPPING = {
    # Trace 0
    'a1b2c3d': (0, 1), 'e4f5g6h': (0, 2), 'i7j8k9l': (0, 3), 'm0n1o2p': (0, 4),
    # Trace 1
    'q3r4s5t': (1, 1), 'u6v7w8x': (1, 2), 'y9z0a1b': (1, 3), 'c2d3e4f': (1, 4),
    # ... continue for all traces
}
```

Format: `'agent_id': (trace_index, prompt_number)`
- `trace_index`: 0-based (0, 1, 2, 3...)
- `prompt_number`: 1-based (1, 2, 3, 4...)

### Step 5: Collect Outputs
Wait for all agents to complete, then run:

```bash
python get-prompt-outputs/run_pipeline.py
```

This will:
1. Read agent outputs from `~/.claude/projects/-Users-omar-nema-Desktop-promptRefinement/agent-*.jsonl`
2. Extract the final assistant message from each JSONL file
3. Populate fields in `datasets/recent_10_traces_modified.json`
4. Display verification summary

### Step 6: Generate Comparison Files (Optional)
Run the extraction script to create human-readable comparisons:

```bash
python extract_llm_traces.py
```

This generates:
- `datasets/trace_comparison.md` - Markdown comparison view
- `datasets/comparison.csv` - CSV export for analysis

---

## Output Structure

### `datasets/recent_10_traces_modified.json`
Main output file containing all prompt variation outputs.

**Structure:**
```json
[
  {
    "id": "3916214930736637988",
    "span_id": "3916214930736637988",
    "trace_id": "698cedce00000000e8b762af57b9d5d9",
    "model_name": "gpt-4o-mini",
    "input_original": "Analyze the following anomalies...",
    "output_original": "During a 13-minute period...",
    "output_new_prompt1": "TIME: 20:33 to 20:46...",
    "output_new_prompt2": "TIME: 20:33 to 20:46...",
    "output_new_prompt3": "TIME: 20:33 to 20:46...",
    "output_new_prompt4": "TIME: 20:33 to 20:46...",
    "url": "https://app.datadoghq.com/llm/traces/...",
    "list_url": "https://app.datadoghq.com/llm/traces?..."
  },
  // ... more traces
]
```

**Fields:**
- `id`, `span_id`, `trace_id` - Datadog trace identifiers
- `model_name` - LLM model used (e.g., gpt-4o-mini)
- `input_original` - Raw anomaly description (unchanged)
- `output_original` - Original LLM summary (unchanged)
- `output_new_prompt1` - Output from PROMPT1 variation
- `output_new_prompt2` - Output from PROMPT2 variation
- `output_new_prompt3` - Output from PROMPT3 variation
- `output_new_prompt4` - Output from PROMPT4 variation
- `url` - Direct link to trace in Datadog UI
- `list_url` - Link to trace list view

---

## Expected Output Format

Each `output_new_prompt*` field should contain formatted anomaly summaries based on the prompt template.

**Example PROMPT1 output:**
```
TIME: 20:33 to 20:46 UTC (13 minutes)

ONE-LINER: Span throughput and network traffic spike on trace-spans-meta-extractor

SUMMARY: The trace-spans-meta-extractor service experienced simultaneous elevated
span ingestion and inbound network traffic during a 13-minute window.

DETAILS:
- Primary issue: Span event rate elevated for org_id:46426
- Scope: Affects 3 services in us1.prod.dog datacenter
- Pattern: Correlated anomalies suggest traffic surge
```

**Example PROMPT2 output:**
```
TIME: 20:33 to 20:46 UTC (13 minutes)

ONE-LINER: Elevated span sampling and inbound network traffic on trace-spans-meta-extractor

DETAILS:
- Primary issue: Span sampling rate spiked on trace-spans-meta-extractor
- Secondary impact: Network ingress traffic anomaly correlates with span volume
- Notable context: Anomalies clustered in 13-minute window
```

**Example PROMPT3 output:**
```
TIME: 20:33 to 20:46 UTC (13 minutes)

ONE-LINER: Span processing surge on trace-spans-meta-extractor

DETAILS:
- Span sampling rate spike for org_id:46426
- Affects trace-spans-meta-extractor in us1.prod.dog datacenter
- Simultaneous metrics suggest correlated processing surge
```

---

## Verification

After running `run_pipeline.py`, verify outputs:

```
Verification:
--------------------------------------------------------------------------------
Trace 1: ✓ P1= 844 P2= 541 P3= 452 P4= 161
Trace 2: ✓ P1= 650 P2= 459 P3= 360 P4= 158
Trace 3: ✓ P1= 618 P2= 372 P3= 362 P4= 117
Trace 4: ✓ P1= 809 P2= 475 P3= 405 P4= 183
```

**Status indicators:**
- `✓` - All prompts collected successfully
- `✗` - One or more prompts missing (check agent IDs)

**Character counts:**
- P1, P2, P3, P4 show output length in characters
- Expected range varies by prompt format:
  - P1 (structured): ~600-900 chars
  - P2 (concise): ~400-600 chars
  - P3 (minimal): ~350-450 chars
  - P4 (ultra-minimal): ~100-200 chars
- Empty (0 chars) indicates collection failure

---

## Troubleshooting

### Issue: "File not found: agent-*.jsonl"
**Cause:** Agent hasn't completed or agent ID incorrect

**Fix:**
1. Check agent status in Claude Code (may still be running)
2. Verify agent ID is correct in `AGENT_MAPPING`
3. Check path: `~/.claude/projects/-Users-omar-nema-Desktop-promptRefinement/`

### Issue: "No output found in agent-*.jsonl"
**Cause:** Agent completed but response extraction failed

**Fix:**
1. Manually inspect JSONL file to verify content exists
2. Check for errors in agent execution
3. Verify agent received correct prompt

### Issue: Empty output (0 chars) for a prompt
**Cause:** Agent failed or returned empty response

**Fix:**
1. Re-spawn agent with same prompt
2. Update `AGENT_MAPPING` with new agent ID
3. Re-run `run_pipeline.py`

---

## Notes

- **Agent storage:** Outputs stored in `~/.claude/projects/-Users-omar-nema-Desktop-promptRefinement/agent-{id}.jsonl`
- **JSONL format:** Each line is JSON; script extracts final assistant message with `stop_reason="end_turn"`
- **Parallel execution:** All 30 agents can be spawned simultaneously for faster processing
- **Idempotent:** Safe to re-run `run_pipeline.py` multiple times with updated agent IDs
