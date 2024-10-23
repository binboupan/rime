![Rime Logo](docs/rime-logo.png?raw=true "Rime Logo" )

# Rime Dashboard

![Main Interface](docs/screenshot.png?raw=true "Main interface ")

Rime is a dashboard inspired by [Flame](https://github.com/pawelmalak/flame) and [SUI](https://github.com/jeroenpardon/sui) written in Python with focus on speed while not forgetting functionality. Rime is easy to extend with plugins.

Pull requests **are** welcome!

## Features

- Service availability check
- Support for multiple categories
- Configuration via YAML
- Lightweight on resources

## Currently available plugins
- Website status checker
- Web radio player

## Getting Started

Edit services.yaml as you see fit!


**Python:**

```
cd src
python3 -m venv venv  
source bin/env/activate  
pip3 install -r dependencies.txt  
cp services.yaml.example services.yaml
uvicorn app:app --port 8095 --reload --reload-include *.yaml

```

## Roadmap
- Bookmarks
- Theming

## External dependencies

Main font used is the [Inter](https://rsms.me/inter/) font.
Using [Simple Icons](https://simpleicons.org/) for the card icons.
