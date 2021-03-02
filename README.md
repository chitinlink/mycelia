<h1 align="center">
  <img src="./.readme/biggs.png" width="25%"><img src="./.readme/smalls.png" width="25%"><br>
  Mycelia
</h1>

Mycelia uses [discord.py], among other things. ([requirements.txt](./requirements.txt))

Biggs is the Bodiam moderation/utilities bot.  
Smalls is a music bot used in Bodiam and elsewhere.

- [Requirements](#requirements)
- [Basic setup](#basic-setup)
- [Proper setup](#proper-setup)
- [Updates](#updates)
- [Useful commands](#useful-commands)
- [Developing](#developing)

## Requirements

* Python 3.8
* systemd (if you install)
* Java 11 (for Smalls' Lavalink)

## Basic setup

Create a `settings.yml` file and fill it in. (see [`settings.example.yml`](./settings.example.yml))

If you're going to run Smalls, create a `lavalink/application.yml` file and fill it in. (see [`lavalink/application.example.yml`](./lavalink/application.example.yml))

```sh
# Install the requirements
pip3 install -r requirements.txt
# Make it an executable
chmod +x ./mycelia.py
# Go wild
./mycelia.py
```

## Proper setup

```sh
./mycelia.py install all
```

This will install the required Python modules and register both bots as [systemd user units][systemd-user].  
**Note**: Because they're user units, they'll shut down once your user is logged out. To prevent this, enable user-linger:

```sh
loginctl enable-linger $USER
```

## Updates

```sh
./mycelia.py update all
```

## Useful commands

* Stop the bots and uninstall their systemd units: `./mycelia.py uninstall all`
* Unit status: `systemctl --user status biggs.service`
* Unit logs: `journalctl --user -u biggs.service -n 50` (Add `-f` for live logs)

## Developing

Please use [Editorconfig].

There is an included [VS Code `launch.json`][vscode-debugging] file for debugging.

Make sure you're browsing the documentation for the proper version of the libraries used in the bot. Check [requirements.txt](./requirements.txt) to be sure.

[discord.py]:       https://github.com/Rapptz/discord.py
[systemd-user]:     https://wiki.archlinux.org/index.php/Systemd/User
[Editorconfig]:     https://editorconfig.org/
[vscode-debugging]: https://code.visualstudio.com/Docs/editor/debugging
