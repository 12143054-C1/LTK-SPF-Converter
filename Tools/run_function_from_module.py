import importlib.util
import sys

def run_function_from_module(module_path, function_name, *args, **kwargs):
    """
    Imports a module from a given path and runs a specified function from that module.

    Parameters:
    - module_path (str): The file path of the module to import.
    - function_name (str): The name of the function to run from the module.
    - args: Positional arguments to pass to the function.
    - kwargs: Keyword arguments to pass to the function.

    Returns:
    - The result of the function call.
    """

    # Load the module spec from the given file path
    spec = importlib.util.spec_from_file_location("module.name", module_path)
    if spec is None:
        raise ImportError(f"Could not load the module from {module_path}")

    # Create a new module based on the spec
    module = importlib.util.module_from_spec(spec)

    # Add the module to sys.modules so it can be imported
    sys.modules[spec.name] = module

    # Execute the module
    spec.loader.exec_module(module)

    # Get the function from the module
    func = getattr(module, function_name, None)
    if func is None:
        raise AttributeError(f"The function '{function_name}' does not exist in the module '{module_path}'")

    # Call the function with the provided arguments and keyword arguments
    return func(*args, **kwargs)

# Example usage:
# Assuming there is a file 'example_module.py' with a function 'example_function'
# module_path = 'path/to/your/example_module.py'
# result = run_function_from_module(module_path, 'example_function', arg1, arg2, kwarg1=value1)
# print(result)
