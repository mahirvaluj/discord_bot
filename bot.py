#!/usr/bin/env python3

import asyncio
import discord
import os
import sys

#wordcloud dependancies
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt

from datetime import datetime
from discord.ext import commands

# Note, requires envvar BOT_TOKEN

bot = commands.Bot(command_prefix="::")

@command.event
async def on_message(message):
    message_content = message.content
    with open("log.txt", "a") as f:
       time_stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
       f.write(f"<{time_stamp}>{message_content}\n")
    await bot.process_commands(message)

@command.command()
async def wordcloud(ctx):
    print('{} - Command: wordcloud | Author: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),ctx.author))
    
    #read data from text file
    text = open('log.txt').read()
    #clean up
    if os.path.exists('word_cloud.png'):
        os.remove('word_cloud.png')
    #generate wordcloud
    wordcloud = WordCloud(max_font_size=50, max_words=500, background_color="white").generate(text)
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    #save wordcloud as an image
    wordcloud.to_file('word_cloud.png')
    #instantiate discord File object
    file = discord.File('word_cloud.png')
    #attach file to discord reply
    await ctx.channel.send(file=file)
    #clean up
    if os.path.exists('word_cloud.png'):
        os.remove('word_cloud.png')
        
    print('{} - Task Finished Succesfully'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

@commands.command()
async def ping(ctx):
    await ctx.send('pang')


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
    bot.run(os.environ['BOT_TOKEN'])

if __name__ == "__main__":
    main()
