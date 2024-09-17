from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, MetaData, Column, Date, DateTime, Float, VARCHAR, TIMESTAMP, TEXT, text, event, DDL, orm

from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import INTEGER, JSONB, BOOLEAN, JSONB, VARCHAR, FLOAT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from fastapi_utils.tasks import repeat_every

import requests


# Increment on schema changes so we can migrate
DB_VERSION = 1
VERSION = "0.1.0"

# Should we refetch configuration, services, etc
DROP_CACHES = False

# Configuration array, kept in memory
config_arr = {}

# Database models
engine = create_engine('sqlite:///data/rime.db', echo = False)

Base = declarative_base()
metadata = Base.metadata

class Services_Categories(Base):
    __tablename__ = "services_categories"
    id = Column(Integer, primary_key = True, unique=True, autoincrement=True)
    name = Column(String) 

class Services(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key = True, unique=True, autoincrement=True)
    category_id = Column(Integer, nullable=False)
    name = Column(String) 
    subtitle = Column(String, nullable=True)
    icon = Column(String, nullable=True)
    url = Column(String)
    ping_url = Column(String, nullable=True)
    enable_ping = Column(Integer, server_default='1')

class Config(Base):
   __tablename__ = "config"
   db_version = Column(Integer, primary_key = True, server_default=str(DB_VERSION))
   theme = Column(String, primary_key = False, server_default='default_dark')
   language = Column(String, primary_key = False, server_default='en')


metadata.create_all(engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")



def ping_services():
    print("-> Pinging services")
    # check service statuses
    for category in config_arr["services"]:
        for service in config_arr["services"][category]:
            print("Pinging ", service)
            state = requests.get(config_arr["services"][category][service]["ping_url"])
            print(state.status_code)

            if state.status_code == 200 or state.status_code == 302 or state.status_code == 301: # online
                config_arr["services"][category][service]["current_color"] = "green"
            else:
                config_arr["services"][category][service]["current_color"] = "red"

def load_config():
    global DROP_CACHES
    DROP_CACHES = False 
    
    print("Reloading configuration")
    with Session(engine) as session:
        session.begin()
        db_config = session.query(Config).first()
        if db_config is None:
            print("-> No configuration exists, creating default configuration")
            new_config = Config(theme="default_dark", language="en")
            session.add(new_config)
            session.commit()

            
            load_config()
        else:
            global config_arr
            config_arr = {}
            config_arr["config"] = {}
            config_arr["services"] = {}
            config_arr["bookmarks"] = {}           
            config_arr["config"]["language"] = db_config.language
            config_arr["config"]["theme"] = db_config.theme

            categories = session.query(Services_Categories).all()
            for category in categories:
                config_arr["services"][category.name] = {}
            
            services = session.query(Services).all()
            for service in services:
                config_arr["services"][str(category.name)][str(service.name)] = {
                    "id": service.id,
                    "name": service.name,
                    "subtitle": service.subtitle,
                    "url": service.url,
                    "ping_url": service.ping_url,
                    "enable_ping": service.enable_ping,
                    "icon": service.icon,
                    "current_color": "red"
                }
               


            print("-> Configuration loaded.")

load_config()


@app.on_event("startup")
@repeat_every(seconds=60)  
def service_ping_task() -> None:
    ping_services()
        

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={"config": config_arr, "version": VERSION}
    )
