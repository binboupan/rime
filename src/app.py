from fastapi import FastAPI, Request

from dependencies import load_plugins
from yamlutil.database import get_config, get_enabled_plugins, get_app_config, get_bookmark_config
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index(request: Request):

    return templates.TemplateResponse(
        request=request, name="index.html", context={"config": get_config(), "enabled_plugins": get_enabled_plugins(), "bookmarks": get_bookmark_config(), "app_config": get_app_config()}
    )


load_plugins(app)

