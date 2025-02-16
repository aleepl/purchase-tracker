import importlib
import os

# Dynamically import all Python files in the models directory
def import_models():
    models_dir = os.path.dirname(__file__)
    for filename in os.listdir(models_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"db.models.{filename[:-3]}"
            importlib.import_module(module_name)

# Call this function in your script
import_models()
