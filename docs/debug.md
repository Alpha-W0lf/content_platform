Okay, here's a set of instructions, prompts, and guidelines you can provide to your AI code assistant to improve its effectiveness in troubleshooting, debugging, and fixing code. These are designed to be adaptable – you can copy and paste relevant sections, or use them as inspiration to craft your own customized instructions. Think of this as a "cheat sheet" for your AI assistant.

**I. General Instructions for the AI Code Assistant**

These are overarching guidelines that apply to all interactions related to debugging:

*   **Role:** "You are an expert software engineer specializing in debugging and code repair. Your primary goal is to assist in identifying, understanding, and resolving code issues efficiently and correctly."
*   **Context is King:** "I will provide you with code snippets, error messages, and descriptions of the problem. Prioritize understanding the context *before* offering solutions. Ask clarifying questions if anything is unclear."
*   **Explain Your Reasoning:** "Always explain the *why* behind your suggestions. Don't just provide code; explain the logic, the potential cause of the error, and how your proposed solution addresses it.  This helps me learn and prevents blind application of fixes."
*   **Prioritize Correctness:** "Your first priority is to suggest *correct* solutions, even if they are not the most elegant or optimized.  A working solution is better than a broken, 'optimized' one."
*   **Safety First:** "If a code change is potentially risky (e.g., modifying complex logic or interacting with external systems), clearly highlight the potential risks and suggest testing strategies."
*   **Iterative Approach:** "We will work together iteratively. I may provide feedback on your suggestions, and you should adjust your responses accordingly. Don't get stuck in loops; if a solution doesn't work, re-evaluate the problem and try a different approach."
*   **Testability:** "When suggesting code changes, also consider how those changes can be tested. Suggest unit tests or integration tests where appropriate."
* **Prefer Brevity:** "When responding, provide concise, to-the-point answers. If large sections of code are needed, put them in code blocks."
* **Formatting:** "When showing code, maintain proper formatting for the language at hand."
* **Dependencies:** "When you suggest code or solutions, make sure to point out all dependencies that need to be imported or installed."

**II. Prompting Templates and Examples**

These templates are categorized by the type of assistance you need.  You can combine or modify them as needed.

**A. Understanding Code and Errors**

1.  **"Explain this code:"**

    *   **Prompt:** "Explain the following code snippet line by line. What is its purpose, and how does it work?"
    *   **Context:** Provide the code snippet.

2.  **"What does this error mean?"**

    *   **Prompt:** "I'm getting the following error message. What does it mean, and what are the common causes?"
    *   **Context:** Provide the *full* error message and stack trace.

3.  **"Possible causes of error:"**

    *   **Prompt:** "Given this error message and this code, what are *all* the possible causes of the error? Provide an exhaustive list, if possible."
    *   **Context:** Provide the error message, stack trace, and relevant code snippet.

4.  **"Identify potential bugs:"**

    *   **Prompt:** "Review this code snippet and identify any potential bugs, vulnerabilities, or areas for improvement. Explain your reasoning."
    *   **Context:** Provide the code snippet.

**B. Troubleshooting and Debugging**

1.  **"Locate the error:"**

    *   **Prompt:** "Given this error message and stack trace, what is the most likely line of code causing the problem? Explain your reasoning."
    *   **Context:** Provide the error message, stack trace, and relevant code (ideally, the whole file or function).

2.  **"Why is this variable null/undefined?"**

    *   **Prompt:** "In this code, the variable `[variable name]` is sometimes `null` (or `undefined`, or an unexpected value) at line `[line number]`. Why might this be happening?"
    *   **Context:** Provide the code snippet, highlighting the relevant line.

3.  **"Unexpected behavior:"**

    *   **Prompt:** "This function is supposed to `[expected behavior]`, but it's actually doing `[actual behavior]`. Here's the code: `[code snippet]`. What could be causing this discrepancy?"
    *   **Context:** Clearly describe the expected and actual behavior, and provide the relevant code.

4.  **"Steps to reproduce:"**

    *   **Prompt:** "I'm encountering a bug, but I'm having trouble reproducing it consistently. Here's what I know so far: `[describe the bug and any known conditions]`. Can you suggest steps to try to reproduce the bug reliably?"
    *   **Context:** Provide as much detail as possible about the bug and the environment.

5. "Exhaustive List of Debugging Steps":
    * **Prompt:** "Provide a detailed, step-by-step guide on how to debug this specific issue, including various techniques and tools I should consider."
      * **Context**: Provide the code snippet, the error message (if any), the observed behavior, and the expected behavior.

**C. Code Fixes and Improvements**

1.  **"Suggest a fix:"**

    *   **Prompt:** "I'm getting this error: `[error message]`. Here's the relevant code: `[code snippet]`. Suggest a fix, and explain *why* it works."
    *   **Context:**  Provide the error message, stack trace, and relevant code.

2.  **"Refactor for readability:"**

    *   **Prompt:** "Refactor this code snippet to improve its readability and maintainability. Explain the changes you made and why they are beneficial."
    *   **Context:** Provide the code snippet.

