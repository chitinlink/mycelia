<img src="./.github/biggs.png" width="36" height="36"> Biggs
============================================================

Bodiam moderation bot, written in Python 3, using [discord.py] and [TinyDB].

- [Running](#running)
  - [Installing](#installing)
  - [Useful commands](#useful-commands)
  - [Updating](#updating)
  - [Uninstalling](#uninstalling)
- [Developing](#developing)

## Running

You need [Python 3].

### Installing

#### 1. Fill out `biggs.yml`.  

You need to create a [Discord Application][discord-apps], enable a bot for it, and get its token.  
You can get guild, channel, and role IDs by right-clicking them with Developer Mode enabled.  
The bot keeps logs and a database at `./logs/` and `./data/db.json` by default.

#### 2. Run the install script.

```sh
sh ./scripts/install.sh
```
    
This will install the required Python modules and register Biggs as a [systemd user unit][systemd-user].

⚠️ **WARNING**:  
Because this is a user unit, it'll shut down once your user is logged out. To prevent this, enable user-linger:

```sh
loginctl enable-linger $USER
```

### Useful commands

* Unit status: `systemctl --user status biggs.service` 
* Unit logs: `journalctl --user -u biggs.service`
* Tail logs: `tail -f ./logs/latest.log`

### Updating

⚠️ **Back up `biggs.yml`** (and any other changes you want to keep) before updating.

Once you have, this script will essentially uninstall, pull the latest version, and then reinstall:
```sh
./scripts/update.sh
```

### Uninstalling

This script stops and unregisters the systemd unit:

```sh
./scripts/uninstall.sh
```

## Developing

Please use [Editorconfig].

There is an included [VS Code `launch.json`][vscode-debugging] file for debugging.

[discord.py]:       https://github.com/Rapptz/discord.py
[TinyDB]:           https://github.com/msiemens/tinydb/
[Python 3]:         https://www.python.org/
[discord-apps]:     https://discord.com/developers/applications/
[systemd-user]:     https://wiki.archlinux.org/index.php/Systemd/User
[Editorconfig]:     https://editorconfig.org/
[vscode-debugging]: https://code.visualstudio.com/Docs/editor/debugging
