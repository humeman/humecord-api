import api

from api.utils import messenger

from quart import request

c = "sample"

@api.app.route("/sample/get/guild", methods = ["GET"])
@api.auth(c)
@api.validate({"id": int})
async def sample_get_guild(data, guild):
    try:
        guild = await api.db.get(
            c,
            f"guilds/{guild}"
        )

    except (ValueError, api.utils.exceptions.NotFound):
        if data.get("autocreate"):
            await api.db.put(
                c,
                f"guilds/{guild}",
                api.mem["ready"][c]["defaults"]["guild"]
            )

            guild = await api.db.get(
                c,
                f"guilds/{guild}"
            )


        else:
            return messenger.error(
                "ArgError",
                f"Guild {guild} does not exist."
            )
    
    return messenger.send(guild)

@api.app.route("/sample/put/guild", methods = ["PUT"])
@api.auth(c)
@api.validate({"id": int, "db": dict})
async def sample_put_guild(data, guild, db):
    await api.db.put(
        c,
        f"guilds/{guild}",
        db
    )

    return messenger.success()