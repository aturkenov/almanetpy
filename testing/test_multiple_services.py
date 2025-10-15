import asyncio

import pytest

import almanet


alpha_service = almanet.remote_service(
    "net.testing.microservice.alpha",
    almanet.transports.ansqd_tcp_transport("localhost:4150"),
)


alpha_clone_service = almanet.remote_service(
    alpha_service.pre,
    alpha_service.transport,
)


beta_service = almanet.remote_service(
    "net.testing.microservice.beta",
    almanet.transports.ansqd_tcp_transport("localhost:4150"),
)


@alpha_service.procedure
async def greet_alpha(
    payload: str,
    session: almanet.Almanet,
) -> str:
    return f"Hello, {payload}!"


@beta_service.procedure
async def greet_beta(
    payload: str,
    session: almanet.Almanet,
) -> str:
    return f"Hello, {payload}!"


_ready_to_exit = asyncio.Event()


@alpha_clone_service.post_join
async def __post_join_alpha_clone(session: almanet.Almanet):
    payload = "Almanet"
    # calling same service
    assert await greet_alpha(payload, force_local=False) == f"Hello, {payload}!"

    # trying to call external service without joining
    with pytest.raises(RuntimeError):
        await greet_beta(payload, force_local=False)

    async with beta_service.make_session():
        with pytest.raises(TimeoutError):
            await greet_beta(payload, force_local=False, timeout=2)

    await beta_service.include_into(session)
    with pytest.raises(TimeoutError):
        await greet_beta(payload, force_local=False, timeout=2)

    _ready_to_exit.set()


async def test_multiple_services(): 
    almanet.serve_single(alpha_service, stop_loop_on_exit=False)
    almanet.serve_single(alpha_clone_service, stop_loop_on_exit=False)
    await _ready_to_exit.wait()
