<PROMPT1>
You are going to write a summary for a potential issue in a Datadog dashboard.

Summarize this anomaly issue in a structured, scannable format. Bold key scope indicators (service names, cells, clusters, metric types). Output ONLY these three sections (TIME, ONE-LINER, DETAILS) with no additional commentary, analysis, or notes or preamble (do not say "based on the data... for example, just give me the structured output below").

Output format:
TIME: [start] to [end] ([duration])
ONE-LINER: [One super-short sentence describing scope - e.g., "Kafka lag across 3 cells" or "Network saturation on bond cluster"]. Do not mention more than 2 items, if there are more that are relevant to the scope generalize it.

DETAILS:
In **exactly three bullets**:
- **Bullet 1** (MAX 10 WORDS): What shifted - the primary metric change with direction
- **Bullet 2** (MAX 10 WORDS): Why it matters - the operational impact or consequence
- **Bullet 3** (MAX 10 WORDS): What to investigate - specific action or check for SRE

Each bullet should be 7-10 words ideal. Do not literally say "what shifted" etc as a header, just provide the information. For instantaneous anomalies (single timestamp), include "instantaneous" or "instant" in bullet 1. DO NOT INCLUDE ANY SPECULATIVE INFORMATION, ONLY DEFINITIVE INFO.

## Bullet 3 Investigation Guidelines

The third bullet should tell the SRE what to check, review, or investigate. Examples:
- "Check [specific component] health and [related metric]"
- "Review [service] logs for [specific error pattern]"
- "Investigate [upstream/downstream dependency] performance"
- "Verify [configuration] settings on [affected scope]"

Be specific with scope (org_id, cluster, service, pod) when relevant. Focus on the most logical first investigation step based on the anomaly type.


</PROMPT1>

<PROMPT2>
  You are going to write a summary for a potential issue in a Datadog dashboard.

  Summarize this anomaly issue in a structured, scannable format. Bold key scope indicators (service names, cells, clusters, metric types). Output ONLY these three sections (TIME, ONE-LINER, DETAILS) with no additional commentary, analysis, or notes or preamble (do not say "based on the data... for example, just give me the structured output below").

  Output format:
  TIME: [start] to [end] ([duration])
  ONE-LINER: [One super-short sentence describing scope - e.g., "Kafka lag across 3 cells" or "Network saturation on bond cluster"]. Do not mention more than 2 items, if there are more that are relevant to the scope generalize it.

  DETAILS:
  In **MAX three bullets that are MAX 12 WORDS per bullet**: what shifted, who/what it touches, and why it matters. Two bullets ideal, 7-9 words ideal. Do not literally say "what shifted" etc as a header, just explain what actually shifted for ex. Group related information but don't cram too much into one bullet.
  - For instantaneous anomalies (single timestamp), include "instantaneous" or "instant" in first bullet
  DO NOT INCLUDE ANY SPECULATIVE INFORMATION, ONLY DEFINITIVE INFO.

   

</PROMPT2>

<PROMPT3>
    You are going to write a summary for a potential issue in a Datadog dashboard.

  Summarize this anomaly issue in a structured, scannable format. Bold key scope indicators (service names, cells, clusters, metric types). Output ONLY these three sections (TIME, ONE-LINER, DETAILS) with no additional commentary, analysis, or notes or preamble (do not say "based on the data... for example, just give me the structured output below").


  Output format:
  TIME: [start] to [end] ([duration])
  ONE-LINER: [One super-short sentence describing scope - e.g., "Kafka lag across 3 cells" or "Network saturation on bond cluster"]. Do not mention more than 2 items, if there are more that are relevant to the scope generalize it.

  DETAILS:
  In **MAX three bullets that are MAX 10 WORDS per bullet**: what shifted, who/what it touches, and why it matters. Two bullets ideal, 7 words ideal. Do not literally say "what shifted" etc as a header, just explain what actually shifted for ex. Group related information but don't cram too much into one bullet. DO NOT INCLUDE ANY SPECULATIVE INFORMATION, ONLY DEFINITIVE INFO.

  

