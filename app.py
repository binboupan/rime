from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, MetaData, Column, Date, DateTime, Float, VARCHAR, TIMESTAMP, TEXT, text, event, DDL, orm

from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import INTEGER, JSONB, BOOLEAN, JSONB, VARCHAR, FLOAT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func



# Increment on schema changes so we can migrate
DB_VERSION = 1
VERSION = "0.1.0"

# Should we refetch configuration, services, etc
DROP_CACHES = False

# Configuration array, kept in memory
config_arr = {}
config_arr["config"] = {}
config_arr["apps_categories"] = {}
config_arr["apps"] = {}
config_arr["bookmarks"] = {}
config_arr["bookmark_categories"] = {}

# Database models
engine = create_engine('sqlite:///data/rime.db', echo = False)

Base = declarative_base()
metadata = Base.metadata


class Services(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key = True, unique=True, autoincrement=True)
    name = Column(String) 
    subtitle = Column(String)
    url = Column(String)
    enable_ping = Column(Integer, primary_key = True, server_default='1')

class Config(Base):
   __tablename__ = "config"
   db_version = Column(Integer, primary_key = True, server_default=str(DB_VERSION))
   theme = Column(String, primary_key = False, server_default='default_dark')
   language = Column(String, primary_key = False, server_default='en')


metadata.create_all(engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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

            print("-> Configuration loaded.")

load_config()


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={"theme": config_arr["config"].get("theme")}
    )
