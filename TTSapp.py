import pymysql
import pyttsx3

engine = pyttsx3.init()
engine.say("Testing to see if this works")
engine.runAndWait()

con = pymysql.connect(
    host="db-mfl-01.sparkedhost.us",
    port=3306,
    user="u109224_Krhr5CV2M2",
    passwd="LzwM5tsReqzPH^1I1+@@XA2A",
    database="s109224_Bot",
)

cur = con.cursor()


###


def main():
    cur.execute(f"SELECT * FROM TTS ORDER BY id ASC")
    queue = cur.fetchall()

    if queue:
        print(queue)
        print(queue[0])
        print(queue[0][-2])
