###  YOU GOTTA PASTE THIS TO THE STAB MODE PYTHON INSTANCE ###

import os
import importlib.util

def run_converted_modules(folder_path):
    # Ensure the provided path is a directory
    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"The provided path '{folder_path}' is not a directory.")
    
    # Iterate over all files in the directory
    for file_name in os.listdir(folder_path):
        # Check if the file is a Python module
        if file_name.endswith('.py'):
            module_name = file_name[:-3]  # Remove the .py extension
            module_path = os.path.join(folder_path, file_name)
            
            # Dynamically load the module
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check if the module has the 'runConverted' function and run it
            if hasattr(module, 'runConverted'):
                print(f"Running 'runConverted' from module '{module_name}'")
                module.runConverted()
            else:
                print(f"Module '{module_name}' does not have a 'runConverted' function")

# Example usage:
run_converted_modules('/path/to/your/folder')
