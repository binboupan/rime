# Simple endpoint, which checks if a website is live or not



from fastapi import FastAPI, APIRouter, Body, status
import requests
from fastapi.responses import JSONResponse
from dependencies import Plugin
import json
from yamlutil.database import get_config

#from database.database import get_plugin_config

class AzuracastPlugin(Plugin):
    def register(self, app: FastAPI):
        print("Load plugin: Azuracast nowplaying")
        router = APIRouter()

        # Add the routes your plugin uses here
        @router.get("/azuracast/status")
        def get_status(id: str, category: str):
            config = get_config()

            print(id, category)

            try:
                response = requests.get(config[category][id]["now_playing_url"])

                np_info = json.loads(response.text)

                if response.status_code == 200 or response.status_code == 302 or response.status_code == 304:
                    return JSONResponse(content={"now_playing": np_info["now_playing"]["song"]["text"]})
                else:
                    return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"now_playing": False})
            except requests.exceptions.RequestException:
                return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"now_playing": False})
        
        # Add routes to the app
        app.include_router(router)
