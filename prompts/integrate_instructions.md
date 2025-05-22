**Objective:**
Transform raw, unstructured thoughts, ideas, and reflections (provided as input text) into a series of clearly defined "Integration Directives." These directives are intended for a downstream agent (human or AI) to efficiently and **directly integrate** the information into a pre-existing Personal Knowledge Management (PKM) system, such as Obsidian. The output should facilitate **precise content placement** into specific existing documents.

**Context / Input Data:**
You will be provided with:
1.  A block of text representing raw thoughts, dictation, or brainstorming (`[Your Raw Thoughts/Dictation]`). This will be appended after the main prompt and a separator.
2.  A list of pre-defined high-level projects or contexts within the PKM system (e.g., `[Project Name 1]`).

**My list of projects**
phd_thesis.md

**Note:** The list above (`phd_thesis.md`) is an example.
Your actual list of projects will be passed to the LLM during runtime.

**Instructions:**
1.  **Analyze the Input Text:** Carefully read `[Your Raw Thoughts/Dictation]` to identify distinct ideas, reflections, tasks, comments related to specific projects, or new content generation prompts.
2.  **Attribute to Projects:** For each distinct piece of information, determine which of the provided `[Project Name X]` it best relates to.
3.  **Determine Integration Specificity:**
    *   For existing projects like `[Project Name 1]` (e.g., a thesis), identify *where* the information should be integrated (e.g., "Chapter X Outline," "Introduction Section," "Methodology Notes").
4.  **Formulate Directives:** For each identified piece of information, create an "Integration Directive" with the following structure (see "Required Output Format" below).
5.  **Define Agent Action:** The "Agent Action" should be an **extremely clear, concise, and direct imperative statement.** Focus strictly on *what content to place and where*, avoiding any elaborate explanation or justification. (e.g., "Insert sentence into `Introduction Section`," "Add image placeholder to `Chapter 3`," "Append TODO comment to `Qubit Stability Notes`," "Create new note for Y").
6.  **Extract Content Details:** The "Content/Thought Details" section should accurately and comprehensively capture the relevant snippet or essence of the thought from the input text, often in bullet points for clarity.
7.  **Focus on Actionability:** The primary goal is to make it easy for a downstream agent to act on these directives without needing to re-interpret the original raw thoughts.

**Important Rules / Constraints:**
*   **Focus on Direct Placement & Conciseness:** The agent's output, particularly the `Agent Action` and the overall structure, *must* be as concise as possible. **Do NOT generate paragraphs of explanatory text or elaborate on the reasoning behind the integration.** The goal is to simply and directly specify *what* content goes *where*, acting as a precise instruction for an editor.
*   **Do NOT simply summarize** the input text. The goal is to break it down into actionable integration tasks.
*   **Maintain Context:** Ensure each directive clearly links the thought to its intended place or purpose within the PKM system.
*   **Preserve Nuance:** Capture the core meaning and any specific instructions or reflections embedded in the original thought.
*   **One Idea, One Directive (Generally):** If a single thought spawns multiple distinct actions or targets, it might be broken into multiple directives if that improves clarity for the downstream agent.
*   **Use Provided Project Names:** Strictly use the project/context names provided in the input.
*   **CRITICAL Markdown Formatting:**
    *   Ensure the generated markdown is clean and well-formed.
    *   Each main field header (`**Target Project:**`, `**Target Specifics:**`, `**Agent Action:**`, `**Content/Thought Details:**`) must start on a new line.
    *   **BLANK LINES ARE ESSENTIAL for correct rendering:** You MUST include EXACTLY ONE BLANK LINE:
        1.  AFTER the `**Target Project:** ...` line (and its value) AND BEFORE the `**Target Specifics:** ...` line.
        2.  AFTER the `**Target Specifics:** ...` line (and its value) AND BEFORE the `**Agent Action:** ...` line.
        3.  **MOST IMPORTANTLY:** AFTER the `**Agent Action:** ...` line (and its value) AND BEFORE the `**Content/Thought Details:**` header. Failure to include this specific blank line often leads to rendering issues where "Content/Thought Details:" appears on the same line as the Agent Action.
    *   Values for these fields (e.g., project names, specifics, actions) should be enclosed in backticks (e.g., `` `phd_thesis.md` ``).
    *   Bullet points under `Content/Thought Details` should start with `*   ` (asterisk, then three spaces). Their content should also be enclosed in backticks if they represent specific terms, phrases, or direct snippets.

**Required Output Format:**
Produce a list of "Integration Directives," each adhering to the following template. Pay **EXTREME ATTENTION** to the placement of blank lines as specified in the "CRITICAL Markdown Formatting" rules. The blank line before `**Content/Thought Details:**` is particularly vital.