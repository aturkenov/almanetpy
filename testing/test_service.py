import asyncio
import os
import pytest
import signal

from datetime import datetime

import almanet
import pydantic


testing_service = almanet.remote_service("net.testing.microservice")


class access_denied_payload(pydantic.BaseModel):
    reason: str
    datetime: datetime


class access_denied(almanet.remote_exception):
    payload: access_denied_payload


@testing_service.procedure(
    exceptions={access_denied},
)
async def greet(
    payload: str,
    session: almanet.Almanet,
) -> str:
    if not isinstance(session, almanet.Almanet):
        pytest.fail("session is not an instance of almanet")
    if payload == "guest":
        raise access_denied(
            access_denied_payload(
                reason="because you are guest",
                datetime=datetime.now(),
            )
        )
    if payload == "not_exist":
        raise access_denied(
            access_denied_payload(
                reason="user not found",
                datetime=datetime.now(),
            )
        )
    return f"Hello, {payload}!"


@testing_service.procedure
async def long_operation(
    payload: float,
    session: almanet.Almanet,
) -> None:
    if not isinstance(session, almanet.Almanet):
        pytest.fail("session is not an instance of almanet")
    almanet.logger.debug(f"sleeping {payload} seconds")
    await asyncio.sleep(payload)
    return None


_ready_to_exit = asyncio.Event()


@testing_service.post_join
async def __post_join(session: almanet.Almanet):
    payload = "Almanet"
    expected_result = "Hello, Almanet!"

    # happy path
    result = await greet(payload, force_local=False)
    assert result == expected_result

    # test validation
    with pytest.raises(almanet.rpc_invalid_payload):
        await greet(123, force_local=False)  # type: ignore

    try:
        await greet("guest", force_local=False)

        raise Exception("invalid behavior")
    # test custom exception
    except access_denied as e:
        assert isinstance(e.payload.reason, str)
        assert isinstance(e.payload.datetime, datetime)

    # test timeout
    with pytest.raises(asyncio.TimeoutError):
        await long_operation(2, force_local=False, timeout=1)

    # test timeout
    with pytest.raises(asyncio.TimeoutError):
        await long_operation(4, force_local=False, timeout=1)

    # test long operation
    await long_operation(61, force_local=False, timeout=120)

    _ready_to_exit.set()


async def _test_interruption_signal():
    os.kill(os.getpid(), signal.SIGINT)
    await asyncio.sleep(1)


async def test_service():
    almanet.serve_single(
        almanet.clients.ansqd_tcp_client("localhost:4150"),
        testing_service,
        stop_loop_on_exit=False,
    )
    await _ready_to_exit.wait()
    await _test_interruption_signal()
