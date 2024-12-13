from pathlib import Path
from typing import Annotated 
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY as _422
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import StreamingResponse
from starlette.requests import Request
import yaml
from fastapi import Depends, FastAPI
from contextlib import asynccontextmanager
from data_utils import find_audio_root_folder
from .info import InfoFinder, InfoLine, InfoError
from .info import InfoIndexer, InfoIndex
from .figures import figure_makers, FigureError
from .transcripts import makers, enrichers

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


sdh_api.mount(
    "/api/audio", StaticFiles(directory=find_audio_root_folder()), name="audio"
)

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


@sdh_api.get("/api/figure/{listing}/{clip_id}/sounds/figure.png")
def make_sounds_figure(
    figure: Annotated[str, Depends(
        figure_makers[("sounds",)]
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


@sdh_api.get("/api/index/info")
def sdh_info_index(
    info_index: Annotated[InfoLine, Depends(InfoIndexer())]
):
    try:
        return info_index
    except InfoError:
        raise HTTPException(status_code=404, detail="No index")


@sdh_api.get("/api/info/{listing}")
def sdh_info(
    info_line: Annotated[InfoLine, Depends(InfoFinder())]
):
    try:
        return info_line
    except InfoError:
        raise HTTPException(status_code=404, detail="No listing")
