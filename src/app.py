from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, MetaData, Column, Date, DateTime, Float, VARCHAR, TIMESTAMP, TEXT, text, event, DDL, orm

from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import INTEGER, JSONB, BOOLEAN, JSONB, VARCHAR, FLOAT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from fastapi_utils.tasks import repeat_every

from urllib3 import Timeout, PoolManager

import os
from passlib.context import CryptContext

from fastapi.security import HTTPBasic, HTTPBasicCredentials
import sys

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBasic()

# Increment on schema changes so we can migrate
DB_VERSION = 1


VERSION = "unknown"

try:
    import gitinfo
    sys.path.append("..")
    VERSION = gitinfo.get_git_info()["commit"][:7]
except Exception as e:
    print(e)
    VERSION = "0.1.1"
    

# Should we refetch configuration, services, etc
DROP_CACHES = False

# Configuration array, kept in memory
config_arr = {}

# Database models
engine = create_engine('sqlite:///data/rime.db', echo = False)

Base = declarative_base()
metadata = Base.metadata

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = credentials.username == "admin"
    with Session(engine) as session:
        session.begin()
        db_config = session.query(Config).first()
        
        # No password set.
        if db_config.admin_password == "":
            return credentials.username

        elif not (correct_username and Hasher.verify_password(credentials.password, db_config.admin_password)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password.",
                headers={"WWW-Authenticate": "Basic"},
            )
        return credentials.username


class Hasher():
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)

class Services_Categories(Base):
    __tablename__ = "services_categories"
    id = Column(Integer, primary_key = True, unique=True, autoincrement=True)
    name = Column(String) 
    hide_title = Column(Integer, server_default="0")


class Bookmarks_Categories(Base):
    __tablename__ = "bookmarks_categories"
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

class Bookmarks(Base):
    __tablename__ = "bookmarks"
    id = Column(Integer, primary_key = True, unique=True, autoincrement=True)
    category_id = Column(Integer, nullable=False)
    name = Column(String) 
    icon = Column(String, nullable=True)
    url = Column(String)


class Config(Base):
   __tablename__ = "config"
   db_version = Column(Integer, primary_key = True, server_default=str(DB_VERSION))
   secret_key = Column(String, primary_key= False, server_default="")
   admin_password = Column(String, primary_key=False, server_default="")
   hide_search_bar = Column(Integer, server_default="0")
   page_title = Column(String, server_default="Rime")
   search_provider_url = Column(String, server_default="https://google.com/search")
   hide_version_string = Column(Integer, server_default="0")
   background_color = Column(String, server_default="")
   text_color = Column(String, server_default="#d6d0ce")
   icon_gradient_start_color = Column(String, server_default="#d6d0ce")
   icon_gradient_end_color = Column(String, server_default="#585857")
   service_card_text_color = Column(String, server_default="#d6d0ce")
   search_box_text_color = Column(String, server_default="#282c34")
   search_box_text_color = Column(String, server_default="#8fba60")
   search_box_focused_text_color = Column(String, server_default="#8fba60")

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
            exception = False

            try:
                timeout = Timeout(connect=2.0, read=7.0)
                http = PoolManager(timeout=timeout)
                state = http.request('GET', config_arr["services"][category][service]["ping_url"])
            except Exception as e:
                exception = True
                config_arr["services"][category][service]["current_color"] = "red" # cannot contact service

            # Work around urllib3 bug with invalid certs returning 200 error code
            if not exception:
                if state.status == 200 or state.status == 302 or state.status == 301: # online
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
            new_config = Config(secret_key=os.urandom(24).hex())
            session.add(new_config)
            session.commit()

            
            load_config()
        else:
            global config_arr
            config_arr = {}
            config_arr["config"] = {
                "hide_search_bar": db_config.hide_search_bar,
                "page_title": db_config.page_title,
                "search_provider_url": db_config.search_provider_url,
                "hide_version_string": db_config.hide_version_string,
                "background_color":  db_config.background_color,
                "text_color": db_config.text_color,
                "icon_gradient_start_color": db_config.icon_gradient_start_color,
                "icon_gradient_end_color": db_config.icon_gradient_end_color,
                "service_card_text_color": db_config.service_card_text_color,
                "search_box_text_color": db_config.search_box_text_color,
                "search_box_focused_text_color": db_config.search_box_focused_text_color
            }
            config_arr["services"] = {}
            config_arr["categories"] = {}
            config_arr["categories_bookmarks"] = {}
            config_arr["bookmarks"] = {}           

            categories = session.query(Services_Categories).all()
            categories_bookmarks = session.query(Bookmarks_Categories).all()


            # bookmarks
            for category in categories_bookmarks:
                config_arr["categories_bookmarks"][str(category.name)] = {
                    "id": category.id,
                }
                config_arr["bookmarks"][category.name] = {}

                bookmarks = session.query(Bookmarks).where(Bookmarks.category_id==category.id).all()
                for bookmark in bookmarks:
                    config_arr["bookmarks"][str(category.name)][str(bookmark.name)] = {
                        "id": bookmark.id,
                        "name": bookmark.name,
                        "url": bookmark.url,
                        "icon": bookmark.icon
                    }
                    
            # categories
            for category in categories:
                config_arr["categories"][str(category.name)] = {
                    "id": category.id,
                    "hide_title": category.hide_title
                }
                config_arr["services"][category.name] = {}
            

                # services
                services = session.query(Services).where(Services.category_id==category.id).all()
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


            print("config_arr", config_arr)
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

