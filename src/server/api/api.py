from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY as _422
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor
from fastapi.responses import JSONResponse
from starlette.requests import Request
from fastapi import Depends, FastAPI 
from contextlib import asynccontextmanager
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


@sdh_api.get("/api/sum/{numbers}")
def open_root_api(numbers):
    return sum(
        int(s) for s in numbers.split("+")
    )
