<PROMPT1>
    You are going to write a summary for a potential issue in a Datadog dashboard. Your output will be in JSON format.

  Summarize this anomaly issue in a structured, scannable format. Bold key scope indicators (service names, cells, clusters, metric types). Output ONLY these three sections (TIME, ONE-LINER, DETAILS) with NO additional commentary, analysis, or notes or  preamble (do not say "based on the data... for example, just give me the structured output below").


  Output format:
  TIME: [start] to [end] ([duration])
  ONE-LINER: [One super-short sentence describing scope - e.g., "Kafka lag across 3 cells" or "Network saturation on bond cluster"]
  SUMMARY: [One detailed sentence explaining the pattern]
  DETAILS:
  - [Bullet 1: Primary issue - keep it short and focused]
  - [Bullet 2: Secondary impacts - avoid listing more than 3-4 items]
  - [Bullet 3: Notable context - one clear point]
  Limit to exactly 3 bullets. Keep each bullet SHORT and scannable - avoid long lists or complex sentences. Group related information but don't cram too much into one bullet.



</PROMPT1>

<PROMPT2>
    You are going to write a summary for a potential issue in a Datadog dashboard.

  Summarize this anomaly issue in a structured, scannable format. Bold key scope indicators (service names, cells, clusters, metric types). Output ONLY these three sections (TIME, ONE-LINER, DETAILS) with no additional commentary, analysis, or notes or  preamble (do not say "based on the data... for example, just give me the structured output below").

  Output format:
  TIME: [start] to [end] ([duration])
  ONE-LINER: [One super-short sentence describing scope - e.g., "Kafka lag across 3 cells" or "Network saturation on bond cluster"]. Do not mention more than 2 items, if there are more that are relevant to the scope generalize it.
  DETAILS:
  - [Bullet 1: Primary issue - keep it short and focused]
  - [Bullet 2: Secondary impacts - avoid listing more than 3-4 items]
  - [Bullet 3: Notable context - one clear point]
  Limit to exactly 3 bullets. Keep each bullet SHORT and scannable - avoid long lists or complex sentences. Group related information but don't cram too much into one bullet.

   

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
