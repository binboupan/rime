# Minecraft (Java) server query plugin

from fastapi import FastAPI, APIRouter, Body, status
import requests
from fastapi.responses import JSONResponse
from dependencies import Plugin
from requests.auth import HTTPBasicAuth
try:
    from mcstatus import JavaServer
except:
    print("Unable to load Minecraft plugin")
    pass

from yamlutil.database import get_config
import base64

#from database.database import get_plugin_config

class SpeedtestTrackerPlugin(Plugin):
    def register(self, app: FastAPI):
        print("Load plugin: Minecraft server stats")
        router = APIRouter()

        # Add the routes your plugin uses here
        @router.get("/minecraft/status")
        def get_status(id: str, category: str):
            config = get_config()

            server = config[category][id]["server"]
            port = config[category][id]["port"]

            try:
                server = JavaServer.lookup(server, port)
                status = server.status()
                return JSONResponse(content={"players":status.players.online, "ping": round(status.latency,1) })

            except e:
                return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"online": False})
        
        # Add routes to the app
        app.include_router(router)
