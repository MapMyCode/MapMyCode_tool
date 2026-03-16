import os
import base64
import io, requests
from IPython.display import Image, display
from PIL import Image as im
import matplotlib.pyplot as plt
from groq_call import run_groq_api
from prompts import get_file_summary, get_mermaid_flowchart_prompt

exclude_dirs = ['.venv','__pycache__','venv','mapmycode']

def walk_directories(path):
    python_files = []

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith(".py") and file != "topological_sort.py":
                python_files.append(os.path.join(root, file))

    return python_files

def create_graph(python_files):
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
    
    return graph, file_contents

def create_dependency_dict(graph,order,file_contents):
    results = {}
    for file in order:
        file_content = file_contents[file]
        
        dependencies = graph[file]
        dependencies_dict = {}
        
        for dependency in dependencies:
            dependencies_dict[dependency] = results[dependency]
        
        summary_prompt = get_file_summary(file,file_content, dependencies_dict)
        result = run_groq_api(summary_prompt)
        results[file] = result
    
    return results

def mm(graph, base_dir):
    graphbytes = graph.encode("utf8")
    base64_bytes = base64.urlsafe_b64encode(graphbytes)
    base64_string = base64_bytes.decode("ascii")
    img = im.open(io.BytesIO(requests.get('https://mermaid.ink/img/' + base64_string).content))
    plt.imshow(img)
    plt.axis('off') # allow to hide axis
    image_path = os.path.join(base_dir, "image.png")
    plt.savefig(image_path, dpi=1200)
    
    
def create_mermaid_diagram(graph,file_wise_summary,path):
    mermaid_prompt = get_mermaid_flowchart_prompt(file_wise_summary,graph)
    response = run_groq_api(mermaid_prompt)
    response = response.replace("```mermaid", "").replace("```", "").strip()
    mm(response,path)

