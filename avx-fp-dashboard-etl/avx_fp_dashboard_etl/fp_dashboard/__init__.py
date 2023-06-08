from pkgutil import iter_modules
from pathlib import Path
from importlib import import_module

if "___loaded___" not in globals():
    package_dir = Path(__file__).resolve().parent
    for (_, module_name, _) in iter_modules([str(package_dir)]):
        try:
            module = import_module(f"{__name__}.{module_name}")
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                if attribute_name.startswith("__"):
                    continue
                globals()[attribute_name] = attribute
        except AttributeError:
            pass
        except ImportError:
            pass
    globals()["___loaded___"] = True

__all__ = ["models"]
