def get_file_summary(file_name, file_content, dependencies_dict):

    summary_prompt = f"""
        You are analyzing a Python codebase.

        I will provide:
        * The file name: {file_name}
        * The full content: {file_content}
        * Dependencies: {dependencies_dict}

        Your task:
        1. Analyze the file and summarize every function defined in it.
        2. Explain how this file uses its dependencies to perform its overall task.

        Instructions:
        1. Identify all functions defined in the file.
        2. For each function, produce a concise summary covering:
           - purpose
           - inputs
           - returns
           - key logic
        3. Add a top-level key called "dependencies" that explains how the current file leverages its dependencies in order to execute its responsibilities.
        4. Use dependency summaries to clarify roles, but do not repeat them verbatim.
        5. If no functions exist, return an empty list for "functions".
        6. If there are no meaningful dependencies, return an empty list for "dependencies".

        Output requirements:
        * Output must be VALID JSON ONLY.
        * Do not include explanations outside the JSON.
        * Follow this exact schema:

        {{
          "file_name": "{file_name}",
          "dependencies": [
            {{
              "dependency_name": "<string>",
              "role": "<how this dependency is used by the current file>"
            }}
          ],
          "functions": [
            {{
              "function_name": "<string>",
              "purpose": "<string>",
              "inputs": ["<param1>", "<param2>"],
              "returns": "<description>",
              "key_logic": "<brief explanation>"
            }}
          ]
        }}
        """
    return summary_prompt

def get_mermaid_flowchart_prompt(files_metadata, dependency_graph):
    """
    Generates a prompt for a Mermaid FLOWCHART (flowchart TD).
    The diagram shows:
    - each file as a node
    - dependency relationships as arrows
    - each file's purpose, main functions, and how it uses its dependencies
    """
    
    prompt = f"""
    You are a Software Visualization Expert.

    ### TASK:
    Convert the following Python project metadata and dependency graph into a **Mermaid.js Flowchart** that clearly explains:
    1. what each file does
    2. how files depend on each other
    3. how each file leverages its dependencies to complete its responsibilities

    ### DATA:
    - **File Metadata:** {files_metadata}
    - **Dependency Graph:** {dependency_graph}

    ### DIAGRAM GOAL:
    Produce a clean, readable architecture flowchart for a Python codebase.
    The chart should help a reader quickly understand:
    - the role of each file
    - the major functions it contains
    - how it uses imported/internal dependency files
    - the overall structure of the project

    ### RULES:
    1. **Header**
       - Start the Mermaid code exactly with:
         `flowchart TD`

    2. **Nodes**
       - Represent every file as one node.
       - Each node must include meaningful, compact information.
       - Use this structure inside each node label:
         - filename
         - purpose/objective
         - main functions
         - dependency usage summary

       - Preferred format:
         `NodeID["<b>filename.py</b><br/>Purpose: ...<br/>Functions: ...<br/>Uses deps for: ..."]`

       - Keep text concise and readable.
       - Do not overload nodes with excessive detail.
       - If a file has no functions, write:
         `Functions: None`
       - If a file has no meaningful dependency usage, write:
         `Uses deps for: None`

    3. **Edges / Dependencies**
       - Show dependencies using directional arrows:
         `A --> B`
       - Arrows must represent that file A depends on file B.
       - Dependencies must be shown primarily through connecting lines, not only through node text.
       - If helpful, add short edge labels for important relationships, such as:
         `A -->|imports helpers| B`
         But only when it improves clarity.

    4. **Subgraphs**
       - Group files by directory, package, or module when applicable.
       - Use subgraphs to improve readability for medium or large projects.
       - Keep grouping logical and not overly fragmented.

    5. **Node Content Prioritization**
       - Use the metadata to infer the file's main responsibility.
       - Summarize how the file leverages dependencies in a practical way, such as:
         - orchestrates helper modules
         - calls utility functions for parsing
         - uses config/constants from another module
         - delegates rendering or I/O to another file
         - builds on shared models or services
       - Do not simply restate raw imports.
       - Explain dependency usage in terms of purpose.

    6. **Color Scheme**
       - Use a soft, modern, easy-to-read color palette.
       - Apply styles consistently using Mermaid `style` statements.

       Use these defaults:
       - **Entry-point / orchestrator files**:
         `fill:#FFF4E5,stroke:#FB8C00,stroke-width:2px,color:#1F1F1F`
       - **Regular processing / service files**:
         `fill:#E8F0FE,stroke:#1A73E8,stroke-width:1.5px,color:#1F1F1F`
       - **Leaf utility / helper files (no internal dependencies)**:
         `fill:#E8F5E9,stroke:#43A047,stroke-width:1.5px,color:#1F1F1F`
       - **Config / constants / schema files**:
         `fill:#F3E8FD,stroke:#8E24AA,stroke-width:1.5px,color:#1F1F1F`

       If a file clearly fits one of these categories, style it accordingly.

    7. **Readability**
       - Prefer short function lists like:
         `Functions: load_data(), clean_text(), run()`
       - If there are too many functions, include only the most important ones and summarize the rest:
         `Functions: parse(), validate(), render(), ...`
       - Keep node labels balanced so the chart remains readable.

    8. **Output Constraint**
       - Return **ONLY** the Mermaid code block.
       - Do not include any explanation, markdown prose, or commentary outside the code block.

    ### EXAMPLE OUTPUT:
    ```mermaid
    flowchart TD
      subgraph app
        A["<b>main.py</b><br/>Purpose: Entry point for the documentation pipeline<br/>Functions: main(), run_pipeline()<br/>Uses deps for: orchestrating scanning, analysis, and diagram generation"]
        B["<b>scanner.py</b><br/>Purpose: Discover Python files in the project<br/>Functions: walk_directories()<br/>Uses deps for: using os/path utilities to traverse directories"]
        C["<b>summarizer.py</b><br/>Purpose: Generate file/function summaries<br/>Functions: get_file_summary()<br/>Uses deps for: consuming dependency context to produce richer summaries"]
      end

      A -->|calls scan step| B
      A -->|calls summary step| C

      style A fill:#FFF4E5,stroke:#FB8C00,stroke-width:2px,color:#1F1F1F
      style B fill:#E8F5E9,stroke:#43A047,stroke-width:1.5px,color:#1F1F1F
      style C fill:#E8F0FE,stroke:#1A73E8,stroke-width:1.5px,color:#1F1F1F
    ```

    Generate the flowchart for the provided data now.
    """
    return prompt