from fastapi import FastAPI, Request

from dependencies import load_plugins
from database.database import create_db_and_tables, get_categories, get_plugin_configs, get_enabled_plugins
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index(request: Request):
    
    templates.env.globals["get_configs"] = get_plugin_configs
    return templates.TemplateResponse(
        request=request, name="index.html", context={"categories": get_categories(), "enabled_plugins": get_enabled_plugins()}
    )


load_plugins(app)
create_db_and_tables()
