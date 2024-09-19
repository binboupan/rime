# Rime

![Main Interface](doc/screenshot.png?raw=true "Main interface")

Rime is a dashboard inspired by [Flame](https://github.com/pawelmalak/flame) and [SUI](https://github.com/jeroenpardon/sui) written in Python with focus on speed while not forgetting functionality.

Pull requests **are** welcome!

## Features

- Service availability check
- Support for multiple categories
- Admin UI for editing services

## Getting Started

After launching the administration interface can be accessed at http://localhost:8000/admin (by default). The username is admin, no password. Set an admin password in the interface.

**Docker:**

docker run -d -p 800:8000 -v ./data:/app/data rime

**Python:**

```
cd src
python3 -m venv venv  
source bin/env/activate  
pip3 install -r dependencies.txt  
fastapi run app.py

```

## Roadmap

- Bookmarks
- Plugin support
- Theming

## External dependencies

Main font used is the [Inter](https://rsms.me/inter/) font.
Using [Simple Icons](https://simpleicons.org/) for the card icons.
