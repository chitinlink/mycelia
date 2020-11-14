import wavelink
import re
import subprocess
from typing import Union, List
from uuid import uuid4
from itertools import islice
from asyncio import Event, Queue
from math import ceil
from shlex import split

# import datetime
# import humanize

import discord
from discord.ext import commands

from lib.utils.etc import Service, time_hms
from lib.utils.checks import in_dms
from lib.utils.text import fmt_list, fmt_plur

LAVALINK_READY = re.compile(" lavalink.server.Launcher\s+: Started Launcher")
RURL = re.compile("https?:\/\/(?:www\.)?.+") #TODO double check this

# TODO md escape track titles etc

def fmt_tracklist(tracks: List[wavelink.Track], page = 1) -> str:
  lst = []
  for i, track in enumerate(tracks):
    _out = ""
    _out += f"`{str(i + ((page - 1) * 10) + 1).rjust(2)}`"
    if track.is_stream:
      _out += f" - `[STREAM]`"
    else:
      _out += f" - `[{time_hms(track.length/1000)}]`"
    _out += f" {track.title}"
    lst.append(_out)
  return fmt_list(lst)

class MusicController:
  def __init__(self, bot, guild_id):
    self.bot = bot
    self.guild_id = guild_id
    self.channel = None

    self.next = Event()
    self.queue = Queue()

    self.volume = 40

    self.bot.loop.create_task(self.controller_loop())

  async def controller_loop(self):
    await self.bot.wait_until_ready()

    player = self.bot._wavelink.get_player(self.guild_id)
    await player.set_volume(self.volume)

    while True:
      self.next.clear()

      track = await self.queue.get() # type: wavelink.player.Track
      await player.play(track)
      await self.channel.send(f"Now playing: {track.title}")
      await self.next.wait()

