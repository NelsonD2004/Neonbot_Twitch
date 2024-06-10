from twitchio.ext import commands
from twitchio.ext import routines
import twitchio as twio
import pymysql
import datetime
import random

con = pymysql.connect(
    host="db-mfl-01.sparkedhost.us",
    port=3306,
    user="u109224_Krhr5CV2M2",
    passwd="LzwM5tsReqzPH^1I1+@@XA2A",
    database="s109224_Bot",
)

cur = con.cursor()


@routines.routine(hours=12)
async def monthly_check():
    day = datetime.date.today().day
    if day == 1:
        cur.execute("DELETE FROM Activity")
        con.commit()


@routines.routine(minutes=0.9)
async def auto_stream_check():
    live = await bot.fetch_streams(user_ids=["803300101"], type="all")
    if live:
        try:
            cur.execute(f"SELECT Live FROM Live_Info ORDER BY Entry DESC LIMIT 1")
            latest = cur.fetchone()
            cur.execute(f"SELECT Title FROM Live_Info ORDER BY Entry DESC LIMIT 1")
            latest_title = cur.fetchone()
        except Exception as e:
            print(e)
            latest = "not live"
        try:
            if str(latest[0]) == "False" and live[0].title == str(latest_title[0]):
                cur.execute(
                    f"UPDATE Live_Info SET Live = '{True}' WHERE Title = '{str(latest_title[0])}'"
                )
                con.commit()

            if str(latest[0]) == "True" and live:
                cur.execute(
                    f"UPDATE Live_Info SET Title = '{live[0].title}' WHERE Title = '{str(latest_title[0])}'"
                )
                con.commit()
                cur.execute(
                    f"UPDATE Live_Info SET Game = '{live[0].game_name}' WHERE Title = '{str(latest_title[0])}'"
                )
                con.commit()
            else:
                cur.execute(
                    f"INSERT INTO Live_Info (Live, Title, Game, Date, Noti) VALUES ('True', '{live[0].title}', '{live[0].game_name}', '{live[0].started_at}', 'False')"
                )
                con.commit()
        except Exception as e:
            print(e)
            cur.execute(
                f"INSERT INTO Live_Info (Live, Title, Game, Date, Noti) VALUES ('True', '{live[0].title}', '{live[0].game_name}', '{live[0].started_at}', 'False')"
            )
            con.commit()
    else:
        cur.execute(f"UPDATE Live_Info SET Live = '{False}' WHERE Live = 'True'")
        con.commit()


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            token="nqnxpafi1e23a43l0phvvfue0w58te",
            prefix="!",
            initial_channels=["Tatox3_"],
            nick="NeonBot",
        )

    async def event_ready(self):
        print(f"Logged in as | {self.nick}")
        print(f"User id is | {self.user_id}")
        auto_stream_check.start()

    async def event_message(self, message):
        global con
        global cur
        if con is None:
            try:
                con = pymysql.connect(
                    host="db-mfl-01.sparkedhost.us",
                    port=3306,
                    user="u109224_Krhr5CV2M2",
                    passwd="LzwM5tsReqzPH^1I1+@@XA2A",
                    database="s109224_Bot",
                )

                cur = con.cursor()
            except pymysql.OperationalError:
                print("Lost connection to the database.")
        if message.echo:
            return
        live = await bot.fetch_streams(user_ids=["803300101"], type="live")
        if live:
            if message.content == "!leaderboard" or message.content == "!rank":
                return

            if message.author.name == "fossabot" or message.author.name == "streamlabs":
                return
            else:
                cur.execute(
                    f"SELECT TwitchName FROM Economy WHERE TwitchID = {message.author.id}"
                )
                authorid = cur.fetchone()
                cur.execute(
                    f"SELECT TwitchName FROM Economy WHERE TwitchName = '{message.author.name}'"
                )
                authorname = cur.fetchone()
                cur.execute(
                    f"SELECT TwitchName FROM Activity WHERE TwitchID = {message.author.id}"
                )
                activityAuthorID = cur.fetchone()
                cur.execute(
                    f"SELECT TwitchName FROM Activity WHERE TwitchName = '{message.author.name}'"
                )
                activityAuthorName = cur.fetchone()

                # Economy unique entry
                if authorid is None and authorname is None:
                    cur.execute(
                        f"INSERT INTO Economy (TwitchName, DiscordID, Potatoes, TwitchID) VALUES ('{message.author.name}', {0}, {1}, {message.author.id})"
                    )
                    con.commit()

                # Activity unique entry
                if activityAuthorID is None and activityAuthorName is None:
                    cur.execute(
                        f"INSERT INTO Activity (TwitchName, Potatoes, TwitchID) VALUES ('{message.author.name}', {1}, {message.author.id})"
                    )
                    con.commit()

                # Economy twitchID update
                if authorid is None and authorname is not None:
                    cur.execute(
                        f"UPDATE Economy SET TwitchID = {message.author.id} WHERE TwitchName = '{message.author.name}'"
                    )
                    con.commit()

                # Economy twitch name update
                if authorid is not None and authorname is None:
                    cur.execute(
                        f"UPDATE Economy SET TwitchName = '{message.author.name}' WHERE TwitchID = {message.author.id}"
                    )
                    con.commit()

                # Activity twitch name update
                if activityAuthorID is not None and activityAuthorName is None:
                    cur.execute(
                        f"UPDATE Activity SET TwitchName = '{message.author.name}' WHERE TwitchID = {message.author.id}"
                    )
                    con.commit()

                # Economy potato addition
                if authorid is not None and authorname is not None:
                    if str(authorname[0]) != message.author.name:
                        cur.execute(
                            f"UPDATE Economy SET TwitchName = '{message.author.name}' WHERE TwitchID = {message.author.id}"
                        )
                        con.commit()
                    else:
                        cur.execute(
                            f"UPDATE Economy SET Potatoes = Potatoes + {1}, TwitchName = '{message.author.name}' WHERE TwitchID = {message.author.id}"
                        )
                        con.commit()

                # Activity potato addition
                if activityAuthorID is not None and activityAuthorName is not None:
                    if str(activityAuthorName[0]) != message.author.name:
                        cur.execute(
                            f"UPDATE Activity SET TwitchName = '{message.author.name}' WHERE TwitchID = {message.author.id}"
                        )
                        con.commit()
                    else:
                        cur.execute(
                            f"UPDATE Activity SET Potatoes = Potatoes + {1}, TwitchName = '{message.author.name}' WHERE TwitchID = {message.author.id}"
                        )
                        con.commit()

        await self.handle_commands(message)

    @commands.command()
    async def voices(self, ctx: commands.Context):
        await ctx.send(
            "The current voices you can use for !tts are (henry, kratos, mrbeast, EVW, Aeonair, npesta, doggie, vit12)"
        )

    @commands.command()
    @commands.cooldown(rate=1, per=5, bucket=commands.Bucket.channel)
    async def tts(self, ctx: commands.Context, voice, *, message):

        live = await bot.fetch_streams(user_ids=["803300101"], type="live")
        cur.execute(
            f"SELECT Potatoes FROM Economy WHERE TwitchID = {ctx.message.author.id}"
        )
        potatoes = cur.fetchone()
        if live:
            if str(voice).lower() not in [
                "henry",
                "mrbeast",
                "evw",
                "kratos",
                "aeonair",
                "npesta",
                "doggie",
                "vit12",
            ]:
                if int(potatoes[0]) >= 100:
                    cur.execute(
                        f"UPDATE Economy SET Potatoes = Potatoes - {100} WHERE TwitchID = {ctx.message.author.id}"
                    )
                    con.commit()
                    cur.execute(
                        f'INSERT INTO TTS (TwitchName, TwitchID, Message, Voice) VALUES ("{ctx.message.author.name}", {ctx.message.author.id}, "{message}", "No")'
                    )
                    con.commit()
                    cur.execute(f"SELECT * FROM TTS")
                    queue = len(cur.fetchall())
                    await ctx.send(
                        f"{ctx.message.author.mention} your message has been added to the queue (#{queue})"
                    )
                else:
                    await ctx.send(
                        f"{ctx.message.author.mention} make sure include what TTS message you want to send '!tts <voice> <message>' and that you have 100 potatoes"
                    )
            else:
                if message and int(potatoes[0]) >= 100:
                    cur.execute(
                        f"UPDATE Economy SET Potatoes = Potatoes - {100} WHERE TwitchID = {ctx.message.author.id}"
                    )
                    con.commit()
                    cur.execute(
                        f'INSERT INTO TTS (TwitchName, TwitchID, Message, Voice) VALUES ("{ctx.message.author.name}", {ctx.message.author.id}, "{message}", "{voice}")'
                    )
                    con.commit()
                    cur.execute(f"SELECT * FROM TTS")
                    queue = len(cur.fetchall())
                    await ctx.send(
                        f"{ctx.message.author.mention} your message has been added to the queue (#{queue})"
                    )
                else:
                    await ctx.send(
                        f"{ctx.message.author.mention} make sure include what TTS message you want to send '!tts <voice> <message>' and that you have 100 potatoes"
                    )
        else:
            await ctx.send("You cannot do this command while Tatox3 is offline.")

    async def event_command_error(self, ctx, error: Exception) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"{error}")
            return

    @commands.command()
    async def bal(self, ctx: commands.Context):
        cur.execute(
            f"SELECT Potatoes FROM Economy WHERE TwitchID = '{ctx.message.author.id}'"
        )
        result = cur.fetchone()
        await ctx.send(
            f"{ctx.message.author.mention}'s current potato balance is {result[0]}"
        )

    @commands.command(aliases=["lb"])
    async def leaderboard(self, ctx: commands.Context):
        cur.execute(
            f"SELECT TwitchName, Potatoes FROM Economy ORDER BY Potatoes DESC LIMIT 5"
        )
        result = cur.fetchall()
        await ctx.send(
            f"Potato Leaderboard | #1 {result[1][0]}: {result[1][1]} | #2 {result[2][0]}: {result[2][1]} | #3 {result[3][0]}: {result[3][1]} | #4 {result[4][0]}: {result[4][1]} | #5 {result[5][0]}: {result[5][1]}"
        )

    @commands.command()
    async def rank(self, ctx: commands.Context):
        count = 0
        cur.execute(f"SELECT TwitchID, Potatoes FROM Economy ORDER BY Potatoes DESC")
        result = cur.fetchall()

        for i in result:
            if i[0] == int(ctx.author.id):
                await ctx.send(
                    f"{ctx.author.mention} you are rank #{count} on the potato leaderboard with {i[1]} potatoes"
                )
            count += 1

    @commands.command(aliases=["g"])
    @commands.cooldown(rate=1, per=5, bucket=commands.Bucket.user)
    async def gamble(self, ctx: commands.Context, amount: int):
        live = await bot.fetch_streams(user_ids=["803300101"], type="live")
        if live:
            rngOdds = random.choices(population=["Win", "Lose"])
            cur.execute(
                f"SELECT Potatoes FROM Economy WHERE TwitchID = {ctx.message.author.id}"
            )
            potatoes = cur.fetchone()
            cur.execute(
                f"SELECT TwitchID FROM Gambling WHERE TwitchID = {ctx.message.author.id}"
            )
            existance = cur.fetchone()
            if int(potatoes[0]) and int(potatoes[0]) >= amount and amount > 1:
                try:
                    if existance is None:
                        cur.execute(
                            f"INSERT INTO Gambling (TwitchID, DiscordID, Gambled, AmountGambled, AmountWon, AmountLost) VALUES ({ctx.message.author.id}, {0}, {0}, {0}, {0}, {0})"
                        )
                    if int(potatoes[0]) >= amount:
                        cur.execute(
                            f"UPDATE Economy SET Potatoes = Potatoes - {amount} WHERE TwitchID = {ctx.message.author.id}"
                        )
                        con.commit()
                        cur.execute(
                            f"UPDATE Gambling SET Gambled = Gambled + {1}, AmountGambled = AmountGambled + {amount} WHERE TwitchID = {ctx.message.author.id}"
                        )
                        con.commit()
                except:
                    await ctx.send(
                        f"{ctx.message.author.mention} It seems you might have less than {amount} potatoes, check your balance and try again!"
                    )

                if rngOdds[0] == "Win":
                    payout = amount * 2
                    await ctx.send(
                        f"{ctx.message.author.mention} YOU WIN! {payout} potatoes have been added to your account."
                    )
                    cur.execute(
                        f"UPDATE Gambling SET AmountWon = AmountWon + {payout} WHERE TwitchID = {ctx.message.author.id}"
                    )
                    con.commit()
                    cur.execute(
                        f"UPDATE Economy SET Potatoes = Potatoes + {payout} WHERE TwitchID = {ctx.message.author.id}"
                    )
                    con.commit()
                else:
                    await ctx.send(
                        f"{ctx.message.author.mention} You Lost! (Womp Womp)"
                    )
                    cur.execute(
                        f"UPDATE Gambling SET AmountLost = AmountLost + {amount} WHERE TwitchID = {ctx.message.author.id}"
                    )
                    con.commit()
            else:
                await ctx.send(
                    "You must bet more than 1 potato. Or you bet more than you have."
                )
        else:
            await ctx.send("You must wait until tatox3 is online to use this.")

    async def event_command_error(self, ctx, error: Exception) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"{error}")
            return

    @commands.command()
    async def help(self, ctx: commands.Context):
        commands_msg = ""
        for command in self.commands:
            commands_msg = "{}, {}".format(commands_msg, "!{}".format(command))
        commands_msg = commands_msg[2:]
        await ctx.send(
            f"""{ctx.message.author.mention} {commands_msg} || To earn potatos (stream currency) just chat!"""
        )


bot = Bot()
bot.run()
