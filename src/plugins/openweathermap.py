# Simple endpoint, which checks if a website is live or not


from fastapi import FastAPI, APIRouter, Body, status, Request
import requests
from fastapi.responses import JSONResponse
from dependencies import Plugin

from yamlutil.database import get_config
from datetime import datetime, timedelta
#from database.database import get_plugin_config
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

templates = Jinja2Templates(directory="templates")

import json





class WebsitePlugin(Plugin):
    last_updated = datetime.now()
    weather_req = {}
    initialupdate = False

    def update_weather(self, lat, lon, api_key):
        if self.last_updated+timedelta(hours=1) < datetime.now() or not self.initialupdate:
            print("Updating weather data...")
            req = requests.get("https://api.openweathermap.org/data/2.5/weather?lat=" + str(lat) + "&lon=" + str(lon) + "&appid=" + str(api_key) + "&units=metric")
            self.weather_req = req.json()
            self.last_updated = datetime.now()
            self.initialupdate = True

        return self.weather_req

    def register(self, app: FastAPI):
        print("Load plugin: Website health checker")
        router = APIRouter()


        # Add the routes your plugin uses here
        @router.get("/openweathermap/status")
        def get_status(id: str, category: str):
            """
            if last_updated <= datetime.now() + timedelta(hours=1):
                print("No need to update")
            else:
                print("Updating", last_updated)
            """
            config = get_config()
            self.update_weather(config[category][id]["lat"], config[category][id]["lon"], config[category][id]["api-key"])
            

            print(id, category)


            return JSONResponse(self.weather_req)

        @router.get("/openweathermap/svg")
        def get_status(id: str, category: str, request: Request):
            """
            if last_updated <= datetime.now() + timedelta(hours=1):
                print("No need to update")
            else:
                print("Updating", last_updated)
            """
            

            return templates.TemplateResponse(
                request=Request, name="icons/material-icons/" + weather_req["weather"][0]["main"].lower() + ".svg"
            )


            return JSONResponse(self.update_weather())

        
        # Add routes to the app
        app.include_router(router)
