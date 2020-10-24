import json
import datetime
import re

import jsonschema
from discord import AllowedMentions
from discord.ext import commands, tasks
import delta

from lib.utils import Cog, in_guild, react, md_list_item, md_code, readable_delta, TIME_FORMAT

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

#TODO moderator tools for dealing with reminders?

class Reminder(Cog):
  def __init__(self, bot: commands.Bot):
    super().__init__()
    self.bot = bot
    self._reminders = bot._db.table("reminders")
    self._reminder_schema = json.load(open("./lib/schema/reminder.json"))

    self.tick.start()

  # Guild-only
  async def cog_check(self, ctx: commands.Context):
    return in_guild(ctx)

  # Reminders
  @commands.group(aliases=["rem"], invoke_without_command=True)
  async def reminder(self, ctx: commands.Context, *, reminder: str):
    """ Set a reminder, ie ",rem 2 hours: Wake up!" """
    # if ctx.invoked_subcommand is not None:
    match = re.match("\A([^:\n]+):(.+)\Z", reminder, re.S)
    if match:
      try:
        when = datetime.datetime.now() + delta.parse(match[1])
      except Exception as exc:
        await react(ctx, "deny")
        await ctx.send(f"Error: {exc}", delete_after=10)
        return

      msg = match[2].strip()
      #TODO make sure this matches properly and add error handling
      # ./lib/schema/reminder.json
      new_reminder = {
        "datetime": when.strftime(TIME_FORMAT),
        "channel": ctx.message.channel.id,
        "message": msg,
        "meta": {
          "message": ctx.message.id,
          "member": ctx.message.author.id,
          "datetime": ctx.message.created_at.strftime(TIME_FORMAT)
        }
      }

      try:
        # Validation step just in case
        jsonschema.validate(instance=new_reminder, schema=self._reminder_schema)
        # Add to table
        self._reminders.insert(new_reminder)
        # UI feedback
        await react(ctx, "confirm")
      # Error handling
      except (jsonschema.exceptions.ValidationError, json.decoder.JSONDecodeError) as exc:
        await react(ctx, "deny")
        if exc.__class__ == json.decoder.JSONDecodeError: msg = exc
        else:                                             msg = exc.message
        await ctx.send(f"JSON Error: {msg}")
    else:
      await react(ctx, "deny")
      await ctx.send("Unsupported syntax. Use `,rem <duration>:<message>`", delete_after=10)

  @reminder.command(aliases=["l"])
  async def list(self, ctx: commands.Context):
    """ See all your reminders. """
    out = ""
    now = datetime.datetime.now()
    your_reminders = sorted(
      filter(lambda reminder: reminder["meta"]["member"] == ctx.author.id, self._reminders.all()),
      key=lambda reminder: - (now - datetime.datetime.strptime(reminder["datetime"], TIME_FORMAT))
    )

    if len(your_reminders) == 0:
      await ctx.send("You don't have any reminders set.")
    else:
      for reminder in your_reminders:
        then = datetime.datetime.strptime(reminder["datetime"], TIME_FORMAT)

        # Only first line, 60 chars max
        _lines = reminder["message"].split("\n")
        msg = _lines[0]
        if len(msg) > 60:
          msg = msg[:60] + " (…)"
        elif len(_lines) > 1:
          msg += " (…)"

        out += md_list_item(
          f"{md_code(str(reminder.doc_id).rjust(3))} - " +
          f"{md_code(reminder['datetime'])}, " +
          f"{readable_delta(now - then)}:\n" +
          f"    {msg}"
        )

      await ctx.send(out, allowed_mentions=AllowedMentions.none())

  @reminder.command(aliases=["r"])
  async def remove(self, ctx: commands.Context, reminder_id: int):
    """ Forget one of your reminders. Check the id using ,rem list first. """
    reminder = self._reminders.get(doc_id=reminder_id)
    if reminder is None:
      if reminder["meta"]["member"] == ctx.author.id:
        self._reminders.remove(doc_ids=[reminder_id])
        await react(ctx, "confirm")
      else:
        await react(ctx, "deny")
        await ctx.send("That's not your reminder.", delete_after=10)
    else:
      await react(ctx, "deny")
      await ctx.send("That's not a reminder.", delete_after=10)

  async def announce_reminder(self, reminder: dict):
    await self.bot._guild.get_channel(reminder["channel"]).send(
      f"Reminder for <@{reminder['meta']['member']}> " +
      f"({readable_delta(datetime.datetime.now() - datetime.datetime.strptime(reminder['meta']['datetime'], TIME_FORMAT))}):\n" +
      f"{reminder['message']}\n" +
      f"https://discord.com/channels/{self.bot._guild.id}/{reminder['channel']}/{reminder['meta']['message']}"
    )

  @tasks.loop(seconds=1)
  async def tick(self):
    # Check all reminders
    for reminder in self._reminders.all():
      # If they are pending
      if datetime.datetime.now() - datetime.datetime.strptime(reminder["datetime"], TIME_FORMAT) >= datetime.timedelta(0):
        # Announce them
        await self.announce_reminder(reminder)
        # And then remove them from the table
        self._reminders.remove(doc_ids=[reminder.doc_id])
