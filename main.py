import os
import discord
import requests

from discord.ext import commands

from cast_utils import get_info, get_links, rcol, ses
from keep_alive import keep_alive

# Tracks the currently playing episode
CURRENT = None

# Bot Setup
bot = commands.Bot(command_prefix="?", help_command=None)


@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready to jam now.")


# Handling wrong commands & missing permissions
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send(
            "_I do not understand that command! Try `?help` to get a list of commands._",
            delete_after=120)

    if isinstance(error, commands.MissingPermissions):
        await ctx.send("`You are not an admin!`", delete_after=120)


@bot.command(name="announce", aliases=['a', '<'])
@commands.has_role("admin")
async def announce_(ctx):
    """
    Announces the release of a new podcast

    """
    await ctx.trigger_typing()

    if get_info():
        pod_num, pod_title, pod_published, pod_shortdesc = get_info()

        # Preparing embed
        file = discord.File("./castbot.png")
        promo_url = rf"https://gitlab.com/nisercast/nisercast.gitlab.io/-/raw/master/assets/episodes/posters/{str(pod_num - 1).zfill(3)}.png"
        embed = discord.Embed(
            title=pod_title,
            description=
            f"_Publication Timestamp: {pod_published}_\n\n{pod_shortdesc}\n\n\u200b",
            colour=discord.Color.from_rgb(*rcol()))

        links = get_links()
        links_final = [
            f"[Google Podcast]({links[0]})\n",
            f"[Spotify Podcast]({links[1]})\n",
            f"[Apple Podcast]({links[2]})\n\n",
            "_You can also listen to episodes via this bot. Type `?help` to learn more._"
        ]

        embed.set_image(url=promo_url)

        embed.add_field(name="Podcast Links:",
                        value=f"{''.join(x for x in links_final)}",
                        inline=False)
        embed.add_field(name="\u200b", value="\u200b", inline=False)

        embed.set_footer(
            text=
            "Custom Podcast Bot for NiSERCast Discord Server | Fork me on GitHub (https://github.com/sdgniser/castbot)",
            icon_url="attachment://castbot.png")

        await ctx.channel.send(content="@everyone", file=file, embed=embed)
        await ctx.message.delete()

    else:
        return await ctx.channel.send("`Podcast not found!`", delete_after=120)


@bot.command(name="play", aliases=['p'])
async def play_(ctx, *, podcast=1):
    """
    Plays the requested NiSERCast episode, sourced from GitLab

    podcast: int
        Episode number
        Defaults to ``1`` (Episode 1)

    """
    global CURRENT

    # Discord limiation: cannot typecheck here
    if podcast == CURRENT:
        return await ctx.send(
            f"`Episode {podcast} is already being played! Try ?r to resume an episode.`",
            delete_after=60)

    source = rf"https://gitlab.com/nisercast/nisercast.gitlab.io/-/raw/master/assets/episodes/{str(podcast).zfill(3)}.mp3"

    await ctx.trigger_typing()

    # Checking, if file exists on GitLab
    resp = ses.get(source).status_code

    if resp != 200:
        return await ctx.send(
            f"`Episode {podcast} either does not exist or GitLab is experiencing issues at this time!`",
            delete_after=120)

    author = ctx.author

    if hasattr(author, "voice") and author.voice and author.voice.channel:
        voice_channel = author.voice.channel
        voice = ctx.channel.guild.voice_client

        # Player loop to skip / change episode
        if voice:
            await voice.disconnect()

        voice = await voice_channel.connect()
        voice.play(discord.FFmpegPCMAudio(source=source))
        voice.is_playing()
        CURRENT = podcast
        await ctx.send(
            f"`Now playing NiSERCast Episode {podcast} requested by {author}`")

    else:
        await ctx.channel.send(
            content=
            "_You are not connected to a voice channel. Please join a voice channel before invoking this command._"
        )


@bot.command(name="pause", aliases=['//', 'pp'])
async def pause_(ctx):
    """
    Pauses the currently playing episode
    
    """
    vc = ctx.voice_client

    if not vc or not vc.is_playing():
        return await ctx.send('_I am currently not playing anything!_',
                              delete_after=60)

    elif vc.is_paused():
        return

    vc.pause()
    await ctx.send(f'**`{ctx.author}`**: Paused the episode!')


