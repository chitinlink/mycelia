from discord.ext import commands

def funnel(bot, message):
  # Ignore if the bot isn't ready
  if bot.is_ready():
    # Ignore unless it's in the correct server (which implies also not a DM)
    if message.guild == bot._guild:
      # Ignore unless:
      if (
        # It's not from a bot (incl. Biggs)
        not message.author.bot and
        # and it's not in an ignored channel
        message.channel not in bot._ignored_channels
      ): return True
  return False

class Funnel(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  # Pass all commands through the funnel
  async def bot_check(self, ctx) -> bool:
    return funnel(self.bot, ctx.message)
