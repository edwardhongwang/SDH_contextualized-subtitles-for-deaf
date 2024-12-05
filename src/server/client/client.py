from pathlib import Path
from starlette.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI

ROOT = Path("src/server/client")

sdh_client = FastAPI()

'''
Client-side single page app
'''

@sdh_client.get("/")
async def open_root_html():
    return FileResponse(ROOT / 'index.html')

sdh_client.mount(
    "/static", StaticFiles(directory=ROOT / "static"), name="static"
)
