import discord
from discord.ext import commands
import numpy as np
import asyncio
import time
import re
import server
import steam_server
import valve.source
import pickle
import datetime

"""
TODO LIST
1. 커맨드별 권한 설정
2. notify 테스트
3. 맵 알림 중복
"""

r = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")

TOKEN = "NTM2NDUwMjM5ODY4MDQzMjY1.DyW6PA.trxuITtdWXUtp_cR2pFe9RGIUIE"
client = commands.Bot(command_prefix="!")
prev_map = [["ip", 123,["map",0]]]

with open ("prev_map.p","rb") as f:
    prev_map = pickle.load(f)

def map_save():
    with open("prev_map.p","wb") as f:
        pickle.dump(prev_map, f)

server_list = server.server_list()

def log(string):
    with open("discord_bot.log","wb") as log:
        string = format(str(time.ctime(int(time.time()))) + " : "+string)
        print(string)
        log.write(string.encode())
        log.close()

@client.command(pass_context=True)
async def server(ctx):
    for i in server_list.clist:
        if i[0] == ctx.message.channel.id:
            temp = await client.say("steam://connect/"+i[1]+":"+str(i[2]))
            await asyncio.sleep(3)
            await client.delete_message(temp)
            await client.delete_message(ctx.message)

@client.command(pass_context=True)
async def add(ctx, ip, port=27015):
    print("addserver")
    result = server_list.add_server(ctx.message.channel.id,ip, port)
    print(server_list.slist)
    if result == 1:
        prev_map.append([ip,port,["dummy",0]])
        temp = await client.say("Add server successfully")
        await asyncio.sleep(3)
        await client.delete_message(temp)
        await client.delete_message(ctx.message)
    else:
        temp = await client.say("Error")
        await asyncio.sleep(3)
        await client.delete_message(temp)
        await client.delete_message(ctx.message)

@add.error
async def addserver_error(error,ctx):
    temp = await client.say("type `!add <ip> [port{default:27015}]`")
    await asyncio.sleep(3)
    await client.delete_message(temp)
    await client.delete_message(ctx.message)

@client.command(pass_context=True)
async def remove(ctx):
    result = server_list.remove_server(ctx.message.channel.id)
    if result == 1:
        temp = await client.say("Remove server successfully")
        await asyncio.sleep(3)
        await client.delete_message(temp)
        await client.delete_message(ctx.message)
    else:
        temp = await client.say("Error")
        await asyncio.sleep(3)
        await client.delete_message(temp)
        await client.delete_message(ctx.message)

@client.command(pass_context=True)
async def map(ctx):
    a=[]
    err = 0
    for i in server_list.clist:
        if i[0] == ctx.message.channel.id:
            a = [i[1], i[2]]
    try:
        sserver = steam_server.server(a[0], int(a[1]))
        new_map = discord.Embed(title = sserver["server_name"],description="Now Playing: "+str(sserver["map"])+"\n"+"Playing: "+str(sserver["player_count"])+"/"+str(sserver["max_players"])+"\n"+"Connect: steam://connect/"+a[0]+":"+str(a[1]),timestamp=datetime.datetime.utcnow())
    except valve.source.NoResponseError as e:
        err = 1
        pass
    if a == []:
        temp = await client.say("Add server first")
    elif err == 1:
        temp = await client.say("Server seems offline")
    else:
        temp = await client.say(embed=new_map)
    await asyncio.sleep(3)
    await client.delete_message(temp)
    await client.delete_message(ctx.message)
    log("send map to " + ctx.message.channel.server.name + "(" + str(ctx.message.channel.server.id) + ")" + "." + ctx.message.channel.name + "(" + str(ctx.message.channel.id) + ")" + "." + ctx.message.author.name)

@client.command(pass_context=True)
async def players(ctx):
    a=[]
    err = 0
    for i in server_list.clist:
        if i[0] == ctx.message.channel.id:
            a = [i[1], i[2]]
            break
    if a == []:
        temp = await client.say("Add server first")
        await asyncio.sleep(3)
        await client.delete_message(temp)
        return
    try:
        splayers = steam_server.player(a[0], int(a[1]))["players"]
        await client.delete_message(ctx.message)
    except valve.source.NoResponseError as e:
        err = 1
        pass
    splayer = ""
    print(splayers[0]["name"])

    embed = discord.Embed(title="Players", timestamp=datetime.datetime.utcnow())
    for i in splayers:
        splayer = splayer + i["name"] + "\n"
    if err == 1:
        temp = await client.say("Server seems offline")
        await asyncio.sleep(3)
        await client.delete_message(temp)
        await client.delete_message(ctx.message)
    else:
        temp = await client.send_message(ctx.message.author,"```"+splayer+"```")
        await client.delete_message(ctx.message)

