#!/usr/bin/env python3

import asyncio
import discord
import insults
import random
import os
import sys

#wordcloud dependencies
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt

from datetime import datetime
from discord.ext import commands


# Note, requires envvar BOT_TOKEN

bot = commands.Bot(command_prefix="::")

# This stores the current nicknames used by force_nick
nickname_dir = {}


def is_admin(user):
    """
    Checks whether user is an administrator on the guild 
    """
    return user.guild_permissions.administrator

@bot.event
async def on_message(message):
    """
    Fill up 'log.txt' with messages as they are sent in channels with bot
    TODO: - Add separate log.txts for separate channels:w
          - Clear log files as they get too large
    """
    message_content = message.content
    with open("log.txt", "a") as f:
       time_stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
       f.write(f"<{time_stamp}>{message_content}\n")
    await bot.process_commands(message)


@commands.command()
async def eat_my_ass(ctx):
    """
    Insult user who calls this function
    """
    print('{} - Command: eat_my_ass | Author: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),ctx.author))
    await ctx.send(f"You fucking {insults.insults[random.randint(0, len(insults.insults) - 1)].lower()}, {ctx.author.mention}.")
    print('{} - Task Finished Succesfully'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))


@commands.command()
async def force_nick(ctx, *args):
    """
    Force nickname on user -- set nickname, and then periodically monitors 
    user for changes, and set back when it happens
    """
    print('{} - Command: force_nick | Author: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),ctx.author))

    if not is_admin(ctx.author):
        await ctx.send("You're not allowed to use this command!")
        print("Not allowed.")
        return

    if len(args) != 2:
        await ctx.send("Invalid number of args.\n\n"\
                       "Usage:\n\t`::force_nick user nick`")
        return

    if len(ctx.message.mentions) != 1:
        await ctx.send("Invalid mention.\n"\
                       "Usage:\n\t`::force_nick user nick`")
        return

    user = ctx.message.mentions[0]

    nickname_dir[user.id] = args[1]
    
    # Make a closure which will check the user's nick for us
    def mk_nick_check(user, nickname):
        async def nick_check():
            while user.id in nickname_dir:
                if user.nick != nickname:
                    await user.edit(nick=nickname)
                await asyncio.sleep(10)
        return nick_check

    chk = mk_nick_check(ctx.message.mentions[0], args[1])

    loop = asyncio.get_event_loop()

    loop.create_task(chk())
    print('{} - Task Finished Succesfully'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    

@commands.command()
async def reset_nick(ctx, *args):
    """
    Reset forced nickname on user
    """
    print('{} - Command: reset_nick | Author: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),ctx.author))
    if not is_admin(ctx.author):
        await ctx.send("You're not allowed to use this command!")
        print("Not allowed.")
        return
        
    if len(args) != 1:
        await ctx.send("Invalid # of arguments.\n"\
                       "Usage:\n\t`::reset_nick user`")
        return

    if len(ctx.message.mentions) != 1:
        await ctx.send("invalid mention.\n"\
                       "Usage:\n\t`::reset_nick user`")
        return

    del nickname_dir[ctx.message.mentions[0].id]
    await ctx.message.mentions[0].edit(nick=None)
    print('{} - Task Finished Succesfully'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))


@commands.command()
async def wordcloud(ctx):
    """
    create wordcloud from all words in log.txt
    TODO: - Individual wordclouds per channel
    """
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
    """
    Yank messsages from a certain channel and output them to a text file
    File will be in folder 'yanks'
    """
    print('{} - Command: yank | Author: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),ctx.author))

    if not is_admin(ctx.author):
        await ctx.send("You're not allowed to use this command!")
        print("Not allowed")
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

    if not os.path.isdir("./yanks"):
        os.mkdir("./yanks")

    with open(filepath, "w+") as wf:
        async for msg in ctx.history(limit=msg_limit, oldest_first=oldest_first):
            if mode == 'full':
                wf.write(f'{msg.author} - {msg.created_at.strftime("%d/%m/Y|%H:%M:%S")} - {repr(msg.content)}\n\n')
            elif mode == 'text':
                wf.write(f'{repr(msg.content)}\n\n')

    print('{} - Task Finished Succesfully'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))


def main():
    if 'BOT_TOKEN' not in os.environ:
        print("Missing BOT_TOKEN environment variable.")
        sys.exit(1)

    bot.add_command(ping)
    bot.add_command(yank)
    bot.add_command(wordcloud)
    bot.add_command(force_nick)
    bot.add_command(reset_nick)
    bot.add_command(eat_my_ass)
    bot.run(os.environ['BOT_TOKEN'])


if __name__ == "__main__":
    main()
