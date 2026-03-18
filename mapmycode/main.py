from dotenv import load_dotenv
import os
from mapmycode.utils import *
import json
from mapmycode.graph_algos import topological_sort,create_dependency_dict, create_graph

load_dotenv(override=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def main(path):
    python_files = walk_directories(path)
    
    print(python_files)
    
    graph, file_contents = create_graph(python_files)
        
    order = topological_sort(graph)

    file_wise_summary = create_dependency_dict(graph, order,file_contents)

    output_file = os.path.join(path, "results.json")

    with open(output_file, "w") as f:
        json.dump(file_wise_summary, f, indent=2)
    
    create_documentation(file_wise_summary,path)
    
    create_mermaid_diagram(graph,file_wise_summary,path)

if __name__ == "__main__":
    path = "../"
    main(path)