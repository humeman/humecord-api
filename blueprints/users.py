import api

from api.utils import messenger

from quart import request, Blueprint

import time
import copy

c = "users"

blueprint = Blueprint("users", __name__)

@blueprint.route("/users/get/user", methods = ["GET"])
@api.auth(c)
async def users_get_user(data):
    if "id" in data:
        try:
            uid = int(data["id"])

        except:
            return messenger.error(
                "ArgError",
                "id must be an int"
            )

        try:
            return messenger.send(
                await api.db.get(
                    c,
                    f"users/{data['id']}"
                )
            )

        except:
            if data.get("autocreate"):
                # Generate new
                user = copy.copy(api.config.defaults["user"])

                user["created_at"] = int(time.time())

                await api.db.put(
                    c,
                    f"users/{data['id']}",
                    user
                )

                return messenger.send(
                    user
                )

            return messenger.error(
                "ArgError",
                f"User {uid} doesn't exist"
            )

    return messenger.send(
        await api.db.get(
            c,
            "blocked"
        )
    )

@blueprint.route("/users/put/user", methods = ["PUT"])
@api.auth(c)
@api.validate({"id": int, "db": dict})
async def users_put_user(data, uid, changes: dict):
    uid = str(uid)

    try:
        user = await api.db.get(
            c,
            f"users/{uid}"
        )

    except:
        # Generate new
        user = copy.copy(
            (await api.db.get(
                "main",
                f"ready/{c}"
            ))["defaults"]["user"]
        )

        user["created_at"] = int(time.time())

        changes = {
            **user,
            **changes
        }

    """if data.get("duration") is None:
        comp["duration"] = None

    else:
        if type(data["duration"]) != int:
            return messenger.error(
                "ArgError",
                "Duration must be an int or None"
            )

        comp["duration"] = data["duration"]
        comp["ends_at"] = int(time.time()) + data["duration"]

    if data.get("reason") is not None:
        if type(data["reason"]) != str:
            return messenger.error(
                "ArgError",
                "Duration must be a string"
            )

        comp["reason"] = data["reason"]"""

    await api.db.update(
        c,
        f"users/{uid}",
        changes
    )

    return messenger.send(
        user
    )