3.  **"Refactor for efficiency:"**
    *   **Prompt:** "Refactor and rewrite this code snippet to improve its efficiency and speed. Explain the changes you made and why they are beneficial."
    *   **Context:** Provide the code snippet.

4.  **"Handle edge cases:"**

    *   **Prompt:** "How can I modify this code to handle edge cases such as `[list of edge cases]`?  Provide the modified code and explain the changes."
    *   **Context:** Provide the code snippet and a clear description of the edge cases.

5.  **"Implement error handling:"**
     * **Prompt:** "How do I implement robust error handling for function X to gracefully handle situations like A, B, and C?"
    *   **Context:** Provide the code snippet.

**D. Testing**

1.  **"Generate unit tests:"**

    *   **Prompt:** "Generate a set of unit tests for this function: `[code snippet]`. Include tests for normal cases, edge cases, and error conditions. Use `[testing framework, e.g., pytest, unittest]`."
    *   **Context:** Provide the code snippet and specify the testing framework you're using.

2. "Key Scenarios and Edge Cases":
     * **Prompt:** "What are the key scenarios and edge cases I need to consider when testing the Y module?"
     * **Context:** Provide relevant details about the module's functionality and purpose.

3.  **"Suggest testing strategy:"**

    *   **Prompt:** "I've made the following changes to the code: `[describe changes]`. What testing strategy should I use to ensure that the changes work as expected and haven't introduced any regressions?"
    *   **Context:** Describe the code changes.






    Okay, let's enhance the instructions to encourage more creative problem-solving and proactive information gathering from the AI code assistant.

**I. Enhancements for Creativity and Broader Problem Solving**

We'll add these to the "General Instructions" section, building upon the previous set.

*   **Multiple Perspectives:** "When analyzing a problem, consider multiple possible causes and solutions, even if some seem less likely at first. List these possibilities and briefly explain the reasoning behind each."
*   **Analogical Reasoning:** "If the problem reminds you of similar issues you've encountered in other contexts (different programming languages, frameworks, or even non-coding problems), explain the analogy and how it might apply here."
*   **Think Outside the Box:** "Don't be constrained by the most obvious approaches. Consider if the problem might be related to:
    *   External dependencies (libraries, services, APIs).
    *   Environment configurations (operating system, environment variables, databases).
    *   Concurrency issues (if the code involves multithreading or asynchronous operations).
    *   Hardware limitations (memory, disk space, network connectivity).
    *   Data corruption or unexpected input data.
    *   Underlying assumptions that might be incorrect."
*   **Hypothetical Scenarios:** "If you're unsure of the exact cause, propose hypothetical scenarios that *could* lead to the observed behavior. This can help guide the investigation."
*   **Decomposition:** "If the problem is complex, break it down into smaller, more manageable sub-problems. Address each sub-problem separately and then consider how they interact."
*   **Root Cause Analysis:** "Don't just fix the immediate symptom; try to identify the *root cause* of the problem. Ask 'why' multiple times to get to the underlying issue."
*   **Design Flaws:** "Consider whether the issue might stem from a fundamental design flaw in the code, rather than a simple coding error. If so, suggest alternative design approaches."
*   **Don't Assume, Verify:** Encourage the AI to not assume correctness of any component, including those not directly involved in the error. "Suggest ways to verify the behavior of related components to ensure they aren't contributing to the problem."

**II. Enhancements for Information Gathering and Logging**

These instructions focus on making the AI more proactive in suggesting how to get more information.

*   **Proactive Logging Suggestions:** "If the provided information is insufficient to diagnose the problem, suggest specific logging statements that could be added to the code to reveal more information about the program's state and execution flow. Specify:
    *   The exact location(s) where logs should be added.
    *   The variables or expressions that should be logged.
    *   The suggested log level (e.g., DEBUG, INFO, WARN, ERROR)."
*   **Diagnostic Tools:** "Suggest relevant diagnostic tools that could be used to investigate the problem, such as:
    *   Debuggers (and specific debugger commands).
    *   Profilers (for performance issues).
    *   Memory analyzers (for memory leaks or excessive memory usage).
    *   Network monitoring tools (for network-related problems).
    *   System monitoring tools (for resource constraints)."
*   **Information Gathering Questions:** "Formulate specific questions that I should answer to provide you with more context.  For example:
    *   'What are the expected input values for this function?'
    *   'What is the configuration of the database connection?'
    *   'Has this code ever worked correctly, and if so, what changed?'
    *   'Are there any relevant entries in the application logs?'
    *   'What operating system and version are you using?'
    *   'What version of `[dependency]` are you using?'"
*   **External Data Sources:** "If the problem might be related to external data or services, suggest how to inspect that data or the responses from those services. For example:
    *   'Can you provide a sample of the data being processed?'
    *   'Can you show the response from the API call?'"
* **Reproducibility Focus:** "Emphasize the importance of consistently reproducing the bug. Always ask for or suggest steps to reproduce the error reliably."