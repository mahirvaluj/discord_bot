#!/usr/bin/env python3

import asyncio
import discord
import os
import sys
import random

from datetime import datetime
from discord.ext import commands
# Note, requires envvar BOT_TOKEN

bot = commands.Bot(command_prefix="::")

@commands.command()
async def ping(ctx):
    await ctx.send('pang')
    
@command.command()
async def flip(ctx):
    options=['Heads','Tails']
    await ctx.send('You rolled ' + options[random.randint(0,1)])

@commands.command()
async def yank(ctx, *args):
    allowed = False
    for i in ctx.author.roles:
        if i.permissions.administrator:
            allowed = True
        
    if not allowed:
        await ctx.send("You're not allowed to use this command!")
        return

    if len(args) != 2:
        await ctx.send(\
            'Invalid number of arguments -- must specify mode and limit\n'\
            'Mode options are:\n\t`text->only capture msg text`\n'\
            '\t`full->capture author, timestamp, text`\n\n'
            'Limit options are: number or "none"\n'\
            'Note: none limit is stressing on the API. Do this sparingly.\n\n'\
            'example: `::yank text 123`\n\n'\
            'This will capture the text of the latest 123 messages in this channel.'
        )
        return

    if args[0] not in ("text", "full"):
        await ctx.send("Mode must be either `text`, or `full`")
        return
    else:
        mode = args[0].strip()

    if args[1].strip() == "none":
        msg_limit = None
        oldest_first = True
    elif args[1].strip().isdigit():
        msg_limit = int(args[1])
        oldest_first = False
    else:
        await ctx.send("Invalid limit")
        return 

    filepath = f"yanks/{datetime.now().strftime('%H-%M-%S')}-{args[0]}-{ctx.channel}"
    await ctx.send(f'Starting yanking channel {ctx.channel}\n' \
                   f'Outputting to `{filepath}`')

    with open(filepath, "w+") as wf:
        async for msg in ctx.history(limit=msg_limit, oldest_first=oldest_first):
            if mode == 'full':
                wf.write(f'{msg.author} - {msg.created_at.strftime("%d/%m/Y|%H:%M:%S")} - {repr(msg.content)}\n\n')
            elif mode == 'text':
                wf.write(f'{repr(msg.content)}\n\n')


def main():
    if 'BOT_TOKEN' not in os.environ:
        print("Missing BOT_TOKEN environment variable.")
        sys.exit(1)

    bot.add_command(ping)
    bot.add_command(yank)
    bot.add_command(flip)
    bot.run(os.environ['BOT_TOKEN'])

if __name__ == "__main__":
    main()
