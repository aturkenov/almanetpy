import almanet

__all__ = [
    "greeting_remote_service",
    "access_denied",
    "greet",
]

greeting_remote_service = almanet.new_remote_service(
    __package__ or "guide.microservice.greeting",
    almanet.transports.ansqd_tcp_transport("localhost:4150"),
)


class access_denied(almanet.remote_exception):
    """Custom RPC exception"""

    payload: str


@greeting_remote_service.public_procedure(exceptions={access_denied})
async def greet(payload: str) -> str:
    """
    Procedure that returns greeting message.

    Raises:
        - access_denied if `payload` is `"guest"`
    """
    ...
