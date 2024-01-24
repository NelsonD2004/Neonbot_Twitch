from twitchio.ext import commands
from twitchio.ext import routines
import pymysql

con = pymysql.connect(
    host="db-mfl-01.sparkedhost.us",
    port=3306,
    user="u109224_Krhr5CV2M2",
    passwd="LzwM5tsReqzPH^1I1+@@XA2A",
    database="s109224_Bot",
)

cur = con.cursor()


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
                    f"UPDATE Live_Info SET Title = '{live[0].title}' WHERE Date = '{live[0].started_at}'"
                )
                con.commit()
                cur.execute(
                    f"UPDATE Live_Info SET Game = '{live[0].game_name}' WHERE Date = '{live[0].started_at}'"
                )
                con.commit()
            else:
                cur.execute(
                    f"INSERT INTO Live_Info (Live, Title, Game, Date, Noti) VALUES ('True', '{live[0].title}', '{live[0].game_name}', '{live[0].started_at}', 'False')"
                )
                con.commit()
        except:
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
        if message.echo:
            return
        live = await bot.fetch_streams(user_ids=["803300101"], type="live")
        if live:
            if message.author.name == "fossabot":
                return

            if message.content == "!leaderboard" or message.content == "!rank":
                pass
            else:
                cur.execute(
                    f"SELECT TwitchName FROM Economy WHERE TwitchName = '{message.author.name}'"
                )
                result = cur.fetchone()

                if result is None:
                    cur.execute(
                        f"INSERT INTO Economy (TwitchName, DiscordID, Potatoes) VALUES ('{message.author.name}', {0}, {1})"
                    )
                    con.commit()
                else:
                    cur.execute(
                        f"UPDATE Economy SET Potatoes = Potatoes + {1} WHERE TwitchName = '{message.author.name}'"
                    )
                    con.commit()

        print(message.author.id)

        await self.handle_commands(message)

    @commands.command()
    @commands.cooldown(rate=1, per=90, bucket=commands.Bucket.channel)
    async def whiff(self, ctx: commands.Context):
        live = await bot.fetch_streams(user_ids=["803300101"], type="live")
        if live:
            point = cur.execute("SELECT Amount FROM Whiff")
            result = point.fetchone()
            await ctx.send(f"Henry has been caught whiffing {result[0]} times!")

            cur.execute(f"UPDATE Whiff SET Amount = Amount + {1}")
            con.commit()
        else:
            await ctx.send("You cannot run this command while henry is offline!")

    async def event_command_error(self, ctx, error: Exception) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("Command is on cooldown!")

    @commands.command()
    async def bal(self, ctx: commands.Context):
        cur.execute(
            f"SELECT Potatoes FROM Economy WHERE TwitchName = '{ctx.message.author.name}'"
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
            f"""Potato Leaderboard | #1 {result[0][0]}: {result[0][1]} | #2 {result[1][0]}: {result[1][1]} | #3 {result[2][0]}: {result[2][1]} | #4 {result[3][0]}: {result[3][1]} | #5 {result[4][0]}: {result[4][1]}"""
        )

    @commands.command()
    async def rank(self, ctx: commands.Context):
        count = 0
        cur.execute(f"SELECT TwitchName, Potatoes FROM Economy ORDER BY Potatoes DESC")
        result = cur.fetchall()

        for i in result:
            count += 1
            if i[0] == ctx.author.name:
                await ctx.send(
                    f"{ctx.author.mention} you are rank #{count} on the potato leaderboard with {i[1]} potatoes"
                )

    @commands.command()
    async def help(self, ctx: commands.Context):
        commands_msg = ""
        for command in self.commands:
            commands_msg = "{}, {}".format(commands_msg, "!{}".format(command))
        commands_msg = commands_msg[2:]
        # await twitchio.User.send_whisper(self.user_id, token="oauth:wmufa00luq1684j03f4w6t3pywcsgd", user_id=ctx.author.id, message="Hello!")
        await ctx.send(
            f"""{ctx.message.author.mention} {commands_msg} || To earn potatos (stream currency) just chat!"""
        )


bot = Bot()
bot.run()
