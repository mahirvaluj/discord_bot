import asyncio
import discord
import os
import sys

from discord.ext import commands
# Note, requires envvar BOT_TOKEN

bot = commands.Bot(command_prefix="::")

@commands.command()
async def ping(ctx):
    await ctx.send('pang')

async def monitor(ctx):
    await ctx.send('Starting monitoring on channel {}')

def main():
    if 'BOT_TOKEN' not in os.environ:
        print("Missing BOT_TOKEN environment variable.")
        sys.exit(1)

    bot.add_command(ping)
    bot.run(os.environ['BOT_TOKEN'])

if __name__ == "__main__":
    main()


