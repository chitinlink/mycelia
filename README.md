<img src="./.github/biggs.png" width="36" height="36"> Biggs
=====

Bodiam moderation bot, written in Python 3, using [discord.py] and [TinyDB].

## Running

You need [Python 3].

1. Install the dependencies:

    ```sh
    pip install -r ./requirements.txt
    ```

2. Fill out `biggs.yml`.  

    You need to create a [Discord Application][discord-apps], enable a bot for it, and get its token.  
    You can get guild and channel IDs by right-clicking them with Developer Mode enabled.  
    The bot keeps logs and a database at `./logs/` and `./data/db.json` by default.

3. Run `main.py`:

    ```sh
    # Normally:
    python3 main.py
    # On Windows:
    py -3 main.py
    ```

## Developing

Please use [Editorconfig].

I recommend having an extra terminal with `tail -f ./logs/latest.log` open when debugging.

There is an included [VS Code `launch.json`][vscode-debugging] file for debugging.

[discord.py]:       https://github.com/Rapptz/discord.py
[TinyDB]:           https://github.com/msiemens/tinydb/
[Python 3]:         https://www.python.org/
[discord-apps]:     https://discord.com/developers/applications/
[Editorconfig]:     https://editorconfig.org/
[vscode-debugging]: https://code.visualstudio.com/Docs/editor/debugging
