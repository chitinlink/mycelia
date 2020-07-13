#!/usr/bin/env python

import logging

import discord

log = logging.getLogger("Biggs")

class Biggs(discord.Client):

  def setup(self, config: dict):
    self.run(config["token"])

    self._server_id = config["server_id"] # type: int
    self._notice_channel_id = config["notice_channel_id"] # type: int

  async def on_ready(self):
    log.info(f"Logged on as {self.user}!")

  async def on_message(self, message: discord.Message):
    try:
      log.info(f"Message from {message.author}: {message.content}")
    except Exception as exc:
      log.error(exc)
      raise exc
