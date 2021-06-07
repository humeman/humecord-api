import api
from . import auth
from . import messenger

from functools import wraps
from quart import request

def wrap_auth(category):
    def inner(function):
        @wraps(function)
        async def dec(*args, **kwargs):
            if request.method == "GET":
                data = request.args

            elif request.method in ["PUT", "POST", "PATCH"]:
                data = await request.get_json()
            
            if category not in api.config.ignore_ready:
                if not api.mem["ready"][category]["ready"]:
                    return messenger.error(
                        "AuthError",
                        f"Bot {category} isn't ready"
                    )

            err = await auth.authenticate(
                data,
                category
            )

            if err is not None:
                return err

            return await function(data, *args, **kwargs)

        return dec

    return inner

def wrap_validate(values):
    def inner(function):
        @wraps(function)
        async def dec(*args, **kwargs):
            validated = []

            if request.method == "GET":
                data = request.args

            elif request.method in ["PUT", "POST", "PATCH"]:
                data = await request.get_json()

            for key, type_ in values.items():
                if key not in data:
                    return messenger.error(
                        "ArgError",
                        f"Missing key {key}"
                    )

                if type(data[key]) != type_:
                    try:
                        new = type_(data[key])

                    except:
                        return messenger.error(
                            "ArgError",
                            f"Key {key} must be of type {type_}"
                        )

                else:
                    new = data[key]
                
                validated.append(new)

            return await function(*args, *validated, **kwargs)

        return dec
    
    return inner