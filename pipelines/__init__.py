import importlib
import pkgutil

registry = {}


def creatable(cls):
    if cls.handles_type() in registry:
        raise KeyError("Duplicate string representations found for string: " + cls.handles_type())

    registry[cls.handles_type()] = cls

    return cls


def import_submodules(package, recursive=False):
    """ Import all submodules of a module, recursively, including subpackages
    """
    if isinstance(package, str):
        package = importlib.import_module(package)

    results = {}

    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        results[full_name] = importlib.import_module(full_name)

        if recursive and is_pkg:
            results.update(import_submodules(full_name))

    return results


import_submodules(__name__)
