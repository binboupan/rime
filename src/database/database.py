# Database functions and models

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select, JSON
from dependencies import Plugin

sqlite_file_name = "sqlite:///data/database.db"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_file_name, connect_args=connect_args)

# Gets current session instance
def get_session():
    with Session(engine) as session:
        yield session


# Used for rotating the same sqlalchemy instance
SessionDep = Annotated[Session, Depends(get_session)]

# Database models
class Plugins(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    plugin_name: str = Field(index=False)
    category: int | None = Field(default=None, index=True)
    plugin_config: dict = Field(sa_type=JSON, nullable=False)

    class Config:
        arbitrary_types_allowed = True

class Categories(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=False)
    is_bookmark_category: int | None = Field(default=0, primary_key=True)


# Creates the database based on the models
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Get plugin config by it's id
def get_plugin_config(id):
    with Session(engine) as session:
        statement = select(Plugins).where(Plugins.id == id)
        results = session.exec(statement)
        plugin = results.first()
        return plugin.plugin_config

def get_categories():
    with Session(engine) as session:
        statement = select(Categories)
        results = session.exec(statement)
        categories = results.all()
        return categories
    
def get_enabled_plugins():
    with Session(engine) as session:
        statement = select(Plugins).distinct()
        results = session.exec(statement)
        enabled_plugins = results.all()
        return enabled_plugins
        
 # Get all configured plugins, for rendering templates
def get_plugin_configs(category_id):
    with Session(engine) as session:
        statement = select(Plugins).where(Plugins.category == category_id)
        results = session.exec(statement)
        plugins = results.all()
        return plugins
    
       