import json

import jsonschema
from discord.ext import commands, tasks
from asyncio import create_task as await_this
import schedule

from lib.utils.etc import Service, react, TIME_FORMAT
from lib.utils.checks import is_mod, in_guild
from lib.utils.text import fmt_list, fmt_code

#TODO: add remove to sch
#TODO: add purge handling

class Schedule(Service):
  def __init__(self, bot: commands.Bot):
    super().__init__(bot)
    self._schedule = bot._db.table("schedule")
    self._schedule_task_schema = json.load(open("./lib/schema/schedule_task.json"))

    # Set up all saved tasks
    for task in self._schedule.all():
      self.setup_task(task)

    self.tick.start()

  # Guild-only
  async def cog_check(self, ctx: commands.Context):
    return in_guild(ctx) and is_mod(ctx)

  # Set up one task
  def setup_task(self, task):
    def task_message(channel, message):
      await_this(channel.send(message))

    if task["type"] == "message":
      eval(task["directive"])(task_message, self.bot._guild.get_channel(task["channel"]), task["message"])

  #Add to schedule
  def add_task(self, task: dict):
    # Validate task
    jsonschema.validate(instance=task, schema=self._schedule_task_schema)
    # Submit validated JSON
    self._schedule.insert(task)
    # Set up task immediately
    self.setup_task(task)

  # Schedule commands
  @commands.group(aliases=["sch"])
  async def schedule(self, ctx: commands.Context):
    """ (Restricted to moderators) """
    if ctx.invoked_subcommand is None: await ctx.send_help("schedule")

  @schedule.command(aliases=["a"])
  async def add(self, ctx: commands.Context, *, data: str):
    """ Add a task to the schedule. """
    try:
      # Parse and add task
      data = json.loads(data)
      self.add_task(data)

      await react(ctx, "confirm")
      await ctx.send(f"Added task of type {fmt_code(data['type'])} to the schedule.", delete_after=10)

    except (jsonschema.exceptions.ValidationError, json.decoder.JSONDecodeError) as exc:
      await react(ctx, "deny")
      if exc.__class__ == json.decoder.JSONDecodeError: msg = exc
      else:                                             msg = exc.message
      await ctx.send(f"JSON Error: {msg}")

  @schedule.command(aliases=["l"])
  async def list(self, ctx: commands.Context):
    """ List existing tasks. """
    await ctx.send(fmt_list(self._schedule.all()))

  # Do stuff every second
  @tasks.loop(seconds=1)
  async def tick(self):
    schedule.run_pending()

  @tick.before_loop
  async def before_tick(self):
    # Wait for on_ready before beginning
    await self.bot.wait_until_ready()

  def cog_unload(self):
    # Cancel task when unloading the cog
    self.tick.cancel()
