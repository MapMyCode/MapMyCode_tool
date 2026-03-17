from groq_call import run_groq_api
from prompts import get_file_summary

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