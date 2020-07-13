import discord, json, os, sqlite3, ast, info, datetime, time
from discord.ext import commands, tasks, menus
from itertools import cycle
from discord.utils import get

async def get_prefix(bot, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)]

prefix = '$'

def return_prefix(guild):
    with open('prefixes.json', 'r') as f:
        prefixreturn = json.load(f)

    return prefixreturn[str(guild)]

client = commands.Bot(command_prefix = get_prefix)
client.remove_command('help')

msg = None

colours = color_ = 0x2f3136

conn = sqlite3.connect('base.db')
c = conn.cursor()
'''c.execute("""CREATE TABLE warns (
    id text,
    reason text,
    serverid text
    )""")'''

uptime = time.time()

@client.event
async def on_ready():
    print(f'{client.user.name} is online')
    await client.change_presence(activity=discord.Streaming(platform="Twitch", name="version 1.0 | ServerProtect", url="https://twitch.tv/#"))

@client.event
async def on_message(message):
    if client.user.mentioned_in(message):
        await message.channel.send(f"Witam! Nazywam się ServerProtect I jestem botem który ochroni twój serwer podczas ataków nad nim! Mój prefix na tym serwerze to **{return_prefix(message.guild.id)}**")
    await client.process_commands(message)


@client.event
async def on_guild_join(guild):
    f = open(f"C:\\Users\\Kacper\\Desktop\\ServerProtect\\configs\\{guild.id}.json", "w+")
    f.write("{}")
    f.close()
    with open('prefixes.json') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = "$"

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

@client.event
async def on_guild_remove(guild):
    os.remove(f"C:\\Users\\Kacper\\Desktop\\ServerProtect\\configs\\{guild.id}.json")
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

@client.event
async def on_member_join(member):
    c.execute(f"SELECT reason from global WHERE id='{member}'")
    data = c.fetchall()
    if len(data) == 0:
        pass
    else:
        await member.kick(member)
    with open('welcome-config.json', 'r') as f:
        config = json.load(f)
    with open('welcome-channel.json', 'r') as f:
        channel = json.load(f)
    kanalid = channel[str(member.guild.id)]
    try:
        if len(config[str(member.guild.id)]) > 0:
            kanal = get(member.guild.text_channels, id=kanalid)
            messagesend = config[str(member.guild.id)]
            if "%nazwa%" in messagesend:
                messagesend = messagesend.replace("%nazwa%", str(member.mention))
                await kanal.send(messagesend)
            else:
                await kanal.send(messagesend)
    except Exception as e:
        pass
                

@client.command()
async def setprefix(ctx, prefix):
    with open('prefixes.json') as f:
        prefixes = json.load(f)
    prefixes[str(ctx.guild.id)] = prefix

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

    await ctx.send("Prefix set to " + prefix)

@client.command()
@commands.has_guild_permissions(administrator=True)
async def slowmode(ctx, time=None):
    if time is None:
        await ctx.send(f"Poprawne użycie = {await client.get_prefix(ctx.message)}slowmode (czas w sekundach)")
    else:
        channel = ctx.message.channel
        await channel.edit(slowmode_delay=time)
        await ctx.send(f"Slowmode ustawiony na {time} sekund!")

@client.command(aliases=['pomoc'])
async def help(ctx):
    global colours
    em = discord.Embed(color=colours, title="ServerProtect | Help Menu", timestamp=ctx.message.created_at)
    em.add_field(name="**:jigsaw: Prefix**", value=f"```{return_prefix(ctx.guild.id)}```", inline=False)
    em.add_field(name="**:thumbsup: Ogólne**", value="```mywarns, statystyki```", inline=False)
    em.add_field(name=":notepad_spiral: **Whitelist**", value="```globalban```", inline=False)
    em.add_field(name=":question: **Sprawdzanie**", value="```userinfo, avatar```", inline=False)
    em.add_field(name=":robot: **Administracyjne**", value="```ban, kick, warn, removewarn, clear, setprefix, welcome```", inline=False)
    em.add_field(name=":file_folder: **Kanałowe**", value="```zablokuj, odblokuj, nuke, slowmode```", inline=False)
    em.add_field(name="**Bot**", value="\n\n[`SUPPORT`](https://discord.gg/SgZ78P2)", inline=False)
    em.set_footer(text=f'WYWOŁAŁ  {ctx.message.author}', icon_url=ctx.author.avatar_url)
    await ctx.send(embed=em)

