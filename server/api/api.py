from pathlib import Path
from typing import Annotated 
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY as _422
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor
from fastapi.responses import JSONResponse
from starlette.requests import Request
import yaml
from fastapi import Depends, FastAPI
from contextlib import asynccontextmanager
from .transcripts import (
    TranscriptError, makers, enrichers 
)
from utils import to_server_constants

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Any startup before yield
    yield
    # Any shutdown costs

# Construct API
sdh_api = FastAPI(lifespan=lifespan)
sdh_api.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

pool = ThreadPoolExecutor(max_workers=1)


# Handle common FastAPI exceptions
@sdh_api.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    content = {'status_code': 10422, 'data': None}
    print(f'{exc}'.replace('\n', ' ').replace('   ', ' '))
    return JSONResponse(content=content, status_code=_422)


@sdh_api.get("/api")
def open_root_api(constants=Depends(to_server_constants)):
    return constants 


@sdh_api.get("/api/make/{listing}")
def none_to_all_sdh_transcript(
    transcript: Annotated[str, Depends(
        makers[()]
    )]
):
    ''' Plain '''
    try:
        return transcript
    except TranscriptError:
        raise HTTPException(status_code=404, detail="No listing")


@sdh_api.get("/api/make/{listing}/edits")
def none_to_all_sdh_transcript(
    transcript: Annotated[str, Depends(
        makers[("edits",)]
    )]
):
    ''' Edits only '''
    try:
        return transcript
    except TranscriptError:
        raise HTTPException(status_code=404, detail="No listing")


@sdh_api.get("/api/make/{listing}/edits/sounds/emotions")
def none_to_all_sdh_transcript(
    transcript: Annotated[str, Depends(
        makers[("edits", "sounds", "emotions")]
    )]
):
    ''' All SDH '''
    try:
        return transcript
    except TranscriptError:
        raise HTTPException(status_code=404, detail="No listing")


@sdh_api.post(
    "/api/enrich/{listing}/edits+sounds+emotions"
)
def none_to_all_sdh_transcript(
    transcript: Annotated[str, Depends(
        enrichers[("edits", "sounds", "emotions")][()]
    )]
):
    ''' From Plain to All SDH '''
    try:
        return transcript
    except TranscriptError:
        raise HTTPException(status_code=404, detail="No listing")


@sdh_api.get("/api/info/{listing}")
def sdh_info(listing):
    # TODO make more robust against malicious users
    folder = Path(listing).resolve().parts[-1]
    static = Path("server/client/static")
    input_folder = static / folder
    info_path = input_folder / "info.yaml"
    if not input_folder.is_dir() or not info_path.is_file():
        return {} #TODO 
    return yaml.safe_load(open(info_path))
