import api
from api.utils import messenger

import copy
import time
from quart import request

c = "main"

@api.app.route("/main/put/ready", methods = ["PUT"])
@api.auth(c)
@api.validate({"category": str, "defaults": dict})
async def main_put_ready(data, category, defaults):
    api.mem["ready"][category]["defaults"] = copy.copy(defaults)
    api.mem["ready"][category]["ready"] = True

    for name, data in defaults.items():
        if "__populate__" in data:
            for _id, _db in (await api.db.get(category, data["__populate__"])).items():
                write = False
                for key, default in data.items():
                    if (not key.startswith("__")) and key not in _db:
                        print(f"Synced key {key} in category {category} to {name} {_id}")
                        _db[key] = copy.copy(default)
                        write = True

                if write:
                    await api.db.put(
                        category,
                        f"{data['__populate__']}/{_id}",
                        _db
                    )
                    print(f"Wrote {_id}")


    return messenger.success()

@api.app.route("/main/get/online", methods = ["GET"])
@api.auth(c)
async def main_get_online(data):
    return messenger.success()

@api.app.route("/main/put/overrides", methods = ["PUT"])
@api.auth(c)
@api.validate({"bot": str, "guilds": list})
async def main_put_overrides(data, bot, guilds):
    if bot not in api.config.config["overrides"]["defaults"]:
        return messenger.error(
            "ArgError",
            f"Bot {bot} doesn't exist"
        )
    
    for guild in guilds:
        if type(guild) != dict:
            return messenger.error(
                "ArgError",
                "'guilds' must be a list of dicts"
            )

        for key in ["id", "enabled"]:
            if key not in guild:
                return messenger.error(
                    "ArgError",
                    "Guilds must have keys 'id', 'enabled'"
                )

    for guild in guilds:
        guild_id = str(guild["id"])

        try:
            odb = await api.db.get(
                c,
                f"overrides/guilds/{guild_id}"
            )

        except:
            # Check if we should autogenerate
            if data.get("autocreate"):
                odb = {
                    "priorities": copy.copy(api.config.config["overrides"]["defaults"]),
                    "data": {}
                }

            else:
                return messenger.error(
                    "NotFound",
                    f"Guild {guild_id} is not in overrides DB, and 'autocreate' is not enabled"
                )

        if "priority" in guild:
            odb["priorities"][bot] = guild["priority"]

        odb["data"][bot] = {
            "priority": odb["priorities"][bot],
            "enabled": guild["enabled"],
            "updated": int(time.time())
        }

        await api.db.put(
            c,
            f"overrides/guilds/{guild_id}",
            odb
        )

        return messenger.success()

@api.app.route("/main/get/overrides", methods = ["GET"])
@api.auth(c)
@api.validate({"guild": int, "bots": list})
async def main_get_overrides(data, guild, bots):
    for bot in bots:
        if bot not in api.config.config["overrides"]["defaults"]:
            return messenger.error(
                "ArgError",
                f"Bot {bot} doesn't exist"
            )

    try:
        odb = await api.db.get(
            c,
            f"overrides/guilds/{guild}"
        )

    except:
        return messenger.error(
            "NotFound",
            f"Guild {guild} has no overrides yet"
        )

    comp = {}
    for bot, info in odb["data"].items():
        if info["enabled"] and bot in bots:
            if info["updated"] >= time.time() - 30:
                comp[bot] = info["priority"]

    max_bot = None
    max_priority = 1000

    for bot, priority in comp.items():
        if priority < max_priority:
            max_bot = bot
            max_priority = priority

    return messenger.send(
        {
            "bot": max_bot,
            "priority": max_priority
        }
    )

@api.app.route("/main/put/override_settings", methods = ["PUT"])
@api.auth(c)
@api.validate({"bot": str, "guild": int, "priority": int})
async def main_put_override_settings(data, bot, guild, priority):
    if bot not in api.config.config["overrides"]["defaults"]:
        return messenger.error(
            "ArgError",
            f"Bot {bot} doesn't exist"
        )

    if priority > 999 or priority < 0:
        return messenger.error(
            "ArgError",
            "Priority must be between 0 and 999"
        )

    try:
        await api.db.get(
            c,
            f"overrides/guilds/{guild}"
        )

    except:
        if data.get("autocreate"):
            odb = {
                "priorities": copy.copy(api.config.config["overrides"]["defaults"]),
                "data": {}
            }

        else:
            return messenger.error(
                "NotFound",
                f"Guild {guild} is not in overrides DB, and 'autocreate' is not enabled"
            )

    odb["priorities"][bot] = priority
    await api.db.put(
        c,
        f"overrides/guilds/{guild}",
        odb
    )
    return messenger.success()

@api.app.route("/main/get/override_settings", methods = ["GET"])
@api.auth(c)
@api.validate({"guild": int})
async def main_get_override_settings(data, guild):
    try:
        odb = await api.db.get(
            c,
            f"overrides/guilds/{guild}"
        )

    except:
        if data.get("autocreate"):
            odb = {
                "priorities": copy.copy(api.config.config["overrides"]["defaults"]),
                "data": {}
            }

        else:
            return messenger.error(
                "NotFound",
                f"Guild {guild} is not in overrides DB, and 'autocreate' is not enabled"
            )
    
    return messenger.send(odb)
