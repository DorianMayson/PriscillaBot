import discord
from discord.ext import commands, tasks
from discord.utils import get
from itertools import cycle
import youtube_dl
import os
import random

TOKEN = 'NzQ3Mzg0MTg0NTgyMTc2ODU4.X0OFww.GkFjN-uwc4QSVURY7BW3lL_tezo'
BOT_PREFIX = '.'

bot = commands.Bot(command_prefix=BOT_PREFIX)
status = cycle(['c высока...','.help'])
bot.remove_command('help')

@bot.event
async def on_ready():
    change_status.start()
    print("Logged in as: " + bot.user.name + "\n")

@tasks.loop(seconds=10)
async def change_status():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,name=next(status)))

@bot.command(pass_context=True)
async def help(ctx):
    author = ctx.message.author

    emb = discord.Embed(colour = discord.Colour.dark_purple())

    emb.set_author(name='Information about commands')
    emb.add_field(name='.', value='Мой префикс перед командой', inline=False)
    emb.add_field(name='.help', value='Чтобы вызвать это меню помощи снова', inline=False)
    emb.add_field(name='.clear', value= 'Чистит последнее сообщение в текущем чате', inline = False)
    emb.add_field(name='.clearall', value='Чистит последние 10 сообщений в текущем чате', inline = False)
    emb.add_field(name='.loveu', value='Признание в любви', inline = False)
    emb.add_field(name='.ping', value='Показывает мой пинг', inline = False)
    emb.add_field(name='.вопрос', value='Задайте любой интересующий вас вопрос', inline = False)
    emb.add_field(name='.join', value='Я зайду в ваш текущий голосовой чат', inline = False)
    emb.add_field(name='.leave(.l)', value='Я покину текущий голосовой чат', inline = False)
    emb.add_field(name='.play(.p)', value='Я начну играть интересующий вас трэк',inline = False)
    emb.add_field(name='.queue(.q)', value='Добавлю трек в очередь,если уже что-то играет', inline=False)
    emb.add_field(name='.pause(.pa)', value='Ставлю на паузу трек', inline=False)
    emb.add_field(name='.resume(.r)', value='Продолжаю трэк', inline=False)
    emb.add_field(name='.stop(.s)', value='Завершаю исполнение текущего трека',inline=False)
    emb.add_field(name='.игра', value='Начнётся игра(в разработке)')

    await author.send(embed=emb)

@bot.command(pass_context=True)
async def clear(ctx, amount=2):
    await ctx.channel.purge(limit=amount)

@bot.command(pass_context=True)
async def clearall(ctx, amount=11):
    await ctx.channel.purge(limit=amount)

@bot.command(pass_context=True, aliases=['loveu', 'LoveYou','loveyou'])
async def _loveu(ctx):
    varianti = ['Я тебя тоже :З',
                'И я тебя! :З',
                'Я тоже тебя люблю! :З',
                'И я тебя тоже люблю! :З']
    await ctx.send(random.choice(varianti))

@bot.command(pass_context=True)
async def ping(ctx):
    await ctx.send(f'Мой пинг:  {round(bot.latency * 1000)}ms')

@bot.command(aliases=['вопрос','Вопрос'])
async def _8ball(ctx,*,question):
    responces = ['Да!',
                 'Нет!',
                 'Конечно же да!',
                 'Конечно же нет!',
                 'Мне кажеться ты чмо...',
                 'Повтори,только теперь внятно!',
                 'Умоляю,избавь меня от этого',
                 'А еще что?',
                 'Думаю нет',
                 'У мамы своей спроси',
                 'Отвали',
                 'И шо?И шо?И ШОО??',
                 'Как говорил мой дед...']
    await ctx.send(f'Вопрос: {question}\nОтвет: {random.choice(responces)}')