</PROMPT3>

<PROMPT4>
    You are going to write a ONE-LINER summary for a potential issue in a Datadog dashboard. Output ONLY these twk sections (TIME, ONE-LINER) with no additional commentary, analysis, notes, or preamble (do not say "based on the data... for example, just give me the structured output below").


  Output format:
  TIME: [start] to [end] ([duration])
  ONE-LINER: [One super-short sentence describing scope - e.g., "Kafka lag across 3 cells" or "Network saturation on bond cluster"]. Do not mention more than 2 items, if there are more that are relevant to the scope generalize it.

 
</PROMPT4>


---

## INSTRUCTIONS FOR CLAUDE CODE

### Overview
This document contains multiple prompts (PROMPT1, PROMPT2, etc.) that need to be tested against the anomaly data in `traces_sampled_for_ui.json`. For each prompt, you will:
1. Substitute the placeholder `[[use input from traces_sampled_for_ui.json]]` with actual `input_original` values from the JSON file
2. Run LLM calls using subagents (completely naively - only the prompt, nothing else)
3. Generate a new JSON file with the results

### Step-by-Step Process

1. **Read the input files:**
   - Read `trace_prompt.md` to extract all PROMPT sections (PROMPT1, PROMPT2, etc.)
   - Read `traces_sampled_for_ui.json` to get the list of traces with their `input_original` and `output_original` fields

2. **For each PROMPT in trace_prompt.md:**
   - Identify the prompt number (e.g., PROMPT1 → prompt number 1)
   - Extract the full prompt text
   - Find the placeholder `[[use input from traces_sampled_for_ui.json]]` in the prompt

3. **For each trace in traces_sampled_for_ui.json:**
   - Take the `input_original` field from the trace
   - Replace `[[use input from traces_sampled_for_ui.json]]` in the prompt with this `input_original`
   - This creates a complete prompt ready for LLM execution

4. **Run LLM calls using subagents:**
   - For each trace, spin up a subagent
   - The subagent should receive ONLY the complete prompt (with `input_original` substituted)
   - Do NOT add any additional instructions, context, or modifications
   - The subagent should execute the LLM call completely naively - just pass the prompt as-is
   - Capture the LLM output

5. **Create the output file:**
   - Start with a copy of `traces_sampled_for_ui.json`
   - For each trace, add a new field: `output_new_prompt[x]` where `x` is the prompt number
   - For example, for PROMPT1, add `output_new_prompt1` containing the LLM output
   - For PROMPT2, add `output_new_prompt2`, etc.
   - Save this as `recent_10_traces_modified.json`

### Example Structure

If you have PROMPT1 and PROMPT2, and 3 traces in the JSON:

**Input (traces_sampled_for_ui.json):**
```json
[
  {
    "id": "123",
    "input_original": "Analyze...",
    "output_original": "Summary..."
  },
  ...
]
```

**Output (recent_10_traces_modified.json):**
```json
[
  {
    "id": "123",
    "input_original": "Analyze...",
    "output_original": "Summary...",
    "output_new_prompt1": "LLM output for PROMPT1",
    "output_new_prompt2": "LLM output for PROMPT2"
  },
  ...
]
```

### Critical Requirements

- **Subagent execution must be completely naive:** Each subagent receives ONLY the complete prompt (with substituted `input_original`). No additional instructions, system prompts, or modifications.
- **Preserve all original fields:** The output JSON must contain all original fields from `traces_sampled_for_ui.json` plus the new `output_new_prompt[x]` fields.
- **Process all prompts:** Iterate through ALL PROMPT sections found in `trace_prompt.md`.
- **Process all traces:** For each prompt, process ALL traces in `traces_sampled_for_ui.json`.