@bot.command(name="resume", aliases=['r'])
async def resume_(ctx):
    """
    Resumes the currently paused episode
    
    """
    vc = ctx.voice_client

    if not vc or not vc.is_connected():
        return await ctx.send('_I am currently not playing anything!_',
                              delete_after=60)

    elif not vc.is_paused():
        return

    vc.resume()
    await ctx.send(f'**`{ctx.author}`**: Resumed the episode!')


@bot.command(name="stop", aliases=['s', 'dc'])
async def stop_(ctx):
    """
    Stops the currently playing episode and destroys the player

    """
    vc = ctx.voice_client

    if not vc or not vc.is_connected():
        return await ctx.send("_I am currently not playing anything!_",
                              delete_after=60)

    try:
        await vc.disconnect()
    except AttributeError:
        pass


@bot.command(name="info", aliases=['i', 'np'])
async def info_(ctx):
    """
    Displays information about the currently playing episode

    """
    global CURRENT

    if CURRENT is not None:
        pod_num, pod_title, pod_published, pod_shortdesc = get_info(CURRENT)

        # Preparing embed
        file = discord.File("./castbot.png")
        embed = discord.Embed(
            title=pod_title,
            description=
            f"_Publication Timestamp: {pod_published}_\n\n{pod_shortdesc}",
            colour=discord.Colour.gold(),
        )

        embed.add_field(name="\u200b", value="\u200b", inline=False)

        embed.set_footer(
            text=
            "Custom Podcast Bot for NiSERCast Discord Server | Fork me on GitHub (https://github.com/sdgniser/castbot)",
            icon_url="attachment://castbot.png")

        await ctx.channel.send(content=None, file=file, embed=embed)

    else:
        await ctx.channel.send("_I am currently not playing anything!_",
                               delete_after=60)


@bot.command(name="help", help="Shows help message and list of commands")
async def help_(ctx):
    """
    Shows help message and list of commands

    """
    file = discord.File("./castbot.png")
    embed = discord.Embed(
        title="List of commands for CastBot",
        description=
        "CastBot announces new NiSERCast episodes and allows server members to play episodes within this server.\n\n**Bot Pefix**: `?`\n\n**List of Commands:**",
        colour=discord.Colour.teal(),
    )

    embed.add_field(
        name="`?announce`",
        value=
        "[**Admin only**] Puts a new episode announcement message in the current channel.",
        inline=True)
    embed.add_field(name="aliases", value="`?a`, `?<`", inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)
    embed.add_field(
        name="`?play <episode number>`",
        value=
        "Searches GitLab for the requested episode and plays it. Plays Ep. 1 by default. Join a voice channel before invoking this command.",
        inline=True)
    embed.add_field(name="aliases", value="`?p`", inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)
    embed.add_field(name="`?pause`",
                    value="Pauses the currently playing episode.",
                    inline=True)
    embed.add_field(name="aliases", value="`?pp`, `?//`", inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)
    embed.add_field(name="`?resume`",
                    value="Resumes the currently paused episode.",
                    inline=True)
    embed.add_field(name="aliases", value="`?r`", inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)
    embed.add_field(
        name="`?stop`",
        value=
        "Stops the currently playing episode and leaves the voice channel.",
        inline=True)
    embed.add_field(name="aliases", value="`?s`, `?dc`", inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)
    embed.add_field(
        name="`?info`",
        value="Displays information about the currently playing episode.",
        inline=True)
    embed.add_field(name="aliases", value="`?i`, `?np`", inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=False)

    embed.set_footer(
        text=
        "Custom Podcast Bot for NiSERCast Discord Server | Fork me on GitHub (https://github.com/sdgniser/castbot)",
        icon_url="attachment://castbot.png")

    await ctx.channel.send(content=None, file=file, embed=embed)


# Start-up and keep-alive
TOKEN = os.getenv("TOKEN")

keep_alive()
bot.run(TOKEN)