@bot.command(pass_context=True, aliases=['j', 'joi'])
async def join(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    await voice.disconnect()

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        print(f"The bot has connected to {channel}\n")

    await ctx.send(f"Вошла в чат {channel}")

@bot.command(pass_context=True, aliases=['l', 'lea'])
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"The bot has left {channel}")
        await ctx.send(f"Покинула {channel}")
    else:
        print("Не могу покинуть чат,когда я не в нём")
        await ctx.send("Я и так не в голосовом!")

@bot.command(pass_context=True, aliases=['p', 'pla'])
async def play(ctx, url: str):

    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            print("Удалён старый файл песни")
    except PermissionError:
        print("Не могу удалить песню,которая сейчас играет")
        await ctx.send("Ошибочка,музыка уже играет")
        return

    await ctx.send("Ща всё буит,надеюсь это не реп...")

    voice = get(bot.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        ydl.download([url])

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            print(f"Renamed File: {file}\n")
            os.rename(file, "song.mp3")

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: print("Композиция запущена..."))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.45

    nname = name.rsplit("-", 2)
    await ctx.send(f"Сейчас играет: {nname[0]}")
    print("playing\n")

@bot.command(pass_context=True, aliases=['pa', 'pau'])
async def pause(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Композиция на паузе")
        voice.pause()
        await ctx.send("Композиция на паузе")
    else:
        print("Музыка не играет,пауза невозможна")
        await ctx.send("Музыка не играет,пауза невозможна")

@bot.command(pass_context=True, aliases=['r', 'res'])
async def resume(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        print("Продолжение композиции")
        voice.resume()
        await ctx.send("Продолжение композиции")
    else:
        print("Мелодия не на паузе")
        await ctx.send("Мелодия не на паузе")

@bot.command(pass_context=True, aliases=['s', 'sto'])
async def stop(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    queues.clear()

    if voice and voice.is_playing():
        print("Мелодия остановлена")
        voice.stop()
        await ctx.send("Мелодия остановлена")
    else:
        print("Ничего не играет,чтобы остановить")
        await ctx.send("Ничего не играет,чтобы остановить")

queues = {}

@bot.command(pass_context=True, aliases=['q', 'que'])
async def queue(ctx, url: str):
    Queue_infile = os.path.isdir("./Queue")
    if Queue_infile is False:
        os.mkdir("Очередь")
    DIR = os.path.abspath(os.path.realpath("Очередь"))
    q_num = len(os.listdir(DIR))
    q_num += 1
    add_queue = True
    while add_queue:
        if q_num in queues:
            q_num += 1
        else:
            add_queue = False
            queues[q_num] = q_num

    queue_path = os.path.abspath(os.path.realpath("Очередь") + f"\song{q_num}.%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'outtmpl': queue_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Загрузка музыки\n")
        ydl.download([url])
    await ctx.send("Добавлена " + str(q_num) + " песня,приятного прослушивания!")

    print("Музыка добавлена в очередь\n")

@bot.command(aliases=['игра','ИГРА'])
async def Игра(ctx):
    await ctx.send('Суть игры в том,чтобы угадать какое число я загадала.Поехали...')
    number = random.randint(0, 10)
    i1 = 0

    while True:
        answer = input('Угадай число: ')
        if answer == "" or answer == "exit":
            print("Выход из игры")
            await ctx.send('Выход из игры')
            break

        if not answer.isdigit():
            print("Введи правильное число")
            await ctx.send('Введи правильное число')
            continue

        answer = int(answer)
        i1 = i1 + 1
        if answer == number:
            print('Верно!')
            await ctx.send('Верно,поздравляю!:З')
            break

        elif answer < number:
            print('Загаданное число больше')
            await ctx.send('Загаданное число больше')
        else:
            print('Загаданное число меньше')
            await ctx.send('Загаданное число меньше')
    print('загаданное число: ', number, 'количество попыток: ', i1)
    await ctx.send('загаданное число: ', number, 'количество попыток: ', i1)
    if i1 > 3:
        await ctx.send('Ну ты и лошара конечно...')
    await ctx.send()

bot.run(TOKEN)