@players.error
async def players_error(error,ctx):
    temp = await client.send_message(ctx.message.channel,"Error!")
    await asyncio.sleep(3)
    await client.delete_message(temp)
    await client.delete_message(ctx.message)

@client.command(pass_context=True)
async def notify(ctx, map):
    add_map = 1
    add_channel = 1
    print("notify "+map)
    for a in range(len(server_list.notify)):
        if a == ctx.message.channel.id:
            add_channel = 0
            if server_list.notify[a][1] == map:
                add_map = 0
                for l in server_list.notify[a][2]:
                    if l == ctx.message.author.id:
                        temp = await client.say(map +" is already added your notify list")
                        await asyncio.sleep(3)
                        await client.delete_message(temp)
                        return
                server_list.notify[a][2].append(ctx.message.author.id)
                server_list.save()
                temp = await client.say("1 Add "+map + " to your notify list")
                await asyncio.sleep(3)
                await client.delete_message(temp)
                return
            server_list.notify[a].append(map)
            server_list.notify[a].append([ctx.message.author.id])
            server_list.save()
            temp = client.say("1 Add " + map + " to your notify list")
            await asyncio.sleep(3)
            await client.delete_message(temp)
            return
    server_list.notify.append([ctx.message.channel.id,map,[ctx.message.author.id]])
    server_list.save()
    temp = await client.say("1 Add " + map + " to your notify list")
    await asyncio.sleep(3)
    await client.delete_message(temp)
    return

@notify.error
async def notify_error(error, ctx):
    temp = await client.send_message(ctx.message.channel, "!notify [map]")
    await asyncio.sleep(3)
    await client.delete_message(temp)
    print(error)

@client.command(pass_context=True)
async def unnotify(ctx, map):
    for a in range(len(server_list.notify)):
        if a == ctx.message.channel.id:
            if server_list.notify[a][1] == map:
                for l in range(len(server_list.notify[a][2])):
                    if server_list.notify[a][2][l] == ctx.message.author.id:
                        del server_list.notify[a][2][l]
                        server_list.save()
                        temp = await client.say("Remove "+map + " on your notify list")
                        await asyncio.sleep(3)
                        await client.delete_message(temp)
                        return
                        temp = await client.say("Did you add " + map + " on your notify list?")
                        await asyncio.sleep(3)
                        await client.delete_message(temp)
                return
                temp = await client.say("Did you add " + map + " on your notify list?")
                await asyncio.sleep(3)
                await client.delete_message(temp)
            return
    temp = await client.say("Did you add "+map+" on your notify list?")
    await asyncio.sleep(3)
    await client.delete_message(temp)
    return

@unnotify.error
async def unnotify_error(error,ctx):
    temp = await client.send_message(ctx.message.channel,"!unnotify [map]")
    await asyncio.sleep(3)
    await client.delete_message(temp)
    print(error)

@client.event
async def on_ready():
    print(client)
    print(client.user.name)
    print(client.user.id)
    print("--------------------")
    print(server_list.slist)
    print("--------------------")
    print(server_list.clist)
    print("--------------------")
    print(server_list.notify)
    print("--------------------")
    log("Bot turned on")


# 맵 업데이트 타이머
async def map_update():
    while(True):
        await asyncio.sleep(4)
        print(prev_map)
        for a in server_list.slist:
            off = 0
            error = 0
            try:
                sserver = steam_server.server(a[0], int(a[1]))
                new_map = discord.Embed(title = sserver["server_name"],description="Now Playing: "+str(sserver["map"])+"\n"+"Playing: "+str(sserver["player_count"])+"/"+str(sserver["max_players"])+"\n"+"Connect: steam://connect/"+a[0]+":"+str(a[1]),timestamp=datetime.datetime.utcnow())
            except valve.source.NoResponseError as e:
                off = 1
                error = 1
                pass
            for i in range(len(prev_map)):
                if prev_map[i][0] == a[0]:
                    if error == 1:
                        if prev_map[i][2][1] == 20:
                            for c in a[2]:
                                c = client.get_channel(c)
                                await client.send_message(c, "Server seems offline")
                                pass
                        else:
                            prev_map[i][2] = [prev_map[i][2][0], prev_map[i][2][1] + 1]
                            map_save()
                    elif not prev_map[i][2][0] == sserver["map"]:
                        for c in a[2]:
                            c = client.get_channel(c)
                            print(prev_map[i], sserver["map"])
                            prev_map[i][2] = [sserver["map"], 0]
                            map_save()
                            await client.send_message(c, embed=new_map)
                            pass
                            off = 1


def default():
    with open("server_list.p", "wb") as f:
        pickle.dump([], f)
    with open("prev_map.p", "wb") as f:
        pickle.dump([], f)


client.loop.create_task(map_update())
client.run(TOKEN)

log("Bot turned off")