import asyncio
import uvicorn
from utils import to_server_constants


def to_server(port, scope, module, log_level):
    print(f'Running {scope} {module} on port {port}')
    uvicorn_config = {
        "port": port,
        "reload": True,
        "host": "0.0.0.0",
        "log_level": log_level,
        "app": f"src:{scope}_{module}"
    }
    # Run with or without TLS
    config = uvicorn.Config(**uvicorn_config)
    return uvicorn.Server(config)


async def run_server(server):
    await server.serve()


async def run_servers(api_port=7777, client_port=8888):

    loop = asyncio.get_event_loop()
    api_server = to_server(
        api_port, 'sdh', 'api', 'info'
    )
    client_server = to_server(
        client_port, 'sdh', 'client', 'error'
    )
    api_task = asyncio.ensure_future(run_server(api_server))
    client_task = asyncio.ensure_future(run_server(client_server))

    # Consider following updates here:
    # https://github.com/encode/uvicorn/pull/1600
    tasks = [api_task, client_task]
    for job in asyncio.as_completed(tasks):
        try: 
            results = await job
        finally:
            break