# Renders the admin view, after credentials are verified with http basic auth
@app.get("/admin")
async def admin_ui(request: Request, str = Depends(verify_credentials)):
    # Reload config before accessing admin ui
    load_config()
    return templates.TemplateResponse(
        request=request, name="admin.html", context={"config": config_arr}
    )

# Renders the service creation admin page, could be merged with other function in the future
@app.get("/serviceCreate")
async def create_service(request: Request, str = Depends(verify_credentials)):
    # Reload config before accessing admin ui
    load_config()

    return templates.TemplateResponse(
        request=request, name="create_service.html", context={"config": config_arr}
    )

# Renders the category creation admin page, could be merged with other function in the future
@app.get("/categoryCreate")
async def create_category(request: Request, str = Depends(verify_credentials)):
    # Reload config before accessing admin ui
    load_config()

    return templates.TemplateResponse(
        request=request, name="create_category.html", context={}
    )

# Renders the bookmark category creation admin page, could be merged with other function in the future
@app.get("/bookmarkCategoryCreate")
async def create_category(request: Request, str = Depends(verify_credentials)):
    # Reload config before accessing admin ui
    load_config()

    return templates.TemplateResponse(
        request=request, name="create_bookmark_category.html", context={}
    )


# Creates a new service
@app.post("/createServiceCallback")
async def create_service_callback(request: Request, str = Depends(verify_credentials)):
    form_data = await request.form()
    with Session(engine) as session:
    
        session.begin()
        service = Services()

        service.name = form_data.get("service_name")
        service.subtitle = form_data.get("service_subtitle")
        service.icon = form_data.get("service_icon")
        service.url = form_data.get("service_url")
        service.ping_url = form_data.get("service_ping_url")
        service.category_id =  form_data.get("service_category")
        service.enable_ping = 1

        session.add(service)
        session.commit()

        # Reload config and return the user to the administration page
        load_config()
        ping_services()

    return templates.TemplateResponse(
        request=request, name="admin.html", context={"config": config_arr}
    )


# Creates a new category
@app.post("/createCategoryCallback")
async def create_category_callback(request: Request, str = Depends(verify_credentials)):
    form_data = await request.form()
    with Session(engine) as session:
        
        session.begin()
        category = Services_Categories()

        category.name = form_data.get("category_name")
        if "hide_title" in form_data:
            category.hide_title = 1
        else:
            category.hide_title = 0
    
        session.add(category)
        session.commit()

        # Reload config and return the user to the administration page
        load_config()

    return templates.TemplateResponse(
        request=request, name="admin.html", context={"config": config_arr}
    )


