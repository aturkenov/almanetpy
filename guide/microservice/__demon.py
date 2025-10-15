import almanet

from . import _greeting


if __name__ == '__main__':
    almanet.serve_single(
        _greeting.public.greeting_remote_service,
    )
