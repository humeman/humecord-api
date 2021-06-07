from quart import request

import api
from . import messenger

async def authenticate(
        args: dict,
        category: str
    ):

    if request.remote_addr not in api.config.ips:
        return messenger.error(
            "AuthError",
            "Request not sent from whitelisted IP"
        )

    if "key" not in args:
        return messenger.error(
            "AuthError",
            "Missing authentication key"
        )

    key = args["key"]

    if key not in api.config.auth:
        return messenger.error(
            "AuthError",
            "Invalid key"
        )

    if category not in api.config.auth[key]:
        return messenger.error(
            "AuthError",
            f"Not allowed to access category {category}"
        )