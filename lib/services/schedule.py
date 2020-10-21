import json
import logging
import datetime

import jsonschema
from tinydb import where
from discord.ext import commands, tasks

from lib.utils import is_mod, in_guild, react, md_list

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

class Schedule(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot
    self._schedule = bot._db.table("schedule")
    self._schedule_task_schema = json.load(open("./lib/schema/schedule_task.json"))
    self.tick.start()

  # Guild-only
  async def cog_check(self, ctx: commands.Context):
    return in_guild(ctx)

  # Add to schedule
  def add_task(self, task: dict):
    """ Insert """
    # Validate task
    jsonschema.validate(instance=task, schema=self._schedule_task_schema)
    # Submit validated JSON
    self._schedule.insert(task)

  # Commands
  @commands.group(aliases=["sch"])
  async def schedule(self, ctx: commands.Context):
    """ Restricted to moderators """
    if ctx.invoked_subcommand is None: await ctx.send_help("schedule")

  @schedule.command(aliases=["a"])
  @commands.check(is_mod)
  async def add(self, ctx: commands.Context, *, data: str):
    """ Adds a task to the schedule """
    try:
      # Parse and add task
      data = json.loads(data)
      self.add_task(data)

      await react(ctx, "confirm")
      await ctx.send(f"Added task of type `{data['type']}` to the schedule.")

    except (jsonschema.exceptions.ValidationError, json.decoder.JSONDecodeError) as exc:
      await react(ctx, "deny")
      if exc.__class__ == json.decoder.JSONDecodeError: msg = exc
      else:                                             msg = exc.message
      await ctx.send(f"JSON Error: {msg}")

  @schedule.command(aliases=["l"])
  @commands.check(is_mod)
  async def list(self, ctx: commands.Context):
    """ List existing tasks """
    await ctx.send(md_list(self._schedule.all()))

  @tasks.loop(seconds=1)
  async def tick(self):
    for task in self._schedule.all():
      # Check if we're past the time for the task
      if datetime.datetime.now() - datetime.datetime.strptime(task["at"], TIME_FORMAT) >= datetime.timedelta(0):
        # Do the task
        if task["type"] == "message":
          # await self.bot._guild.get_channel(task["channel"]).send(task["message"])
          print(task["message"])
        #if task["type"] == "purge":
        # TODO:
        # 1. Do the task
        # 2. Figure out what to do when several "repeat cycles" have gone by.
        #    Maybe calculate how many times to repeat the task? Only if relevant.
        #    Only need to purge once, then fast-forward "at".

        # If it's set to repeat, then reschedule
        if "repeat_after" in task:
          # at += repeat_after
          new_task = task
          new_task["at"] = (datetime.datetime.strptime(
            new_task["at"], TIME_FORMAT) +
            datetime.timedelta(seconds=new_task["repeat_after"])
          ).strftime(TIME_FORMAT)
          # Add the new task to the schedule
          self._schedule.insert(new_task)

        # Remove from the schedule
        self._schedule.remove(doc_ids=[task.doc_id])

  @tick.before_loop
  async def before_tick(self):
    # Wait for on_ready before beginning
    await self.bot.wait_until_ready()

  def cog_unload(self):
    # Cancel task when unloading the cog
    self.tick.cancel()
