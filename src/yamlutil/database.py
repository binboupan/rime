# Database functions and models

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from dependencies import Plugin
import yaml

with open('config/services.yaml', 'r') as f:
    data = yaml.load(f, Loader=yaml.SafeLoader)

with open('config/config.yaml', 'r') as f:
    config_data = yaml.load(f, Loader=yaml.SafeLoader)

with open('config/bookmarks.yaml', 'r') as f:
    bookmark_data = yaml.load(f, Loader=yaml.SafeLoader)


def get_app_config():
    return config_data

def get_config():
    return data

def get_bookmark_config():
    return bookmark_data


def get_enabled_plugins():
    enabled_plugins = []

    for category in data:
        for item in data[category]:
            if data[category][item]["plugin"] not in enabled_plugins:
                enabled_plugins.append(data[category][item]["plugin"])
    return enabled_plugins
        
