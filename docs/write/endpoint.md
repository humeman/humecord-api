# writing API endpoints

This is a quick demo on how to write API endpoints.

## basic structure

### decorators
Each API function must have, at minimum, two decorators.

Take the sample request:
```py
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
```

Decorators are the `@api` calls at the start of the function.

**Quart route:**
`@api.app.route("/sample/put/guild, methods = ["PUT"])`
Here, you have to define both the URL and the methods that are allowed for this route.
Valid methods are:
    GET, PUT, POST, PATCH, DELETE

**Authentication call:**
`@api.auth(c)`
This makes sure the request is authenticated.

**Data validation call:** (optional)
`@api.validate({"id": int, "db": dict})`
This automatically validates any parameters that are needed to perform the request, and returns an error if they are not present or of an invalid type.
Validation args should be a dict:

```py
{
    "required_key": str,
    "some_boolean": bool
}
```

In this example, "required_key" has to be a string and "some_boolean" has to be a boolean.

When they're validated, they're passed as args to the function, alongside `data` - the actual request JSON or args.

So, for this example:
```py
async def function(data, required_key, some_boolean):
```
is correct.

### database access

The following calls can be used to access the database:

```py
# Gets something from the database
data = await api.db.get(
    c, # category (use c for simplicity - it's defined at the top of each file)
    "guilds/1" # path - would get db["guilds"]["1"]
)

# Make edits to data here

# Put it back
await api.db.put(
    c,
    "guilds/1",
    data # Data to set the path to - in this case, db["guilds"]["1"] = data
)
```

And, the following exceptions can be raised:
```py
api.utils.exceptions.NotFound # Can't find file
api.utils.exceptions.SecurityError # Attempted string escape
```

### messenger
To send data back to the client, use the `messenger` util (humecord.utils.messenger).

Some examples:
```py
# No data to send - just say that the operation was successful
return messenger.success()

# Something went wrong
return messenger.error(
    "SampleError",  # Error type - for example, AuthError, ArgError, so on
    "More info about the error" # Full error message
)

# Return some data
return messenger.data(
    data # Sent as JSON
)
```