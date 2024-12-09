from pathlib import Path
from typing import Annotated 
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY as _422
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor
from fastapi.responses import JSONResponse
from starlette.responses import StreamingResponse
from starlette.requests import Request
import yaml
from fastapi import Depends, FastAPI
from contextlib import asynccontextmanager
from .figures import figure_makers, FigureError
from .transcripts import makers, enrichers
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


class TranscriptError(Exception):
    pass


# Handle common FastAPI exceptions
@sdh_api.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    content = {'status_code': 10422, 'data': None}
    print(f'{exc}'.replace('\n', ' ').replace('   ', ' '))
    return JSONResponse(content=content, status_code=_422)


@sdh_api.get("/api")
def open_root_api(constants=Depends(to_server_constants)):
    return constants 


@sdh_api.get("/api/figure/{listing}/{clip_id}/figure.png")
def make_plain_figure(
    figure: Annotated[str, Depends(
        figure_makers[("edits",)]
    )]
):
    ''' Plain '''
    try:
        return StreamingResponse(content=figure, media_type="image/png")
    except FigureError:
        raise HTTPException(status_code=404, detail="No listing clip")


@sdh_api.get("/api/figure/{listing}/{clip_id}/edits/figure.png")
def make_edits_figure(
    figure: Annotated[str, Depends(
        figure_makers[("edits",)]
    )]
):
    ''' Edits only '''
    try:
        return StreamingResponse(content=figure, media_type="image/png")
    except FigureError:
        raise HTTPException(status_code=404, detail="No listing clip")


@sdh_api.get(
    "/api/figure/{listing}/{clip_id}/edits/sounds/emotions/figure.png"
)
def make_all_figure(
    figure: Annotated[str, Depends(
        figure_makers[("edits", "sounds", "emotions")]
    )]
):
    ''' Full SDH '''
    try:
        return StreamingResponse(content=figure, media_type="image/png")
    except FigureError:
        raise HTTPException(status_code=404, detail="No listing clip")


@sdh_api.get("/api/make/{listing}/{clip_id}")
def make_plain(
    transcript: Annotated[str, Depends(
        makers[()]
    )]
):
    ''' Plain '''
    try:
        return transcript
    except TranscriptError:
        raise HTTPException(status_code=404, detail="No listing")


@sdh_api.get("/api/make/{listing}/{clip_id}/edits")
def make_edits(
    transcript: Annotated[str, Depends(
        makers[("edits",)]
    )]
):
    ''' Edits only '''
    try:
        return transcript
    except TranscriptError:
        raise HTTPException(status_code=404, detail="No listing")


@sdh_api.get("/api/make/{listing}/{clip_id}/edits/sounds/emotions")
def make_all(
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
    "/api/enrich/{listing}/{clip_id}/edits"
)
def enrich_with_edits(
    transcript: Annotated[str, Depends(
        enrichers[("edits",)][()]
    )]
):
    ''' From Plain to Edits '''
    try:
        return transcript
    except TranscriptError:
        raise HTTPException(status_code=404, detail="No listing")


@sdh_api.post(
    "/api/enrich/{listing}/{clip_id}/sounds"
)
def enrich_with_sounds(
    transcript: Annotated[str, Depends(
        enrichers[("sounds",)][()]
    )]
):
    ''' From Plain to Sounds '''
    try:
        return transcript
    except TranscriptError:
        raise HTTPException(status_code=404, detail="No listing")


@sdh_api.post(
    "/api/enrich/{listing}/{clip_id}/edits+sounds+emotions"
)
def enrich_with_all(
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
def sdh_info(
    listing, constants=Depends(to_server_constants)
):
    # TODO make more robust against malicious users
    folder = Path(listing).resolve().parts[-1]
    static = Path(constants["client"]["audio_root"])
    input_folder = static / folder
    info_path = input_folder / "info.yaml"
    if not input_folder.is_dir() or not info_path.is_file():
        return {} #TODO 
    return yaml.safe_load(open(info_path))
