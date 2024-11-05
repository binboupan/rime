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
- Web radio player (Supports Shoutcast and Icecast)
- Jellyfin Stats
- qBitTorrent Stats
- PiHole Stats
- Adguard Home Stats
- Bookmarks

## Getting Started

An example service configuration file is provided at src/config/services.yaml


**Python:**

```
cd src
python3 -m venv venv  
source bin/env/activate  
pip3 install -r dependencies.txt  
cp config/bookmarks.yaml.example config/bookmarks.yaml
cp config/services.yaml.example config/services.yaml
cp config/config.yaml.example config/config.yaml
uvicorn app:app --port 8095 --reload --reload-include *.yaml

```

**Docker Compose:**
Add configuration files to src/config and run:

```
docker compose up

```

## Roadmap
- Theming  
- Proper documentation

## External dependencies

Main font used is the [Inter](https://rsms.me/inter/) font.
Using [Simple Icons](https://simpleicons.org/) and [Material Design Icons](https://pictogrammers.com/library/mdi/) for the card icons.
