# creating a bot

Bots you wish to use on the API must follow this process.

## process

1. **Create a blueprint.**
    * First, go to the `blueprints/` folder, and create a `botname.py` file (depending on what the bot's API will be named).
    * For a helpful starting point, you can copy and paste the `sample.py` file in there and edit as needed.
    * Make sure you define the category name by changing the `c` variable.

2. **Import the blueprint.**
    * Head over to `/main.py`.
    * Down in the Imports section, import your blueprint:
        `from blueprints import botname`

3. **Register the blueprint in config.**
    * Open `config.yml`
    * Add database entries under the `data` config option.
        * For this example:
        ```yaml
        botname:
            guilds: {}
        ```
    * Add an authentication key.
        * This can be anything. Preferrably make it long and random.
        * Then, register it to `main` and the bot's own API.
        * For example:
            * `key_value: [main, botname]`

4. Start writing!
    * Check out the other API docs for instructions on that.