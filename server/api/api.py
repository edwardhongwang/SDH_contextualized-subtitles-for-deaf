from pathlib import Path
import shutil
import logging
import json
from io import BytesIO
from typing import Annotated,Generator
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY as _422
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import StreamingResponse
from starlette import requests
import yaml
from fastapi import Request, Depends, FastAPI
from contextlib import asynccontextmanager
from data_utils import find_audio_root_folder
from data_utils import to_server_constants
from data_utils import should_server_export
from data_utils import find_listing_info
from .info import InfoFinder, InfoLine
from .info import InfoIndexer, InfoIndex
from .figures import figure_makers, FigureError
from .transcripts import makers, enrichers, Transcript
from src import TranscriptError, InfoError

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


def export(content, url, datatype="filepath"):
    constants = to_server_constants()
    can_export = should_server_export()
    export_root = constants["api"].get("export_root")
    if not can_export or not export_root:
        return content
    export_root = Path(export_root)
    if not export_root.is_dir():
        return content
    export_path = export_root / url[1:]
    export_parent = export_path.parents[0]
    L = logging.getLogger(__name__)
    L.info(f'Exporting "{export_path.name}" in "{export_parent}"')
    export_parent.mkdir(parents=True, exist_ok=True)
    if datatype == "filepath":
        suffix = export_path.suffix
        protected = ('.mp3',)
        licenses = (None,) # Todo after class project
        info = find_listing_info(export_parent.parts[-2])
        auth = info.get("license", None)
        # Due to copyright, don't export mp3 files
        if suffix in protected and auth not in licenses:
            L.error(
                f'Can\'t export "{suffix}" with "{auth}" license'
            )
        else:
            shutil.copy(content, export_path)
        return content
    elif datatype == "png":
        with open(export_path, "wb") as f:
            f.write(content.getbuffer())
        content.seek(0)
        return content
    elif datatype == "pydantic":
        with open(export_path, 'w') as f:
            json.dump(content, f)
        return content
    L.warning(f'Unsupported export datatype "{datatype}"')
    return content

# Handle common FastAPI exceptions
@sdh_api.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: requests.Request, exc: RequestValidationError
):
    content = {'status_code': 10422, 'data': None}
    print(f'{exc}'.replace('\n', ' ').replace('   ', ' '))
    return JSONResponse(content=content, status_code=_422)


class StaticExportable(StaticFiles):

    def file_response(self, *args, **kwargs):
        resp = super().file_response(*args, **kwargs)
        content = Path(resp.path)
        root = Path(self.directory).resolve()
        url = str(content.relative_to(root))
        export(content, f'/data/{url}', "filepath")
        return resp


sdh_api.mount(
    "/data", StaticExportable(directory=find_audio_root_folder()),
    name="data"
)

@sdh_api.get("/api/figure/{listing}/{clip_id}/figure.png")
def make_plain_figure(
    request: Request,
    figure: Annotated[Generator[BytesIO, None, None], Depends(
        figure_makers[()]
    )]
):
    ''' Plain '''
    try:
        content = export(next(figure), request.url.path, 'png')
        return StreamingResponse(content=content, media_type="image/png")
    except FigureError:
        raise HTTPException(status_code=404, detail="No listing clip")


@sdh_api.get("/api/figure/{listing}/{clip_id}/edits/figure.png")
def make_edits_figure(
    request: Request,
    figure: Annotated[Generator[BytesIO, None, None], Depends(
        figure_makers[("edits",)]
    )]
):
    ''' Edits only '''
    try:
        content = export(next(figure), request.url.path, 'png')
        return StreamingResponse(content=content, media_type="image/png")
    except FigureError:
        raise HTTPException(status_code=404, detail="No listing clip")


@sdh_api.get("/api/figure/{listing}/{clip_id}/sounds/figure.png")
def make_sounds_figure(
    request: Request,
    figure: Annotated[Generator[BytesIO, None, None], Depends(
        figure_makers[("sounds",)]
    )]
):
    ''' Edits only '''
    try:
        content = export(next(figure), request.url.path, 'png')
        return StreamingResponse(content=content, media_type="image/png")
    except FigureError:
        raise HTTPException(status_code=404, detail="No listing clip")


