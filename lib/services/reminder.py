import json
import datetime
import re

import jsonschema
from discord import AllowedMentions, Member
from discord.ext import commands, tasks
import dateparser

from lib.utils.etc import Service, react, readable_delta, TIME_FORMAT
from lib.utils.checks import is_mod, in_guild
from lib.utils.text import fmt_list_item, fmt_code

dateparser_settings = {
  "TIMEZONE": "Etc/UTC",
  "DATE_ORDER": "YMD",
  "PREFER_DATES_FROM": "future",
  "PREFER_DAY_OF_MONTH": "current",
}

def remsort(now: datetime):
  def _remsort(reminder):
    return - (now - datetime.datetime.strptime(reminder["datetime"], TIME_FORMAT))
  return _remsort

def remshort(reminder: dict):
  _lines = reminder["message"].split("\n")
  msg = _lines[0]
  if   len(msg) > 60:   return msg[:60] + " (…)"
  elif len(_lines) > 1: return msg + " (…)"
  return msg

class Reminder(Service):
  def __init__(self, bot: commands.Bot):
    super().__init__(bot)
    self._reminders = bot._db.table("reminders")
    self._reminder_schema = json.load(open("./lib/schema/reminder.json"))

    self.tick.start()

  # Guild-only
  async def cog_check(self, ctx: commands.Context):
    return in_guild(ctx)

  # Reminders
  @commands.group(aliases=["grem"], invoke_without_command=True)
  async def reminder(self, ctx: commands.Context, *, reminder: str):
    """ Set a reminder, ie ",rem in 2 hours: Wake up!" """
    match = re.match("\A([^:\n]+):\s?(.+)\Z", reminder, re.S)
    if match:
      try:
        when = dateparser.parse(match[1])

        # Issue in parsing
        if when is None:
          await react(ctx, "deny")
          return await ctx.reply("Sorry, but I couldn't parse that.", delete_after=10, mention_author=False)

        duration = when - datetime.datetime.utcnow()

        # Past date
        if duration <= datetime.timedelta(0):
          await react(ctx, "deny")
          return await ctx.reply("I can't go back in time.", delete_after=10, mention_author=False)

        # Date exceeding 5 years
        if duration > datetime.timedelta(days = 365.25 * 5):
          await react(ctx, "deny")
          return await ctx.reply("That's way too long.", delete_after=10, mention_author=False)

      except Exception as exc:
        await react(ctx, "deny")
        await ctx.reply(f"Error: {exc}", delete_after=10, mention_author=False)
        return

      msg = match[2].strip()
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

  	  # FIXME There is a timezone-related issue... SOMEWHERE in this file.
      # All reminders are one hour sooner than they should be.
      self.log.debug(f"Now:  {datetime.datetime.utcnow().strftime(TIME_FORMAT)}")
      self.log.debug(f"Then: {new_reminder['datetime']}")
      self.log.debug(f"Diff: {datetime.datetime.strptime(new_reminder['datetime'], TIME_FORMAT) - datetime.datetime.utcnow()}")
      self.log.debug(f"Pending? {datetime.datetime.strptime(new_reminder['datetime'], TIME_FORMAT) - datetime.datetime.utcnow() <= datetime.timedelta(0)}")

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
        await ctx.reply(f"JSON Error: {msg}", mention_author=False)
    else:
      await react(ctx, "deny")
      await ctx.reply("Unsupported syntax. Use `,rem <when>:<message>`", delete_after=10, mention_author=False)

  @reminder.command(aliases=["l"])
  async def list(self, ctx: commands.Context):
    """ See all your reminders. """
    out = ""
    your_reminders = sorted(
      filter(
        lambda reminder: reminder["meta"]["member"] == ctx.author.id,
        self._reminders.all()
      ),
      key=remsort(datetime.datetime.utcnow())
    )

    if len(your_reminders) == 0:
      await ctx.reply("You don't have any reminders set.", mention_author=False)
    else:
      for reminder in your_reminders:
        then = datetime.datetime.strptime(reminder["datetime"], TIME_FORMAT)
        msg = remshort(reminder)

        out += fmt_list_item(
          f"{fmt_code(str(reminder.doc_id).rjust(3))} - " +
          f"{fmt_code(reminder['datetime'])}, " +
          f"{readable_delta(datetime.datetime.utcnow() - then)}:\n" +
          f"    {msg}"
        )

      await ctx.reply(out, allowed_mentions=AllowedMentions.none(), mention_author=False)

  @reminder.command(aliases=["la"])
  @commands.check(is_mod)
  async def listall(self, ctx: commands.Context):
    """ (Restricted to moderators) List all reminders. """

    if len(self._reminders.all()) == 0:
      await ctx.reply("There are no reminders.", delete_after=10, mention_author=False)
      return

    out = ""
    for reminder in sorted(self._reminders.all(), key=remsort(datetime.datetime.utcnow())):
      then = datetime.datetime.strptime(reminder["datetime"], TIME_FORMAT)
      msg = remshort(reminder)

      out += fmt_list_item(
        f"{fmt_code(str(reminder.doc_id).rjust(3))} - " +
        f"{fmt_code(reminder['datetime'])}, " +
        f"{readable_delta(datetime.datetime.utcnow() - then)} " +
        f"(<@{reminder['meta']['member']}>):\n"
        f"    {msg}"
      )

    await ctx.reply(out, allowed_mentions=AllowedMentions.none(), mention_author=False)

  @reminder.command()
  @commands.check(is_mod)
  async def purge(self, ctx: commands.Context, user: Member):
    """ (Restricted to moderators) Purge all of a user's reminders. """
    rems = list(map(
      lambda r: r.doc_id,
      filter(
        lambda r: r["meta"]["member"] == user.id,
        self._reminders.all()
      )
    ))
    self._reminders.remove(doc_ids=rems)
    await react(ctx, "confirm")
    await ctx.reply(f"Purged {len(rems)} reminders.", delete_after=10, mention_author=False)

  @reminder.command()
  @commands.check(is_mod)
  async def delete(self, ctx: commands.Context, reminder_id: int):
    """ (Restricted to moderators) Delete any reminder. """
    reminder = self._reminders.get(doc_id=reminder_id)
    if reminder is not None:
      self._reminders.remove(doc_ids=[reminder_id])
      await react(ctx, "confirm")
    else:
      await react(ctx, "deny")
      await ctx.reply("That's not a reminder.", delete_after=10, mention_author=False)

  @reminder.command(aliases=["r"])
  async def remove(self, ctx: commands.Context, reminder_id: int):
    """ Forget one of your reminders. Check the id using ,rem list first. """
    reminder = self._reminders.get(doc_id=reminder_id)
    if reminder is not None:
      if reminder["meta"]["member"] == ctx.author.id:
        self._reminders.remove(doc_ids=[reminder_id])
        await react(ctx, "confirm")
      else:
        await react(ctx, "deny")
        await ctx.reply("That's not your reminder.", delete_after=10, mention_author=False)
    else:
      await react(ctx, "deny")
      await ctx.reply("That's not a reminder.", delete_after=10, mention_author=False)

  async def announce_reminder(self, reminder: dict):
    await self.bot._guild.get_channel(reminder["channel"]).send(
      f"Reminder for <@{reminder['meta']['member']}> " +
      f"({readable_delta(datetime.datetime.utcnow() - datetime.datetime.strptime(reminder['meta']['datetime'], TIME_FORMAT))}):\n" +
      f"{reminder['message']}\n" +
      f"https://discord.com/channels/{self.bot._guild.id}/{reminder['channel']}/{reminder['meta']['message']}"
    )

  @tasks.loop(seconds=1)
  async def tick(self):
    # Check all reminders
    for reminder in self._reminders.all():
      # If they are pending
      if datetime.datetime.strptime(reminder["datetime"], TIME_FORMAT) - datetime.datetime.utcnow() <= datetime.timedelta(0):
        # Announce them
        await self.announce_reminder(reminder)
        # And then remove them from the table
        self._reminders.remove(doc_ids=[reminder.doc_id])
