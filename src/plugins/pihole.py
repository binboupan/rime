# Simple endpoint, which checks if a website is live or not
# Main logic is Javascript in static/js/website.js


from fastapi import FastAPI, APIRouter, Body, status
import requests
from fastapi.responses import JSONResponse
from dependencies import Plugin

from yamlutil.database import get_config

#from database.database import get_plugin_config

class WebsitePlugin(Plugin):
    def register(self, app: FastAPI):
        print("Load plugin: Pihole stats")
        router = APIRouter()

        # Add the routes your plugin uses here
        @router.get("/pihole/status")
        def get_status(id: str, category: str):
            config = get_config()

            print(id, category)

            try:
                response = requests.get(config[category][id]["url"] + "/admin/api.php?summaryRaw&auth=" + config[category][id]["api-key"])
                
                if response.status_code == 200 or response.status_code == 302 or response.status_code == 304:
                    return JSONResponse(content=response.json())
                else:
                    return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"online": False})
            except requests.exceptions.RequestException:
                return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"online": False})
        
        # Add routes to the app
        app.include_router(router)
