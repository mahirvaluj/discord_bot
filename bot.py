#!/usr/bin/env python3

import asyncio
import discord
import random
import os
import sys
import re

#google image search dependancy
from google_images_download import google_images_download

#wordcloud dependencies
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt

from datetime import datetime
from discord.ext import commands


# Note, requires envvar BOT_TOKEN

bot = commands.Bot(command_prefix="::")


# This stores the current nicknames used by force_nick
nickname_dir = {}
muted_l = []


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
    global muted_l

    message_content = message.content
    for i in muted_l:
        if re.match(i[0], message_content):
            await message.delete()
    with open("log.txt", "a") as f:
       time_stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
       f.write(f"<{time_stamp}>{message_content}\n")
    await bot.process_commands(message)


@commands.command()
async def unmute_all(ctx):
    """
    removes all values from mute list
    """
    print('{} - Command: unmute_all | Author: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),ctx.author))

    if not is_admin(ctx.author):
        await ctx.send("You're not allowed to use this command!")
        print("Not allowed.")
        return

    global muted_l
    muted_l = []

    print('{} - Task Finished Succesfully'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))


@commands.command()
async def mute_where(ctx, text):
    """
    adds text to "muted_l"
    text in muted_l will be deleted when sent. 
    """
    print('{} - Command: mute_where | Author: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),ctx.author))
    global muted_l

    if not is_admin(ctx.author):
        await ctx.send("You're not allowed to use this command!")
        print("Not allowed.")
        return

    try:
        muted_re = re.compile(text, re.I)
        muted_l.append((muted_re, text))
    except:
        await ctx.send(f"```{text}``` is not valid regex.")
        print("Invalid regex")
        return

    print('{} - Task Finished Succesfully'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))


@commands.command()
async def unmute_where(ctx, text):
    """
    removes text to "muted_l"
    text in muted_l will be deleted when sent. 
    """
    print('{} - Command: unmute_where | Author: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),ctx.author))
    global muted_l

    if not is_admin(ctx.author):
        await ctx.send("You're not allowed to use this command!")
        print("Not allowed.")
        return

    for i, t in enumerate(muted_l):
        if t[1] == text:
            muted_l = muted_l[:i] + muted_l[i+1:]

    print('{} - Task Finished Succesfully'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    

@commands.command()
async def mute_status(ctx):
    """
    sends status of muted text
    NOTE: THIS IS BUSTED ATM
    """
    print('{} - Command: mute_status | Author: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),ctx.author))
    global muted_l

    if not is_admin(ctx.author):
        await ctx.send("You're not allowed to use this command!")
        print("Not allowed.")
        return

    await ctx.send(repr(muted_l))

    print('{} - Task Finished Succesfully'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))


@commands.command()
async def google(ctx, *, keywords:str):
    """
    Finds a random google image with a given keyword
    """
    print('{} - Command: google | Author: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),ctx.author))
    response = google_images_download.googleimagesdownload()   #class instantiation

    arguments = {"keywords":keywords,"limit":5,"print_urls":False, "format":"jpg", "safe_search":True}   #creating list of arguments
    paths = response.download(arguments)   #passing the arguments to the function
    my_files = [
    discord.File(paths[0][keywords][random.randint(0,4)]),
    ]

    await ctx.send(files=my_files)
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
async def emojify(ctx, *, content:str):
   """
   Emojify the input
   """
   print('{} - Command: emoji | Author: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),ctx.author))
   normalText=list(content.lower())
   emojiText = []

   for i in normalText:
        if i == '0': 
            emojiText.append(':zero:')
        elif i == '1': 
            emojiText.append(':one:')
        elif i == '2': 
            emojiText.append(':two:')
        elif i == '3': 
            emojiText.append(':three:')
        elif i == '4': 
            emojiText.append(':four:')
        elif i == '5': 
            emojiText.append(':five:')
        elif i == '6': 
            emojiText.append(':six:')
        elif i == '7': 
            emojiText.append(':seven:')
        elif i == '8': 
            emojiText.append(':eight:')
        elif i == '9': 
            emojiText.append(':nine:')
        elif i == 'b':
            emojiText.append(':b:')
        elif i == ' ':
            emojiText.append(' ')
        elif re.search("[a-z]", i):
            emojiText.append(':regional_indicator_{}:'.format(i))
        else:
            emojiText.append(i)

   fullStr = ' '.join(emojiText)
   await ctx.send(fullStr)
   print('{} - Task Finished Succesfully'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))


@commands.command()
async def ping(ctx):
    await ctx.send('pang')


@commands.command()
async def echo(ctx, n:int, *, content:str):
    """
    Echoes a message, !echo [amount of times to echo] [message here]
    """
    print('{} - Command: echo | Author: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),ctx.author))
    index = 0
    limit = 15
    if n > 0:
        while index < min(n,limit):
            await ctx.send(content)
            index += 1
    else:
        await ctx.send(content)
    print('{} - Task Finished Succesfully'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))


@commands.command()
async def coinflip(ctx):
    """
    Flip a coin
    """
    options=['Heads','Tails']
    await ctx.send('You rolled ' + options[random.randint(0,1)])


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
    bot.add_command(echo)
    bot.add_command(mute_where)
    bot.add_command(unmute_where)
    bot.add_command(unmute_all)
    bot.add_command(mute_status)
    bot.add_command(google)
    bot.add_command(coinflip)
    bot.add_command(emojify)
    bot.add_command(yank)
    bot.add_command(wordcloud)
    bot.add_command(force_nick)
    bot.add_command(reset_nick)
    bot.run(os.environ['BOT_TOKEN'])


if __name__ == "__main__":
    main()
