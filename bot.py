import discord, json, os, sqlite3, ast, info
from discord.ext import commands, tasks, menus
from datetime import datetime
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
    reason text
    )""")'''


@client.event
async def on_ready():
    print(f'{client.user.name} is online')
    await client.change_presence(activity=discord.Streaming(platform="Twitch", name="version 1.0 | ServerProtect", url="https://twitch.tv/#"))

@client.event
async def on_message(message):
    global client
    if client.user.mentioned_in(message):
        await message.channel.send(f"Hello! I am ServerProtect, a bot that will protect your discord guild! My prefix is **{return_prefix(message.guild.id)}**")
    await client.process_commands(message)


@client.event
async def on_guild_join(guild):
    f = open(f"C:\\Users\\Kacper\\Desktop\\ServerProtect\\configs\\{guild.id}.json", "w+")
    f.write("{}")
    f.close
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

    with open('prefixes.json', 'r') as f:
        json.dump(prefixes, f, indent=4)

@client.event
async def on_member_join(member):
    c.execute(f"SELECT reason from global WHERE id='{member}'")
    data = c.fetchall()
    if len(data) == 0:
        pass
    else:
        await member.kick(member)

@client.command()
async def load(ctx, extension):
    global client
    client.load_extension(f'cogs.{extension}')

@client.command()
async def unload(ctx, extension):
    global client
    client.unload_extension(f'cogs.{extension}')


@client.command()
async def setprefix(ctx, prefix):
    with open('prefixes.json') as f:
        prefixes = json.load(f)
    prefixes[str(ctx.guild.id)] = prefix

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

    await ctx.send("Prefix set to " + prefix)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


@client.command()
async def helpdump(ctx):
    cog = client.get_cog('Commands')
    commands = cog.get_commands()
    times = 0
    for c in commands:
        times += 1
    for x in range(times):
        for c in commands:
            await ctx.send(f'`{c.name}`')


@client.command()
@commands.has_guild_permissions(administrator=True)
async def slowmode(ctx, time=None):
    if time is None:
        await ctx.send(f"Correct usage = {await client.get_prefix(ctx.message)}slowmode (time in seconds)")
    else:
        channel = ctx.message.channel
        await channel.edit(slowmode_delay=time)
        await ctx.send(f"Channel slowmode has been set to {time} seconds!")

@client.command()
async def help(ctx):
    global colours
    em = discord.Embed(color=colours, title="ServerProtect | Help Menu")
    em.add_field(name="**General**", value="```mywarns```", inline=False)
    em.add_field(name="**Whitelist**", value="```globalban```", inline=False)
    em.add_field(name="**Checkers**", value="```userinfo, avatar```", inline=False)
    em.add_field(name="**Administration**", value="```ban, kick, warn, clear, slowmode, setprefix```", inline=False)
    em.add_field(name="**Bot**", value="\n\n[SUPPORT](https://discord.gg/SgZ78P2)", inline=False)
    await ctx.send(embed=em)

@client.command(aliases=['purge', 'cls'])
@commands.has_guild_permissions(administrator=True)
async def clear(ctx, num: int=None):
    if num is None:
        await ctx.send("You need to input the number of messages you want to delete!")
    else:
        await ctx.message.delete()
        await ctx.channel.purge(limit=num)

@client.command()
@commands.has_guild_permissions(administrator=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    if member is None:
        await ctx.send("You need to input member you would like to ban!")
    elif reason is None:
        await ctx.send("You need to input a reason for the ban!")
    else:
        await ctx.guild.ban(member, reason=reason)
        await ctx.send(f"User: {member.mention} has been banned for {reason}")


@client.command()
@commands.has_guild_permissions(administrator=True)
async def unban(ctx, member: discord.Member):
    if member is None:
        await ctx.send("You need to input a member to unban!")
    else:
        await ctx.guild.unban(member)
        await ctx.send(f"Unbanned " + member)

@client.command()
@commands.has_guild_permissions(administrator=True)
async def kick(ctx, member: discord.Member):
    await ctx.guild.kick(member)
    await ctx.send(f"{member.mention} has been kicked!")

@client.command()
@commands.has_guild_permissions(administrator=True)
async def globalban(ctx, member: discord.Member, *, reason=None):
    if member is None:
        await ctx.send("You need to input a member to globally ban!")
    elif reason is None:
        await ctx.send("You need to input a reason for ban!")
    else:
        with open('whitelist.json', 'r') as f:
            whitelist = json.load(f)
        try:
            if len(whitelist[str(ctx.message.author.id)]) > 0:
                c.execute(f"INSERT INTO global VALUES ('{member}', '{reason}')")
                conn.commit()
                await ctx.send(f"User {member.mention} has been globally banned for {reason}")
                await ctx.guild.ban(member, reason=f"global ban. server reason = {reason}")
        except:
            await ctx.send("You are not whitelisted to globally ban!")

@client.command()
@commands.has_guild_permissions(administrator=True)
async def warn(ctx, member: discord.Member=None, *, reason=None):
    if member is None:
        await ctx.send("You need to input a member to warn!")
    elif reason is None:
        await ctx.send("You need to input a reason for the warn!")
    else:
        c.execute(f"INSERT INTO warns VALUES ('{member}', '{reason}')")
        conn.commit()
        await ctx.send(f"User {member.mention} has been warned for {reason}")


@client.command()
async def mywarns(ctx):
    global colours
    outputlol = list()
    member = ctx.message.author
    c.execute(f"SELECT reason from warns WHERE id='{member}'")
    output = c.fetchall()
    if len(output) == 0:
        Embed = discord.Embed(colour=next(colours), title="Warning system")
        Embed.add_field(name=f"Your warns", value="This user has no warns!", inline=False)
        Embed.set_footer(text=f'EXECUTED BY {ctx.message.author} • {ctx.message.created_at}')
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
        Embed = discord.Embed(colour=next(colours), title="Warning system")
        Embed.add_field(name=f"Your warns", value=f"{', '.join(outputlol)}", inline=False)
        Embed.set_footer(text=f'EXECUTED BY {ctx.message.author} • {ctx.message.created_at}')
        Embed.set_author(name="ServerProtect", url="https://hx54.xyz/", icon_url="https://cdn.discordapp.com/attachments/722621049698648136/722621130690658344/90688356-vector-flat-icon-of-lock-on-black-background.jpg")
        await ctx.send(embed=Embed)

@client.command()
async def userinfo(ctx, member: discord.Member = None):
    member = ctx.message.author if not member else member
    roles = [role for role in member.roles]
    embed = discord.Embed(colour=discord.Colour.blue(), timestamp=ctx.message.created_at)
    
    embed.set_author(name=f'User info - {member}', url="https://hx54.xyz/", icon_url="https://cdn.discordapp.com/attachments/722621049698648136/722621130690658344/90688356-vector-flat-icon-of-lock-on-black-background.jpg")
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text=f'EXECUTED BY {ctx.message.author} • {ctx.message.created_at}', icon_url=ctx.author.avatar_url)

    embed.add_field(name="ID:", value=member.id)
    embed.add_field(name="Guild name:", value=member.display_name)

    embed.add_field(name="Account created at:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
    embed.add_field(name="Joined at:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))

    embed.add_field(name=f'Roles ({len(roles)})', value=" ".join([role.mention for role in roles]))
    embed.add_field(name="Top role:", value=member.top_role.mention)

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


@client.command()
@commands.is_owner()
async def evaluate(ctx, *, cmd):
    """Evaluates input.
    Input is interpreted as newline seperated statements.
    If the last statement is an expression, that is the return value.
    Usable globals:
      - `bot`: the bot instance
      - `discord`: the discord module
      - `commands`: the discord.ext.commands module
      - `ctx`: the invokation context
      - `__import__`: the builtin `__import__` function
    Such that `>eval 1 + 1` gives `2` as the result.
    The following invokation will cause the bot to send the text '9'
    to the channel of invokation and return '3' as the result of evaluating
    >eval ```
    a = 1 + 2
    b = a * 2
    await ctx.send(a + b)
    a
    ```
    """
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
            embed.set_author(name=f'Poll - made by {ctx.message.author}', url="https://hx54.xyz/", icon_url="https://cdn.discordapp.com/attachments/722621049698648136/722621130690658344/90688356-vector-flat-icon-of-lock-on-black-background.jpg")
            embed.add_field(name="Poll value: ", value=f"**{msg}**")
            embed.set_footer(text=f'EXECUTED BY {ctx.message.author} • {ctx.message.created_at}', icon_url=ctx.author.avatar_url)
            return await channel.send(embed=embed)

        @menus.button('\N{WHITE HEAVY CHECK MARK}')
        async def on_thumbs_up(self, payload):
            return

        @menus.button('\N{CROSS MARK}')
        async def on_thumbs_down(self, payload):
            return


@client.command()
async def poll(ctx, *, wiadom=None):
    global msg
    if wiadom != None:
        msg = wiadom
        m = MyMenu()
        await m.start(ctx)
    else:
        await ctx.send("You need to input the poll value!")

@client.command()
@commands.has_guild_permissions(administrator=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("This channel has been locked! Only the administrators have permission to send messages as of now!")

@client.command()
@commands.has_guild_permissions(administrator=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("This channel has been unlocked!")

@client.command()
@commands.has_guild_permissions(administrator=True)
async def nuke(ctx):
    oldchannel = ctx.channel
    channelname = ctx.channel.name
    await oldchannel.clone()
    await oldchannel.delete()
    newchannel = get(ctx.guild.text_channels, name=channelname)
    await newchannel.send("This channel has been nuked!")

@slowmode.error
@kick.error
@ban.error
@unban.error
@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(error)

client.run(info.info["token"])
