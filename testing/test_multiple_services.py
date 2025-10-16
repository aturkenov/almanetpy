import asyncio

import almanet


alpha_service = almanet.remote_service(
    "net.testing.microservice.alpha",
    almanet.transports.ansqd_tcp_transport("localhost:4150"),
)

beta_service = almanet.remote_service(
    "net.testing.microservice.beta",
    almanet.transports.ansqd_tcp_transport("localhost:4150"),
)


@alpha_service.procedure
async def alpha_greet(
    payload: str,
    session: almanet.Almanet,
) -> str:
    return f"Hello, {payload}!"


_ready_to_exit = asyncio.Event()


@beta_service.post_join
async def __post_join_beta(session: almanet.Almanet):
    payload = "Almanet"
    # calling same service
    assert await alpha_greet(payload, force_local=False) == f"Hello, {payload}!"
    _ready_to_exit.set()


async def test_multiple_services(): 
    almanet.serve_single(alpha_service, stop_loop_on_exit=False)
    almanet.serve_single(beta_service, stop_loop_on_exit=False)
    await _ready_to_exit.wait()