class Music(Service):
  def __init__(self, bot):
    super().__init__(bot)
    self.controllers = {}
    self.bot._wavelink = wavelink.Client(bot=self.bot)
    _path = self.bot._config["lavalink_path"]
    _args = self.bot._config["lavalink_args"]
    self._lavalink = subprocess.Popen(
      split(f"java -jar ./Lavalink.jar {_args}"),
      shell=False, cwd=self.bot._config["lavalink_path"],
      stdout=subprocess.PIPE, universal_newlines=True)
    self._searchresults = {}

    self.bot.add_listener(self.check_searchresults, "on_message")

    rc = 0
    while True:
      stdout = self._lavalink.stdout.readline()
      if stdout == "" and rc is not None:
        break
      if LAVALINK_READY.search(stdout):
        self.bot.loop.create_task(self.start_nodes())
        break
      rc = self._lavalink.poll()

  # Guilds only
  async def cog_check(self, ctx):
    return not in_dms(ctx)

  # Close Lavalink when unloading
  def cog_unload(self):
    self._lavalink.terminate()

  async def start_nodes(self):
    await self.bot.wait_until_ready()

    _id = uuid4()
    node = await self.bot._wavelink.initiate_node(
      host="127.0.0.1",
      port=2333,
      rest_uri="http://127.0.0.1:2333",
      password="efbca800-5806-4fbf-868e-71403b9f61c4",
      identifier=str(_id),
      region="eu_west"
    )
    self.log.info(f"Initiated Wavelink node with identifier {_id}.")

    # Set our node hook callback
    node.set_hook(self.on_event_hook)

  async def on_event_hook(self, event):
    if isinstance(event, (wavelink.TrackEnd, wavelink.TrackException)):
      controller = self.get_controller(event.player)
      controller.next.set()

  def get_controller(self, value: Union[commands.Context, wavelink.Player]):
    if isinstance(value, commands.Context): gid = value.guild.id
    else:                                   gid = value.guild_id

    try:
      controller = self.controllers[gid]
    except KeyError:
      controller = MusicController(self.bot, gid)
      self.controllers[gid] = controller

    return controller

  @commands.command(name="join", aliases=["connect"])
  async def join_voice(self, ctx):
    """ Make me join your voice channel. """
    try:
      channel = ctx.author.voice.channel
    except AttributeError:
      await ctx.send("Please join a channel first...", delete_after=10)
      raise discord.DiscordException()

    player = self.bot._wavelink.get_player(ctx.guild.id)
    await ctx.send(f"Joining __{channel.mention}__.", delete_after=10)
    await player.connect(channel.id)

    controller = self.get_controller(ctx)
    controller.channel = ctx.channel

  @commands.command(aliases=["p"])
  async def play(self, ctx, *, query: str):
    """ Play something. """

    player = self.bot._wavelink.get_player(ctx.guild.id)
    if not player.is_connected:
      try: await ctx.invoke(self.join_voice)
      except discord.DiscordException: return #FIXME probably use a diff exception here instead

    if RURL.match(query):
      tracks = await self.bot._wavelink.get_tracks(f"{query}")
      if isinstance(tracks, wavelink.TrackPlaylist):
        for t in tracks.tracks: await self.queue_track(ctx, t, nomessage=True)
        await ctx.send(f"Added `{len(tracks.tracks)}` tracks to the queue.")
        # FIXME says 100 tracks for some reason
      else:
        await self.queue_track(ctx, tracks[0])
    else:
      if not (tracks := (await self.bot._wavelink.get_tracks(f"ytsearch:{query}"))[:10]):
        return await ctx.send("Couldn't find anything.", delete_after=10)
      else:
        list_msg = await ctx.send(
          f"Results for \"{query}\":\n{fmt_tracklist(tracks)}"
        )
        self._searchresults[ctx.author.id] = {
          "tracks": tracks,
          "datetime": ctx.message.created_at, # NOTE unused atm
          "list_msg": list_msg
        }
        return

  async def queue_track(self, ctx, track: wavelink.player.Track, *, nomessage = False):
    controller = self.get_controller(ctx)
    controller.queue.put_nowait(track)
    if not nomessage:
      await ctx.send(f"Added to the queue: {track.title}")

  async def check_searchresults(self, message: discord.Message):
    mid = message.author.id
    if not mid in self._searchresults.keys(): return
    match = re.match(fr"^{self.bot.command_prefix}?(10|[1-9])$", message.content)
    if not match: return
    track = self._searchresults[mid]["tracks"][int(match[1]) - 1]
    await self._searchresults[mid]["list_msg"].delete()
    del self._searchresults[mid]
    await self.queue_track(await self.bot.get_context(message), track)

  @commands.command(aliases=["q", "list"])
  async def queue(self, ctx, *, pagenum: int = 1):
    """ List queued tracks. """
    if pagenum < 1: return

    player = self.bot._wavelink.get_player(ctx.guild.id) # type: wavelink.player.Player
    controller = self.get_controller(ctx)

    if not player.current and not controller.queue._queue:
      return await ctx.send("There's nothing in the queue...", delete_after=10)

    qsize = controller.queue.qsize()
    numpages = ceil(qsize / 10)

    if pagenum > numpages:
      return await ctx.send(f"There's only {numpages} page{fmt_plur(numpages)} of tracks in the queue.", delete_after=10)

    tracks = list(islice(controller.queue._queue, (pagenum - 1) * 10, (pagenum - 1) * 10 + 10))

    _c = player.current
    _p = player.position
    time_remaining = time_hms(((_c.duration - _p) +
      sum(map(lambda t: t.duration,
        filter(lambda t: not t.is_stream, controller.queue._queue))
      )
    ) / 1000)

    _out = ""
    _out += f"Currently playing: "
    if not _c.is_stream:
      _out += f"`[{time_hms(_p / 1000)}/{time_hms(_c.length / 1000)}]`"
    else:
      _out += f"`[STREAM]`"
    _out += f" {_c.title}\n"
    if controller.queue._queue:
      if numpages > 1:
        _out += f"Page `{pagenum}/{numpages}` "
      _out += f"(`{qsize}` item{fmt_plur(qsize)}, `[{time_remaining}]` remaining)\n"
      _out += fmt_tracklist(tracks, page=pagenum)
    await ctx.send(_out)

  @commands.command(aliases=["np", "what"])
  async def nowplaying(self, ctx): #TODO
    """ Get info for the current track. """
    player = self.bot._wavelink.get_player(ctx.guild.id)

    if not player.current:
      return await ctx.send("I'm not playing anything...", delete_after=10)

    _c = player.current
    _p = player.position

    _out = ""
    _out += f"Currently playing: "
    if not _c.is_stream:
      _out += f"`[{time_hms(_p / 1000)}/{time_hms(_c.length / 1000)}]`"

    await ctx.send(_out)

  @commands.command(aliases=["s", "next"])
  async def skip(self, ctx, *, number: int = 1): # TODO a-b skip specific tracks
    """ Skip the current track. """
    if number < 1: return

    player = self.bot._wavelink.get_player(ctx.guild.id)

    if not player.is_playing:
      return await ctx.send("I'm not playing anything...", delete_after=10)

    msg = "Skipping"
    if number > 1: msg += f" {number} tracks"
    await ctx.send(msg + ".", delete_after=10)
    if number > 1:
      controller = self.get_controller(ctx)
      for _ in range(number - 1): controller.queue.get_nowait()
    await player.stop()

  @commands.command(aliases=["unresume"])
  async def pause(self, ctx):
    """ Pause the player. """
    player = self.bot._wavelink.get_player(ctx.guild.id) # type: wavelink.Player
    if not player.is_playing or player.is_paused:
      return await ctx.send("I'm not playing anything...", delete_after=10)

    await ctx.send("Pausing.", delete_after=10)
    await player.set_pause(True)

  @commands.command(aliases=["unpause", "continue"])
  async def resume(self, ctx):
    """ Resume the player from a paused state. """
    player = self.bot._wavelink.get_player(ctx.guild.id)
    if not player.is_paused:
      return await ctx.send("I'm not paused...", delete_after=10)

    await ctx.send("Resuming.", delete_after=10)
    await player.set_pause(False)

  @commands.command()
  async def volume(self, ctx, *, vol: int):
    """ Set the volume. """
    player = self.bot._wavelink.get_player(ctx.guild.id)
    controller = self.get_controller(ctx)

    vol = max(min(vol, 1000), 0)
    controller.volume = vol

    await ctx.send(f"Volume is now `{vol}`.")
    await player.set_volume(vol)

  @commands.command(aliases=["disconnect", "dc", "stop", "kill", "die", "fuckoff"])
  async def destroy(self, ctx):
    """ Reset and disconnect. """
    player = self.bot._wavelink.get_player(ctx.guild.id)

    try: del self.controllers[ctx.guild.id]
    except KeyError: return await player.disconnect()

    await player.disconnect()
    await ctx.send("Ok, bye!", delete_after=10)

  # @commands.command()
  # async def info(self, ctx):
  #   """ Retrieve various Node/Server/Player information. """
  #   player = self.bot._wavelink.get_player(ctx.guild.id)
  #   node = player.node # type: wavelink.Node

  #   used  = humanize.naturalsize(node.stats.memory_used)
  #   total = humanize.naturalsize(node.stats.memory_allocated)
  #   free  = humanize.naturalsize(node.stats.memory_free)
  #   cpu   = node.stats.cpu_cores

  #   fmt = f"**WaveLink:** `{wavelink.__version__}`\n\n" \
  #     f"Connected to `{len(self.bot._wavelink.nodes)}` nodes.\n" \
  #     f"Best available Node `{self.bot._wavelink.get_best_node().__repr__()}`\n" \
  #     f"`{len(self.bot._wavelink.players)}` players are distributed on nodes.\n" \
  #     f"`{node.stats.players}` players are distributed on server.\n" \
  #     f"`{node.stats.playing_players}` players are playing on server.\n\n" \
  #     f"Server Memory: `{used}/{total}` | `({free} free)`\n" \
  #     f"Server CPU: `{cpu}`\n\n" \
  #     f"Server Uptime: `{datetime.timedelta(milliseconds=node.stats.uptime)}`"
  #   await ctx.send(fmt)
