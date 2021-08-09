import api

from api.utils import messenger

from quart import request, make_response, Blueprint

import copy
import time

c = "status"

blueprint = Blueprint("status", __name__)

@blueprint.route("/status/get/bot", methods = ["GET"])
@api.auth(c)
@api.validate({"bot": str})
async def status_get_bot(data, bot_name):
    if bot_name == "all":
        return messenger.send(
            await api.db.list(
                c,
                "bots"
            )
        )

    else:
        try:
            bot = await api.db.get(
                c,
                f"bots/{bot_name}"
            )

        except:
            return messenger.error(
                "ArgError",
                f"Bot {bot_name} not found"
            )

        else:
            return messenger.send(
                bot
            )

@blueprint.route("/status/put/bot", methods = ["PUT"])
@api.auth(c)
@api.validate({"bot": str, "details": dict})
async def status_put_update(data, bot_name, details):
    try:
        status = await api.db.get(
            c,
            f"bots/{bot_name}"
        )

    except:
        status = {
            "last_ping": 0,
            "details": {},
            "online": False,
            "error": False
        }


    status.update(
        {
            "last_ping": time.time(),
        }
    )

    status["details"].update(details)

    if data.get("shutdown"):
        status["online"] = False

    else:
        status["online"] = True

    status["error"] = False

    await api.db.put(
        c,
        f"bots/{bot_name}",
        status
    )

    return messenger.success()
               
@blueprint.route("/status/put/override", methods = ["PUT"])
@api.auth(c)
@api.validate({"bot": str, "changes": dict})
async def status_put_override(data, bot_name, changes):
    try:
        status = await api.db.get(
            c,
            f"bots/{bot_name}"
        )

    except:
        status = {
            "last_ping": 0,
            "details": {},
            "online": False,
            "error": False
        }

        changes = {
            **status,
            **changes
        }

    
    await api.db.update(
        c,
        f"bots/{bot_name}",
        changes
    )

    return messenger.success()