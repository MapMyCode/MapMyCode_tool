import os
import base64
import io, requests
from IPython.display import Image, display
from PIL import Image as im
import matplotlib.pyplot as plt
from mapmycode.groq_call import run_groq_api
from mapmycode.prompts import get_mermaid_flowchart_prompt, get_documentation_prompt

exclude_dirs = ['.venv','__pycache__','venv','mapmycode','.test-env','dist']

def walk_directories(path):
    python_files = []

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith(".py") and file != "topological_sort.py":
                python_files.append(os.path.join(root, file))

    return python_files

def create_documentation(files_metadata,path):
    prompt = get_documentation_prompt(files_metadata)
    response = run_groq_api(prompt)
    
    path = os.path.join(path,"documentation.md")
    with open(path,'w') as f:
        f.write(response)
    

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

