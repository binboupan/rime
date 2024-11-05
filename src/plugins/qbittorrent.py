# Gets qBitTorrent Stats

from fastapi import FastAPI, APIRouter, Body, status
import requests
from fastapi.responses import JSONResponse
from dependencies import Plugin
import json
import base64

from yamlutil.database import get_config

#from database.database import get_plugin_config

class WebsitePlugin(Plugin):
    def register(self, app: FastAPI):
        print("Load plugin: qBitTorrent stats")
        router = APIRouter()

        # Add the routes your plugin uses here
        @router.get("/qbittorrent/status")
        def get_status(id: str, category: str):
            try:
                config = get_config()

                config[category][id]["api-key"]

                authentication = base64.b64decode(config[category][id]["api-key"]).decode("UTF-8").split(":")

                session = requests.Session()

                r = session.post(config[category][id]["url"]+"/api/v2/auth/login", data={"username": authentication[0], "password": authentication[1]}, headers={"Referer":config[category][id]["url"]})

                auth_token = session.cookies.get_dict()["SID"]
                dl_info_req = session.post(config[category][id]["url"]+"/api/v2/transfer/info", cookies={"SID": auth_token})
                info_req = session.post(config[category][id]["url"]+"/api/v2/torrents/info", cookies={"SID": auth_token})


                state = {
                    "downloading": 0,
                    "seeding": 0,
                    "dl_speed": 0,
                    "ul_speed": 0
                }


                info = json.loads(info_req.text)
                speed_info = json.loads(dl_info_req.text)

                for torrent in info:
                    if torrent["state"] in ["stalledUP", "uploading"]:
                        state["seeding"] = state["seeding"] + 1
                    elif torrent["state"] in ["downloading", "stalledDL"]:
                        state["downloading"] = state["downloading"] + 1

                state["dl_speed"] = round(speed_info["dl_info_speed"] / 1024 / 1024, 1)
                state["ul_speed"] = round(speed_info["up_info_speed"] / 1024 / 1024, 1)

                session.post(config[category][id]["url"]+"/api/v2/logout", cookies={"SID": auth_token})


            
                    
                return JSONResponse(content=state)
    
            except requests.exceptions.RequestException:
                return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"online": False})
        
        # Add routes to the app
        app.include_router(router)
