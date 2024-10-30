# Adguard Home Plugin


from fastapi import FastAPI, APIRouter, Body, status
import requests
from fastapi.responses import JSONResponse
from dependencies import Plugin
from requests.auth import HTTPBasicAuth

from yamlutil.database import get_config
import base64

#from database.database import get_plugin_config

class AdguardPlugin(Plugin):
    def register(self, app: FastAPI):
        print("Load plugin: Adguard stats")
        router = APIRouter()

        # Add the routes your plugin uses here
        @router.get("/adguardhome/status")
        def get_status(id: str, category: str):
            config = get_config()

            authentication = base64.b64decode(config[category][id]["api-key"]).decode("utf-8").split(":")

            #HTTPBasicAuth('user', 'pass')
            try:
                response = requests.get(config[category][id]["url"] + "/control/stats", auth=HTTPBasicAuth(authentication[0], authentication[1]))
                
                if response.status_code == 200 or response.status_code == 302 or response.status_code == 304:
                    return JSONResponse(content=response.json())
                else:
                    return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"online": False})
            except requests.exceptions.RequestException:
                return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"online": False})
        
        # Add routes to the app
        app.include_router(router)
