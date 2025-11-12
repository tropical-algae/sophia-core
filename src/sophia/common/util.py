import importlib
import pkgutil
from types import ModuleType

import yaml


def load_yaml(yaml_path: str) -> dict:
    try:
        with open(yaml_path) as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as err:
        raise Exception(
            f"Error occurred when read YAML from path '{yaml_path}'. Error: {err}"
        ) from err


def import_all_modules_from_package(package: ModuleType) -> None:
    """Import all models from pkg

    Args:
        package (str): pkg name
    """
    for _, modname, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        importlib.import_module(modname)