# Creates a new category
@app.post("/createBookmarkCategoryCallback")
async def create_bookmark_category_callback(request: Request, str = Depends(verify_credentials)):
    form_data = await request.form()
    with Session(engine) as session:
        
        session.begin()
        category = Bookmarks_Categories()

        category.name = form_data.get("category_name")

    
        session.add(category)
        session.commit()

        # Reload config and return the user to the administration page
        load_config()

    return templates.TemplateResponse(
        request=request, name="admin.html", context={"config": config_arr}
    )




# Delete a category
@app.get("/serviceDelete")
async def service_delete(request: Request, str = Depends(verify_credentials)):
    # Reload config before accessing admin ui
   
    edit_id = request.query_params["id"]
    with Session(engine) as session:
        service = session.query(Services).where(Services.id==edit_id).first()
        session.delete(service)
        session.commit()
        load_config()
        ping_services()
        return templates.TemplateResponse(
            request=request, name="admin.html", context={"config": config_arr}
        )


# Delete a category
@app.get("/categoryDelete")
async def category_delete(request: Request, str = Depends(verify_credentials)):
    # Reload config before accessing admin ui
   
    edit_id = request.query_params["id"]
    with Session(engine) as session:
        category_config = session.query(Services_Categories).where(Services_Categories.id==edit_id).first()
        session.delete(category_config)
        session.commit()
        load_config()
        ping_services()
        return templates.TemplateResponse(
            request=request, name="admin.html", context={"config": config_arr}
        )

# Delete a category
@app.get("/bookmarkDelete")
async def bookmark_delete(request: Request, str = Depends(verify_credentials)):
    # Reload config before accessing admin ui
   
    edit_id = request.query_params["id"]
    with Session(engine) as session:
        category_config = session.query(Bookmarks).where(Bookmarks.id==edit_id).first()
        session.delete(category_config)
        session.commit()
        load_config()
        ping_services()
        return templates.TemplateResponse(
            request=request, name="admin.html", context={"config": config_arr}
        )


# Delete a bookmark category
@app.get("/bookmarkCategoryDelete")
async def bookmark_category_delete(request: Request, str = Depends(verify_credentials)):
    # Reload config before accessing admin ui
   
    edit_id = request.query_params["id"]
    with Session(engine) as session:
        category_config = session.query(Bookmarks_Categories).where(Bookmarks_Categories.id==edit_id).first()
        session.delete(category_config)
        session.commit()
        load_config()
        ping_services()
        return templates.TemplateResponse(
            request=request, name="admin.html", context={"config": config_arr}
        )
    


# Service editor
@app.get("/serviceEditor")
async def category_editor(request: Request, str = Depends(verify_credentials)):
    # Reload config before accessing admin ui
    load_config()
    edit_id = request.query_params["id"]
    with Session(engine) as session:
        service_config = session.query(Services).where(Services.id==edit_id).first()
        category_list = session.query(Services_Categories).all()

        return templates.TemplateResponse(
            request=request, name="edit_service.html", context={"config": service_config, "categories": category_list}
        )


# Bookmark editor
@app.get("/bookmarkEditor")
async def bookmark_editor(request: Request, str = Depends(verify_credentials)):
    # Reload config before accessing admin ui
    load_config()
    edit_id = request.query_params["id"]
    with Session(engine) as session:
        service_config = session.query(Bookmarks).where(Bookmarks.id==edit_id).first()
        category_list = session.query(Bookmarks_Categories).all()

        return templates.TemplateResponse(
            request=request, name="edit_bookmark.html", context={"config": service_config, "categories": category_list}
        )



# Bookmark Category editor
@app.get("/bookmarkCategoryEditor")
async def category_editor(request: Request, str = Depends(verify_credentials)):
    # Reload config before accessing admin ui
    load_config()
    edit_id = request.query_params["id"]
    with Session(engine) as session:
        category_config = session.query(Bookmarks_Categories).where(Bookmarks_Categories.id==edit_id).first()

        return templates.TemplateResponse(
            request=request, name="edit_bookmark_category.html", context={"config": category_config}
        )
    

