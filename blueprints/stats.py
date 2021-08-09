import api

from api.utils import messenger

from quart import request, make_response, Blueprint

import copy
import time
import pytz
import datetime
import asyncio

tz = pytz.timezone("America/Denver")

c = "stats"

blueprint = Blueprint("stats", __name__)

@blueprint.route("/stats/get/api", methods = ["GET"])
@api.auth(c)
async def stats_get_api(data):
    return messenger.send(
        await api.db.get(
            c,
            "api/main"
        )
    )

@blueprint.route("/stats/get/bot", methods = ["GET"])
@api.auth(c)
@api.validate({"bot": str})
async def stats_get_bot(data, bot_name):
    if bot_name == "all":
        bots = await api.db.list(
            c,
            "bots"
        )

        for name, stats in bots.items():
            update_period(stats, 0)
            #update_uptime(stats)

            await api.db.put(
                c,
                f"bots/{name}",
                stats
            )

        return messenger.send(
            bots
        )

    else:
        try:
            stats = await api.db.get(
                c,
                f"bots/{bot_name}"
            )

        except:
            return messenger.error(
                "ArgError",
                f"Bot {bot_name} not found"
            )

        else:
            update_period(stats, 0)

            await api.db.put(
                c,
                f"bots/{bot_name}",
                stats
            )

            return messenger.send(
                stats
            )

@blueprint.route("/stats/put/update", methods = ["PUT"])
@api.auth(c)
@api.validate({"bot": str, "commands": dict, "uptime": float})
async def stats_put_update(data, bot_name, command_count, uptime):
    try:
        stats = await api.db.get(
            c,
            f"bots/{bot_name}"
        )

    except:
        stats = {
            "commands": {
                "total": 0,
                "categories": {},
                "day": {
                    "day": None,
                    "count": 0
                },
                "history": [],
                "extra": {}
            },
            "uptime": {
                "total": {
                    "start": None,
                    "count": 0
                },
                "month": {
                    "month": None,
                    "start": None,
                    "count": 0
                }
            }
        }

    # Update command totals
    stats["commands"]["total"] += command_count["__total__"]
    update_period(stats, command_count["__total__"])

    # Update category/command totals
    for category, commands in command_count.items():
        if category == "__total__":
            continue

        if category.startswith("__"):
            if category not in stats["commands"]["extra"]:
                stats["commands"]["extra"][category] = 0

            stats["commands"]["extra"][category] += commands
            continue

        if category not in stats["commands"]["categories"]:
            stats["commands"]["categories"][category] = {}

        cat = stats["commands"]["categories"][category]

        for command, count in commands.items():
            if command not in cat:
                cat[command] = 0

            cat[command] += count

    # Append uptime
    if stats["uptime"]["total"]["start"] is None:
        stats["uptime"]["total"]["start"] = float(time.time()) - uptime

    update_uptime(stats)

    stats["uptime"]["total"]["count"] += uptime
    stats["uptime"]["month"]["count"] += uptime

    await api.db.put(
        c,
        f"bots/{bot_name}",
        stats
    )

    return messenger.success()

def update_uptime(
        stats
    ):

    month = strf("%Y-%m")

    if stats["uptime"]["month"]["month"] != month:
        stats["uptime"]["month"] = {
            "month": month,
            "start": time.time(),
            "count": 0
        }

def update_period(
        stats,
        count
    ):

    day = strf("%Y-%m-%d")

    if stats["commands"]["day"]["day"] != day:
        if stats["commands"]["day"]["day"] is not None:
            stats["commands"]["history"].append(stats["commands"]["day"])
        stats["commands"]["day"] = {
            "day": day,
            "count": 0
        }

    stats["commands"]["day"]["count"] += count

def strf(template):
    current = datetime.datetime.utcnow()

    return pytz.utc.localize(current).astimezone(tz).strftime(template)


async def wrap_stats(response):
    await update_stats(response)

    return response

@api.app.after_request
async def update_stats(response):
    stats = await api.db.get(
        c,
        "api/main"
    )

    # Update time
    hour = time.time() // 3600
    if hour != stats["current"]:
        stats["categories"] = {}
        for category in list(api.config.data) + api.config.ignore_ready:
            stats["categories"][category] = {
                "success": 0,
                "fail": 0
            }

        stats["current"] = hour

    initial_path = request.url.split("://")[1].split("/")[1]

    if initial_path in stats["categories"]:
        path = initial_path

    else:
        path = "unknown"
    
    if response.status_code == 200:
        cat = "success"

    else:
        cat = "fail"

    stats["categories"][path][cat] += 1
    stats["total"][cat] += 1

    await api.db.put(
        c,
        "api/main",
        stats
    )

    return response