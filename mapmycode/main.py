from dotenv import load_dotenv
import os
from mapmycode.utils import *
import json
from mapmycode.graph_algos import topological_sort,create_dependency_dict, create_graph

load_dotenv(override=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def main(path,output_dir):
    python_files = walk_directories(path)
    
    print(f"Python files identified :  {python_files}")
    print('-'*60)
    
    print("Creating graph...")
    print('-'*60)
    graph, file_contents = create_graph(python_files)
    
    print("Identifying build order...")
    print('-'*60)
    order = topological_sort(graph)

    print("Creating dependency network...")
    print('-'*60)
    file_wise_summary = create_dependency_dict(graph, order,file_contents)

    output_file = os.path.join(output_dir, "results.json")

    with open(output_file, "w") as f:
        json.dump(file_wise_summary, f, indent=2)
    
    print('Creating documentation...')
    print('-'*60)
    create_documentation(file_wise_summary,output_dir)
    
    print('Creating architecture diagram...')
    print('-'*60)
    create_mermaid_diagram(graph,file_wise_summary,output_dir)

if __name__ == "__main__":
    path = "../"
    main(path,path)