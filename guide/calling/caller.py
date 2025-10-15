import asyncio

import guide.microservice


async def main():
    # Join to remote network
    async with guide.microservice.greeting_remote_service.make_session():
        payload = "Aidar"

        # catching rpc exceptions with `try` and `except almanet.remote_exception` statement
        try:
            result = await guide.microservice.greet(payload)
            print(result)
        except guide.microservice.access_denied as e:
            print(f"during call {guide.microservice.greet.uri}({payload}): {e}")


if __name__ == "__main__":
    asyncio.run(main())
