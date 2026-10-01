import os
import base64
import re
from urllib.parse import urlparse, parse_qs

import discord
from discord.ext import commands
from discord import app_commands

from myserver import server_on


bot = commands.Bot(
    command_prefix='!',
    intents=discord.Intents.all()
)


# =========================================================
# Base64 Functions
# =========================================================

def is_base64(value: str) -> bool:
    if not value:
        return False

    # ตรวจรูปแบบ Base64
    if not re.fullmatch(r'[A-Za-z0-9+/]*={0,2}', value):
        return False

    try:
        decoded = base64.b64decode(value, validate=True)
        return base64.b64encode(decoded).decode() == value
    except Exception:
        return False


def decode_base64(value: str):
    if not is_base64(value):
        return None

    try:
        return base64.b64decode(value).decode('utf-8')
    except Exception:
        return None


def get_r_from_url(url: str):
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        return params.get('r', [None])[0]

    except Exception:
        return None


# =========================================================
# Bot Event
# =========================================================

@bot.event
async def on_ready():
    print("Bot Online!")
    print("555")

    synced = await bot.tree.sync()

    print(f"{len(synced)} command(s)")


# =========================================================
# Member Join / Leave
# =========================================================

@bot.event
async def on_member_join(member):

    channel = bot.get_channel(1140633489520205934)

    text = f"Welcome to the server, {member.mention}!"

    embed = discord.Embed(
        title='Welcome to the server!',
        description=text,
        color=0x66FFFF
    )

    await channel.send(text)
    await channel.send(embed=embed)
    await member.send(text)


@bot.event
async def on_member_remove(member):

    channel = bot.get_channel(1140633489520205934)

    text = f"{member.name} has left the server!"

    await channel.send(text)


# =========================================================
# Chatbot
# =========================================================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    mes = message.content

    if mes == 'hello':
        await message.channel.send("Hello It's me")

    elif mes == 'hi bot':
        await message.channel.send(
            "Hello, " + str(message.author.name)
        )

    await bot.process_commands(message)


# =========================================================
# Normal Commands
# =========================================================

@bot.command()
async def hello(ctx):
    await ctx.send(f"hello {ctx.author.name}!")


@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)


# =========================================================
# Slash Commands
# =========================================================

@bot.tree.command(
    name='hellobot',
    description='Replies with Hello'
)
async def hellocommand(interaction):
    await interaction.response.send_message(
        "Hello It's me BOT DISCORD"
    )


@bot.tree.command(name='name')
@app_commands.describe(name="What's your name?")
async def namecommand(interaction, name: str):

    await interaction.response.send_message(
        f"Hello {name}"
    )


# =========================================================
# /bypass
# =========================================================

@bot.tree.command(
    name='bypass',
    description='ตรวจสอบและถอดค่า r จาก URL'
)
@app_commands.describe(
    url='ใส่ URL ที่มีพารามิเตอร์ r'
)
async def bypasscommand(interaction, url: str):

    # ดึง r จาก URL
    r = get_r_from_url(url)

    if not r:

        embed = discord.Embed(
            title='❌ ไม่พบค่า r',
            description='URL ที่ส่งมาไม่มีพารามิเตอร์ `r`',
            color=0xFF0000
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

        return

    # ตรวจ Base64
    if not is_base64(r):

        embed = discord.Embed(
            title='❌ ค่า r ไม่ถูกต้อง',
            description='ค่า `r` ไม่ใช่ Base64 ที่ถูกต้อง',
            color=0xFF0000
        )

        embed.add_field(
            name='r',
            value=f'```{r[:1000]}```',
            inline=False
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

        return

    # Decode
    decoded_url = decode_base64(r)

    if not decoded_url:

        await interaction.response.send_message(
            '❌ ไม่สามารถถอดรหัสค่า r ได้',
            ephemeral=True
        )

        return

    # แสดงผล
    embed = discord.Embed(
        title='🔎 Base64 Decoder',
        color=0x5865F2
    )

    embed.add_field(
        name='ค่า r',
        value=f'```{r[:1000]}```',
        inline=False
    )

    embed.add_field(
        name='URL ที่ถอดออกมา',
        value=f'```{decoded_url[:1000]}```',
        inline=False
    )

    embed.set_footer(
        text='Base64 URL Decoder'
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# Help
# =========================================================

@bot.tree.command(
    name='help',
    description='Bot Commands'
)
async def helpcommand(interaction):

    embed = discord.Embed(
        title='Help Me! - Bot Commands',
        description='Bot Commands',
        color=0x66FFFF,
        timestamp=discord.utils.utcnow()
    )

    embed.add_field(
        name='/hellobot',
        value='Hello Command',
        inline=True
    )

    embed.add_field(
        name='/name',
        value='แสดงชื่อ',
        inline=True
    )

    embed.add_field(
        name='/bypass',
        value='ตรวจสอบและถอดค่า r จาก URL',
        inline=False
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# Start Bot
# =========================================================

server_on()

bot.run(os.getenv('TOKEN'))
