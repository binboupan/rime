# Speedtest Tracker Plugin


from fastapi import FastAPI, APIRouter, Body, status
import requests
from fastapi.responses import JSONResponse
from dependencies import Plugin
from requests.auth import HTTPBasicAuth

from yamlutil.database import get_config
import base64

#from database.database import get_plugin_config

class SpeedtestTrackerPlugin(Plugin):
    def register(self, app: FastAPI):
        print("Load plugin: Speedtest Tracker stats")
        router = APIRouter()

        # Add the routes your plugin uses here
        @router.get("/speedtest-tracker/status")
        def get_status(id: str, category: str):
            config = get_config()

            authentication = config[category][id]["api-key"]

            #HTTPBasicAuth('user', 'pass')
            try:
                print(config[category][id]["url"] + "/api/v1/results/latest")
                response = requests.get(config[category][id]["url"] + "/api/v1/results/latest", headers={'Accept': 'application/json', 'Authorization': 'Bearer '+config[category][id]["api-key"]} )
                print(response.text)
                print(response.status_code)
                if response.status_code == 200 or response.status_code == 302 or response.status_code == 304:
                    return JSONResponse(content=response.json())
                else:
                    return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"online": False})
            except requests.exceptions.RequestException as e:
                import traceback
                traceback.print_exc()
                print(e)
                return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"online": False})
        
        # Add routes to the app
        app.include_router(router)
