Biggs
=====

Bodiam moderation bot, written in Python 3, using [discord.py](https://github.com/Rapptz/discord.py).

## Running

You need [Python 3](https://www.python.org/).

1. Install the dependencies:

    ```sh
    pip install -r ./requirements.txt
    ```

2. Fill out `biggs.yml`.

3. Run `main.py`:

    ```sh
    # Normally:
    python3 main.py
    # On Windows:
    py -3 main.py
    ```

## Developing

Please use [Editorconfig](https://editorconfig.org/).

The bot producees gzipped logfiles in the `logs` folder. I recommend having an extra terminal with `tail -f ./logs/latest.log` open when debugging.