@sdh_api.get(
    "/api/figure/{listing}/{clip_id}/edits/sounds/emotions/figure.png"
)
def make_all_figure(
    request: Request,
    figure: Annotated[Generator[BytesIO, None, None], Depends(
        figure_makers[("edits", "sounds", "emotions")]
    )]
):
    ''' Full SDH '''
    try:
        content = export(next(figure), request.url.path, 'png')
        return StreamingResponse(content=content, media_type="image/png")
    except FigureError:
        raise HTTPException(status_code=404, detail="No listing clip")


@sdh_api.get("/api/make/{listing}/{clip_id}")
def make_plain(
    request: Request,
    transcript: Annotated[Generator[Transcript, None, None], Depends(
        makers[()]
    )]
):
    ''' Plain '''
    try:
        content = next(transcript).json_serialized()
        return export(content, request.url.path, 'pydantic')
    except TranscriptError:
        raise HTTPException(status_code=404, detail="No listing")


@sdh_api.get("/api/make/{listing}/{clip_id}/edits")
def make_edits(
    request: Request,
    transcript: Annotated[Generator[Transcript, None, None], Depends(
        makers[("edits",)]
    )]
):
    ''' Edits only '''
    try:
        content = next(transcript).json_serialized()
        return export(content, request.url.path, 'pydantic')
    except TranscriptError:
        raise HTTPException(status_code=404, detail="No listing")


@sdh_api.get("/api/make/{listing}/{clip_id}/edits/sounds/emotions")
def make_all(
    request: Request,
    transcript: Annotated[Generator[Transcript, None, None], Depends(
        makers[("edits", "sounds", "emotions")]
    )]
):
    ''' All SDH '''
    try:
        content = next(transcript).json_serialized()
        return export(content, request.url.path, 'pydantic')
    except TranscriptError:
        raise HTTPException(status_code=404, detail="No listing")


@sdh_api.post(
    "/api/enrich/{listing}/{clip_id}/edits"
)
def enrich_with_edits(
    request: Request,
    transcript: Annotated[Generator[Transcript, None, None], Depends(
        enrichers[("edits",)][()]
    )]
):
    ''' From Plain to Edits '''
    try:
        content = next(transcript).json_serialized()
        return export(content, request.url.path, 'pydantic')
    except TranscriptError:
        raise HTTPException(status_code=404, detail="No listing")


@sdh_api.post(
    "/api/enrich/{listing}/{clip_id}/sounds"
)
def enrich_with_sounds(
    request: Request,
    transcript: Annotated[Generator[Transcript, None, None], Depends(
        enrichers[("sounds",)][()]
    )]
):
    ''' From Plain to Sounds '''
    try:
        content = next(transcript).json_serialized()
        return export(content, request.url.path, 'pydantic')
    except TranscriptError:
        raise HTTPException(status_code=404, detail="No listing")


@sdh_api.post(
    "/api/enrich/{listing}/{clip_id}/edits+sounds+emotions"
)
def enrich_with_all(
    request: Request,
    transcript: Annotated[Generator[Transcript, None, None], Depends(
        enrichers[("edits", "sounds", "emotions")][()]
    )]
):
    ''' From Plain to All SDH '''
    try:
        content = next(transcript).json_serialized()
        return export(content, request.url.path, 'pydantic')
    except TranscriptError:
        raise HTTPException(status_code=404, detail="No listing")


@sdh_api.get("/api/index/info")
def sdh_info_index(
    request: Request,
    info_index: Annotated[Generator[InfoIndex, None, None], Depends(InfoIndexer())]
):
    try:
        content = next(info_index).json_serialized()
        return export(content, request.url.path, 'pydantic')
    except InfoError:
        raise HTTPException(status_code=404, detail="No index")


@sdh_api.get("/api/info/{listing}")
def sdh_info(
    request: Request,
    info_line: Annotated[Generator[InfoLine, None, None], Depends(InfoFinder())]
):
    try:
        content = next(info_line).json_serialized()
        return export(content, request.url.path, 'pydantic')
    except InfoError:
        raise HTTPException(status_code=404, detail="No listing")