# Category editor
@app.get("/categoryEditor")
async def category_editor(request: Request, str = Depends(verify_credentials)):
    # Reload config before accessing admin ui
    load_config()
    edit_id = request.query_params["id"]
    with Session(engine) as session:
        category_config = session.query(Services_Categories).where(Services_Categories.id==edit_id).first()

        return templates.TemplateResponse(
            request=request, name="edit_category.html", context={"config": category_config}
        )


# Updates a category
@app.post("/updateServiceCallback")
async def update_service(request: Request, str = Depends(verify_credentials)):
    form_data = await request.form()
    with Session(engine) as session:
        session.begin()
        service = session.query(Services).where(Services.id==form_data.get("service_id")).first()


        service.name = form_data.get("service_name")
        service.subtitle = form_data.get("service_subtitle")
        service.icon = form_data.get("service_icon")
        service.url = form_data.get("service_url")
        service.ping_url = form_data.get("service_ping_url")
        service.category_id =  form_data.get("service_category")
        service.enable_ping = 1

        session.add(service)
        session.commit()

        # Reload config and return the user to the administration page
        load_config()

    return templates.TemplateResponse(
        request=request, name="admin.html", context={"config": config_arr}
    )



# Updates a Bookmark
@app.post("/updateBookmarkCallback")
async def update_bookmark(request: Request, str = Depends(verify_credentials)):
    form_data = await request.form()
    with Session(engine) as session:
        session.begin()
        service = session.query(Bookmarks).where(Bookmarks.id==form_data.get("service_id")).first()
        service.name = form_data.get("service_name")
        service.icon = form_data.get("service_icon")
        service.url = form_data.get("service_url")
        service.category_id =  form_data.get("service_category")


        session.add(service)
        session.commit()

        # Reload config and return the user to the administration page
        load_config()

    return templates.TemplateResponse(
        request=request, name="admin.html", context={"config": config_arr}
    )


# Updates a category
@app.post("/updateBookmarkCategory")
async def update_bookmark_category(request: Request, str = Depends(verify_credentials)):
    form_data = await request.form()
    with Session(engine) as session:
        session.begin()
        category = session.query(Bookmarks_Categories).where(Bookmarks_Categories.id==form_data.get("category_id")).first()


        category.name = form_data.get("category_name")

    
        session.add(category)
        session.commit()

        # Reload config and return the user to the administration page
        load_config()

    return templates.TemplateResponse(
        request=request, name="admin.html", context={"config": config_arr}
    )

# Updates a category
@app.post("/updateCategory")
async def update_category(request: Request, str = Depends(verify_credentials)):
    form_data = await request.form()
    with Session(engine) as session:
        session.begin()
        category = session.query(Services_Categories).where(Services_Categories.id==form_data.get("category_id")).first()


        category.name = form_data.get("category_name")
        if "hide_title" in form_data:
            category.hide_title = 1
        else:
            category.hide_title = 0
    
        session.add(category)
        session.commit()

        # Reload config and return the user to the administration page
        load_config()

    return templates.TemplateResponse(
        request=request, name="admin.html", context={"config": config_arr}
    )


# Updates general settings in admin
@app.post("/updateGeneralSettings")
async def update_general_settings(request: Request, str = Depends(verify_credentials)):
    form_data = await request.form()
    with Session(engine) as session:
        session.begin()
        db_config = session.query(Config).first()

        db_config.page_title = form_data.get("page_title")
        db_config.search_provider_url = form_data.get("search_url")

        if form_data.get("admin_password") != "":
            db_config.admin_password = Hasher.get_password_hash(form_data.get("admin_password"))
    
        session.add(db_config)
        session.commit()

        # Reload config and return the user to the administration page
        load_config()

    return templates.TemplateResponse(
        request=request, name="admin.html", context={"config": config_arr}
    )