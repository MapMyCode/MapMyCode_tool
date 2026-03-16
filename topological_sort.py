import os
from MapMyCode_tool.groq_call import run_groq_api
import base64
import io, requests
from IPython.display import Image, display
from PIL import Image as im
import matplotlib.pyplot as plt
import re
import json

from dotenv import load_dotenv
load_dotenv(override=True)


exclude_dirs = ['.venv','__pycache__','venv']

def walk_directories():
    all_files_folders = os.listdir('.')
    
    python_files = []
    dirs = []
    
    for file in all_files_folders:
        if os.path.isdir(file) and file not in exclude_dirs:
            dirs.append(file)
        
        if file[-3:] == '.py' and file!='topological_sort.py':
            python_files.append(file)
    
    while len(dirs)!=0:
        
        dir = dirs.pop(0)
        
        dir_files = os.listdir(dir)
        
        for file in dir_files:
            path = dir + "/" + file
            if os.path.isdir(path) and path not in exclude_dirs:
                dirs.append(path)
            
            if file[-3:] == '.py' and file!='topological_sort.py':
                python_files.append(file)
    
    return python_files


def topological_sort(graph):
    visited = set()
    stack = []

    def dfs(node):
        if node in visited:
            return
        
        visited.add(node)

        for neighbor in graph[node]:
            dfs(neighbor)

        stack.append(node)

    for node in graph:
        dfs(node)

    return stack

def get_file_summary(file_name, file_content, dependencies_dict):

    summary_prompt = f"""
        You are analyzing a Python codebase.

        I will provide:
        * The file name: {file_name}
        * The full content: {file_content}
        * Dependencies: {dependencies_dict}

        Your task: Analyze the file and summarize every function defined in it.

        Instructions:
        1. Identify all functions defined in the file.
        2. For each, produce a concise summary (purpose, inputs, returns, key logic).
        3. Use dependency summaries to clarify roles, but do not repeat them verbatim.
        4. If no functions exist, return an empty list for "functions".

        Output requirements:
        * Output must be VALID JSON ONLY.
        * Do not include explanations outside the JSON.
        * Follow this exact schema:

        {{
        "file_name": "{file_name}",
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
    file_summary = run_groq_api(summary_prompt, model="openai/gpt-oss-120b")
    return file_summary

def get_mermaid_flowchart_prompt(files_metadata, dependency_graph):
    """
    Generates a prompt for a Mermaid FLOWCHART (flowchart TD).
    Ensures the LLM uses the modern 'flowchart' syntax for better rendering.
    """
    
    prompt = f"""
    You are a Software Visualization Expert. 

    ### TASK:
    Convert the following Python project metadata and dependency graph into a **Mermaid.js Flowchart**.

    ### DATA:
    - **File Metadata (Functions & Objectives):** {files_metadata}
    
    - **Dependency Graph (Imports):** {dependency_graph}

    ### RULES:
    1. **Header**: Start the code block exactly with `flowchart TD`.
    2. **Nodes**: Represent each file as a node with a descriptive label. 
       - Format: `NodeID["**filename.py**<br/>Objective: ...<br/>Funcs: ..."]`
    3. **Edges**: Use `-->` to show dependencies (e.g., `main.py --> utils.py`).
    4. **Subgraphs**: Group files by their directory/module if applicable.
    5. **Styling**: 
       - For leaf-node files (those with NO dependencies), use: `style NodeID fill:#e1f5fe,stroke:#01579b`
       - For entry-point files, use: `style NodeID fill:#fff3e0,stroke:#e65100`
    6. **Output**: Return **ONLY** the mermaid code block. Do not write any markdown prose before or after the code block.

    ### EXAMPLE OUTPUT:
    ```mermaid
    flowchart TD
      subgraph API
        A["**routes.py**<br/>Objective: Handle requests<br/>Funcs: get_user()"]
      end
      A --> B["**db.py**<br/>Objective: Database connection"]
      
      style B fill:#e1f5fe,stroke:#01579b
    ```

    Generate the flowchart for the provided data now:
    """
    
    response = run_groq_api(prompt)
    return response

def mm(graph):
    graphbytes = graph.encode("utf8")
    base64_bytes = base64.urlsafe_b64encode(graphbytes)
    base64_string = base64_bytes.decode("ascii")
    img = im.open(io.BytesIO(requests.get('https://mermaid.ink/img/' + base64_string).content))
    plt.imshow(img)
    plt.axis('off') # allow to hide axis
    plt.savefig('image.png', dpi=1200)

def main():
    
    # all_files = os.listdir('.')
    
    # python_files = []
    # for file in all_files:
    #     if file[-3:] == '.py' and file!='topological_sort.py':
    #         python_files.append(file)
    
    python_files = walk_directories()
    print(python_files)
    
    graph = {}
    file_contents = {}
    for i in range(len(python_files)):
        with open(python_files[i],'r') as f:
            current_content = f.read()
            
        file_contents[python_files[i]] = current_content
        graph[python_files[i]] = []
        
        for j in range(len(python_files)):
            
            if i == j:
                continue
            
            search_term = "from " + python_files[j][:-3]
            if search_term in current_content:
                graph[python_files[i]] += [python_files[j]]
        
    
    order = topological_sort(graph)

    results = {}
    for file in order:
        file_content = file_contents[file]
        
        dependencies = graph[file]
        dependencies_dict = {}
        
        for dependency in dependencies:
            dependencies_dict[dependency] = results[dependency]
        
        result = get_file_summary(file, file_content, dependencies_dict)
        results[file] = result


    json.dump(results, open('results.json','w'))
    
    response = get_mermaid_flowchart_prompt(results, graph)
    response = response.replace("```mermaid", "").replace("```", "").strip()
    mm(response)


    


if __name__ == "__main__":
    main()