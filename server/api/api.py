import logging
from pathlib import Path
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY as _422
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor
from fastapi.responses import JSONResponse
from starlette.requests import Request
import yaml
from fastapi import Depends, FastAPI 
from contextlib import asynccontextmanager
from utils import to_server_constants
from utils import load_config
from src import use_speech_to_text_engine 
from src import use_llm_proofreader
from src import use_sound_describer
from utils import parse_srt

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


@sdh_api.get("/api/sum/{numbers}")
def open_root_api(numbers):
    return sum(
        int(s) for s in numbers.split("+")
    )


@sdh_api.get("/api/sdh/all/{listing}")
def full_sdh_transcript(listing):
    # TODO make more robust against malicious users
    folder = Path(listing).resolve().parts[-1]
    static = Path("server/client/static")
    input_folder = static / folder
    audio_path = input_folder / "voice.mp3"
    if not input_folder.is_dir() or not audio_path.is_file():
        return [] #TODO 
    L = logging.getLogger(__name__)
    config = load_config(L, Path('config'))
    # Speech transcriber
    transcript = use_speech_to_text_engine(
        L, config, audio_path, stt_engine="deepgram"
    )
    proofread_transcript = use_llm_proofreader(
        L, config, transcript
    )
    described_transcript = use_sound_describer(
        L, config, proofread_transcript, audio_path
    )
    return parse_srt(
        described_transcript
    )


@sdh_api.get("/api/sdh/info/{listing}")
def sdh_info(listing):
    # TODO make more robust against malicious users
    folder = Path(listing).resolve().parts[-1]
    static = Path("server/client/static")
    input_folder = static / folder
    info_path = input_folder / "info.yaml"
    if not input_folder.is_dir() or not info_path.is_file():
        return {} #TODO 
    return yaml.safe_load(open(info_path))