@client.command(aliases=['purge', 'cls'])
@commands.has_guild_permissions(administrator=True)
async def clear(ctx, num: int=None):
    if num is None:
        await ctx.send("Musisz podać liczbe wiadomości których chcesz usunąć!")
    else:
        await ctx.message.delete()
        await ctx.channel.purge(limit=num)

@client.command()
@commands.has_guild_permissions(administrator=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    if member is None:
        await ctx.send("Musisz podać osobę którą chcesz zbanować!")
    elif reason is None:
        await ctx.send("Musisz podać powód bana!")
    else:
        await ctx.guild.ban(member, reason=reason)
        await ctx.send(f"Użytkownik {member.mention} został zbanowany za {reason}")


@client.command()
@commands.has_guild_permissions(administrator=True)
async def unban(ctx, member: discord.Member):
    if member is None:
        await ctx.send("Musisz podać użytkownika do wyrzucenia!")
    else:
        await ctx.guild.unban(member)
        await ctx.send(f"Odbanowano " + member)

@client.command()
@commands.has_guild_permissions(administrator=True)
async def kick(ctx, member: discord.Member):
    await ctx.guild.kick(member)
    await ctx.send(f"{member.mention} został wyrzucony z serwera!")

@client.command()
@commands.has_guild_permissions(administrator=True)
async def globalban(ctx, member: discord.Member, *, reason=None):
    if member is None:
        await ctx.send("Musisz podać osobę którą chcesz zbanować!")
    elif reason is None:
        await ctx.send("Musisz podać powód bana!")
    else:
        with open('whitelist.json', 'r') as f:
            whitelist = json.load(f)
        try:
            if len(whitelist[str(ctx.message.author.id)]) > 0:
                c.execute(f"INSERT INTO global VALUES ('{member}', '{reason}')")
                conn.commit()
                await ctx.send(f"Użytkownik {member.mention} został globalnie zbanowany za {reason}")
                await ctx.guild.ban(member, reason=f"global ban. server reason = {reason}")
        except:
            await ctx.send("Nie masz whitelisty na global-banowanie!")

@client.command()
@commands.has_guild_permissions(administrator=True)
async def warn(ctx, member: discord.Member=None, *, reason=None):
    if member is None:
        await ctx.send("Musisz podać osobe której chcesz dać ostrzeżenie!")
    elif reason is None:
        await ctx.send("Musisz podać powód ostrzeżenia!")
    else:
        c.execute(f"INSERT INTO warns VALUES ('{member}', '{reason}', '{ctx.message.guild.id}')")
        conn.commit()
        await ctx.send(f"Użytkownik {member.mention} dostał ostrzeżenie. Powód: {reason}")


@client.command()
async def mywarns(ctx):
    global colours
    outputlol = list()
    member = ctx.message.author
    c.execute(f"SELECT reason from warns WHERE id='{member}' AND serverid='{ctx.message.guild.id}'")
    output = c.fetchall()
    if len(output) == 0:
        Embed = discord.Embed(colour=colours, title="System ostrzeżeń", timestamp=ctx.message.created_at)
        Embed.add_field(name=f"Twoje ostrzeżenia", value="Nie posiadach żadnych ostrzeżeń!", inline=False)
        Embed.set_footer(text=f'WYWOŁAŁ {ctx.message.author}', icon_url=ctx.author.avatar_url)
        Embed.set_author(name="ServerProtect", url="https://hx54.xyz/", icon_url="https://cdn.discordapp.com/attachments/722621049698648136/722621130690658344/90688356-vector-flat-icon-of-lock-on-black-background.jpg")
        await ctx.send(embed=Embed)
    else:
        for x in output:
            x = str(x)
            line = x.split("('")
            second = line[1]
            real = second.split("',)")
            real.pop(1)
            outputlol.append(real[0])
        Embed = discord.Embed(colour=colours, title="Warning system")
        Embed.add_field(name=f"Twoje warny", value=f"{', '.join(outputlol)}", inline=False)
        Embed.set_footer(text=f'WYWOŁAŁ  {ctx.message.author} • {ctx.message.created_at}')
        Embed.set_author(name="ServerProtect", url="https://hx54.xyz/", icon_url="https://cdn.discordapp.com/attachments/722621049698648136/722621130690658344/90688356-vector-flat-icon-of-lock-on-black-background.jpg")
        await ctx.send(embed=Embed)

@client.command()
async def userinfo(ctx, member: discord.Member = None):
    member = ctx.message.author if not member else member
    roles = [role for role in member.roles]
    embed = discord.Embed(colour=colours, timestamp=ctx.message.created_at)
    
    embed.set_author(name=f'Informacje Użytkownika - {member}', url="https://hx54.xyz/", icon_url="https://cdn.discordapp.com/attachments/722621049698648136/722621130690658344/90688356-vector-flat-icon-of-lock-on-black-background.jpg")
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text=f'WYWOŁAŁ {ctx.message.author}', icon_url=ctx.author.avatar_url)

    embed.add_field(name="ID:", value=member.id)
    embed.add_field(name="Nazwa serwera:", value=member.display_name)

    embed.add_field(name="Data stworzenia konta:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
    embed.add_field(name="Data dołączenia:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))

    embed.add_field(name=f'Role ({len(roles)})', value=" ".join([role.mention for role in roles]))
    embed.add_field(name="Najwyzsza rola:", value=member.top_role.mention)

    embed.add_field(name="Bot?", value=member.bot)

    await ctx.send(embed=embed)

@client.command()
async def avatar(ctx, member: discord.Member=None):
    if member is None:
        member = ctx.message.author
    await ctx.send(member.avatar_url)

def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


@client.command(aliases=['eval'])
@commands.is_owner()
async def evaluate(ctx, *, cmd):
    fn_name = "_eval_expr"
    cmd = cmd.strip("` ")
    # add a layer of indentation
    cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
    # wrap in async def body
    body = f"async def {fn_name}():\n{cmd}"

    parsed = ast.parse(body)
    body = parsed.body[0].body

    insert_returns(body)

    env = {
        'bot': ctx.bot,
        'discord': discord,
        'commands': commands,
        'ctx': ctx,
        '__import__': __import__
    }
    exec(compile(parsed, filename="<ast>", mode="exec"), env)

    result = (await eval(f"{fn_name}()", env))
    await ctx.send(result)


class MyMenu(menus.Menu):
        global msg
        async def send_initial_message(self, ctx, channel):
            await ctx.message.delete()
            embed = discord.Embed(colour=discord.Colour.green(), timestamp=ctx.message.created_at)
            embed.set_author(name=f'Ankieta - stworzona przez {ctx.message.author}', url="https://hx54.xyz/", icon_url="https://cdn.discordapp.com/attachments/722621049698648136/722621130690658344/90688356-vector-flat-icon-of-lock-on-black-background.jpg")
            embed.add_field(name="Treść ankiety: ", value=f"**{msg}**")
            embed.set_footer(text=f'WYWOŁAŁ {ctx.message.author}', icon_url=ctx.author.avatar_url)
            return await channel.send(embed=embed)

        @menus.button('\N{WHITE HEAVY CHECK MARK}')
        async def on_thumbs_up(self, payload):
            return

        @menus.button('\N{CROSS MARK}')
        async def on_thumbs_down(self, payload):
            return


@client.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def ankieta(ctx, *, wiadom=None):
    global msg
    if wiadom != None:
        msg = wiadom
        m = MyMenu()
        await m.start(ctx)
    else:
        await ctx.send("Musisz wpisać treść ankiety!")

@client.command()
@commands.has_guild_permissions(administrator=True)
async def zablokuj(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("Ten kanał został zablokowany! Od teraz tylko administracja może wysyłać wiadomości!")

@client.command()
@commands.has_guild_permissions(administrator=True)
async def odblokuj(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("Ten kanał został odblokowany!")

@client.command()
@commands.has_guild_permissions(administrator=True)
async def nuke(ctx):
    channelname = ctx.channel.name
    await ctx.channel.clone()
    await ctx.channel.delete()
    newchannel = get(ctx.guild.text_channels, name=channelname)
    await newchannel.send("Ten kanał został nukowany!", delete_after=10)

@client.command(aliases=['staty'])
async def statystyki(ctx):
    onlineuser = 0
    for x in client.get_all_members():
        if str(x.status) != "offline":
            onlineuser += 1
    current_time = time.time()
    difference = int(round(current_time - uptime))
    text = str(datetime.timedelta(seconds=difference))
    em = discord.Embed (
        color = colours,
        title = "Statystyki bota",
        description = f"● <:bust_in_silhouette:731566170188284016> **Użytkownicy: {len(client.users)}** \n\n ● <:file_folder:731566457678200854> **Serwery: {len(client.guilds)}** \n\n ● <:green_circle:731573322554277899> **Użytkowników online: {onlineuser}** \n\n ● <:timer:732030489904283760> **Czas online: {text}**",
        timestamp = ctx.message.created_at
    )
    em.set_thumbnail(url=client.user.avatar_url)
    em.set_footer(text=f'WYWOŁAŁ  {ctx.message.author}', icon_url=ctx.author.avatar_url)
    await ctx.send(embed=em)

@client.command()
@commands.has_guild_permissions(administrator=True)
async def removewarn(ctx, member: discord.Member=None, *, warn=None):
    if member and warn != None:
        warn = str(warn)
        c.execute(f"SELECT reason from warns WHERE id='{member}' AND reason='{warn}' AND serverid='{ctx.message.guild.id}'")
        output = c.fetchall()
        if len(output) != 0:
            c.execute(f"DELETE from warns WHERE id='{member}' AND reason='{warn}' AND serverid='{ctx.message.guild.id}'")
            conn.commit()
            await ctx.send(f"Usunięto ostrzeżenie użytkownika {member.mention} o treści **{warn}**")
        else:
            await ctx.send("Ten użytkownik nie ma takie ostrzeżenia")
    else:
        if member is None:
            await ctx.send("Musisz podać użytkownika któremu chcesz usunąć ostrzeżenie!")
        elif warn is None:
            await ctx.send("Musisz podać ostrzeżenie ktore chciał byś usunąć!")

@client.command()
@commands.has_guild_permissions(administrator=True)
async def welcome(ctx, channel: discord.TextChannel=None, *, message=None):
    if channel is None and message is None:
        await ctx.send(f"Witam! Teraz konfigurujesz wiadomość powitalną! wpisz {return_prefix(ctx.guild.id)}welcome wiadomość. Możesz użyć %nazwa% żeby miec nazwe użytkownika.")
    elif channel is None:
        await ctx.send("Musisz podać kanał!")
    elif message is None:
        await ctx.send("Musisz podać wiadomość powitalną!")
    else:
        with open('welcome-config.json') as f:
            config = json.load(f)
        try:
            if len(config[str(ctx.guild.id)]) != 0:

                #Remove old message
                with open('welcome-config.json') as f:
                    config = json.load(f)
                config.pop(str(ctx.guild.id))
                with open('welcome-config.json', 'w') as f:
                    json.dump(config, f, indent=4)

                #Add new message
                with open('welcome-config.json', 'r') as f:
                    config = json.load(f)
                config[str(ctx.guild.id)] = message
                with open('welcome-config.json', 'w') as f:
                    json.dump(config, f, indent=4)

                #Remove old channel
                with open('welcome-channel.json', 'r') as f:
                    channel1 = json.load(f)
                channel1.pop(str(ctx.guild.id))
                with open('welcome-channel.json', 'w') as f:
                    json.dump(channel1, f, indent=4)

                #add new channel
                with open('welcome-channel.json', 'r') as f:
                    channel1 = json.load(f)
                ch = channel.id
                channel1[str(ctx.guild.id)] = ch
                with open('welcome-channel.json', 'w') as f:
                    json.dump(channel1, f, indent=4)    

                await ctx.send(f"Ustawiono nową wiadomość: {message}")
        except KeyError:
            with open('welcome-config.json', 'r') as f:
                config = json.load(f)
            config[str(ctx.guild.id)] = message
            with open('welcome-config.json', 'w') as f:
                json.dump(config, f, indent=4)

            with open('welcome-channel.json', 'r') as f:
                channel1 = json.load(f)
            ch = channel.id
            channel1[str(ctx.guild.id)] = ch
            with open('welcome-channel.json', 'w') as f:
                json.dump(channel1, f, indent=4)
            
            await ctx.send(f"Dodano nową wiadomość powitalną: {message}")


@ankieta.error
@slowmode.error
@kick.error
@ban.error
@unban.error
@clear.error
@removewarn.error
@warn.error
@nuke.error
@zablokuj.error
@odblokuj.error
@welcome.error
async def command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Ojoj! Nie masz permisji na to!")
    elif isinstance(error, commands.CommandOnCooldown):
        errorstr = str(error).split('in')
        await ctx.send("Spokojnie! Możesz znów użyć tej komendy za " + errorstr[2])

client.run(info.info["token"])
