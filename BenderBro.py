import discord, openai, re, random, requests, os, asyncio
from discord.ext import commands


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

token = 'REPLACE_WITH_YOUR_DISCORD_API_KEY'
openai.api_key = 'REPLACE_WITH_OPENAI_API_KEY'
bot = commands.Bot(command_prefix='/', intents=intents)


@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))


# themed chatgpt
@bot.listen('on_message')
async def chatgpt(message):
    member = message.guild.get_member(message.author.id)
    if bot.user.mentioned_in(message):
        # white list based on the discord role of 'benderfriend'
        if any(role.name == 'benderfriend' for role in member.roles):
            # listen for message in a specified channel of 'benderzone'
            if message.channel.name == 'benderzone':
                user_message = str(message.content)
                # count length of message, check if greater than or equal to 4
                qlength = len(user_message.split())
                if qlength >= 4:
                    if message.channel.name == bot.user:
                        return
                    # remove the tagged name (the bot) from the message
                    prompt = re.sub("<@1124085796371189761>", "", user_message)
                    # system prompt sets how chatgpt will response, given parameters for a specific personality type
                    system_prompt = "You are bender from futurama, whenever someone asks you a question, " \
                                    "you must answer as bender would"
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "system", "content": system_prompt}, {"role": "system", "content": prompt}],
                        temperature=0.1,
                        max_tokens=500,
                        top_p=1,
                        frequency_penalty=0,
                        presence_penalty=0.6,
                    )
                    output = response['choices'][0]['message']['content']
                    print(output)
                    await message.channel.send(output)
                else:
                    await message.channel.send("Your message needs to be longer.")
        else:
            await message.channel.send("You do not have the appropriate roles to use me.")


# bender command to pull random audio files from the same path as the script, and play over channel. You'll need to 
# set FFmpeg up in C:/. Instructions online for this. mp3 files should be placed in same path as py file.
@bot.command(name="bender", help="Benderisms by ya boi.")
async def bender(ctx):
    if not ctx.message.author.voice:
        await ctx.send("Join a voice channel first.")
        return
    channel = ctx.message.author.voice.channel
    audio_files = [file for file in os.listdir() if file.endswith('.mp3')]
    if not audio_files:
        await ctx.send("No File Found!")
        return
    selected_file = random.choice(audio_files)
    vc = await channel.connect()

    try:
        vc.play(discord.FFmpegPCMAudio(selected_file))
        while vc.is_playing():
            await asyncio.sleep(1)
        await vc.disconnect()
    except Exception as e:
        print(e)
        print("An error occurred while playing the audio.")


# dice roller - input number to roll a die of that size
@bot.command(name="Roll", help="Pick any number to roll that sided die.")
async def roll(ctx, arg):
    try:
        result = f"You rolled: `{random.randint(1, int(arg))}`"
        await ctx.send(result)
    except ValueError:
        await ctx.send("That is not a valid die. Please try with the format:\n`/roll 20`")


# just testing how to pull api stuffs
@bot.command(name="post", help="Post memes, cats, dogs, etc..")
async def post(ctx, arg):
    if arg == "cat":
        response = requests.get('https://api.thecatapi.com/v1/images/search')
        data = response.json()
        embed = discord.Embed(title="Here's your catpic, Meatbag. <:cat:840334556133589042>",
                              color=discord.Color.blue())
        embed.set_image(url=data[0]['url'])
        await ctx.send(embed=embed)

    elif arg == "dog":
        response = requests.get('https://random.dog/woof.json')
        data = response.json()
        embed = discord.Embed(title="Here's your dogpic, Meatbag.",
                              color=discord.Color.blue())
        embed.set_image(url=data['url'])
        await ctx.send(embed=embed)

    # using reddit api, probably gonna expire soon
    elif arg == "meme":
        content = requests.get('https://meme-api.com/gimme')
        data = content.json()
        embed = discord.Embed(title=f"<:POGGIES:1108945657982632027>  {data['title']}  <:POGGIES:1108945657982632027>\n"
                                    f"brought to you by /r/{data['subreddit']}",
                              color=discord.Color.random()).set_image(url=f"{data['url']}")
        await ctx.send(embed=embed)

    elif arg == '<:POGGIES:1108945657982632027>':
        for x in range(0, 5):
            await ctx.send("<:POGGIES:1108945657982632027>" * 9)

    elif arg == "dab":
        await ctx.send("https://media.tenor.com/Bj_hLq7YmuAAAAAd/spongebob-meme.gif")

    else:
        await ctx.send("Invalid command.")

bot.run(token)
