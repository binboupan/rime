# Dependencies used elsewhere in the code

from fastapi import FastAPI
import importlib
import os

# Plugin model skeleton
class Plugin:
    def register(self, app: FastAPI):
        raise NotImplementedError

# Where is the plugin folder
PLUGIN_DIR = 'plugins'

# Loads plugins and creates routes for them
def load_plugins(app: FastAPI):
    for filename in os.listdir(PLUGIN_DIR):
        if filename.endswith(".py"):
            module_name = filename[:-3]
            module = importlib.import_module(f"{PLUGIN_DIR}.{module_name}")
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, Plugin) and attr is not Plugin:
                    plugin: Plugin = attr()
                    plugin.register(app)


