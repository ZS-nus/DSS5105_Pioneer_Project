import os
import ast
from collections import defaultdict

def extract_imports(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            tree = ast.parse(file.read())
        except:
            print(f"Failed to parse: {file_path}")
            return set()
    
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.add(name.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    return imports

def scan_directory(directory):
    all_imports = set()
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                imports = extract_imports(file_path)
                all_imports.update(imports)
    return all_imports

if __name__ == "__main__":
    directory = "."  # Current directory
    imports = scan_directory(directory)
    print("Found imports:")
    for imp in sorted(imports):
        print(f"- {imp}")