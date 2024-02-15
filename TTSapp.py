import pymysql
import pyttsx3


con = pymysql.connect(
    host="db-mfl-01.sparkedhost.us",
    port=3306,
    user="u109224_Krhr5CV2M2",
    passwd="LzwM5tsReqzPH^1I1+@@XA2A",
    database="s109224_Bot",
)

cur = con.cursor()


###
engine = pyttsx3.init()
engine.setProperty("rate", 100)


def main():
    cur.execute(f"SELECT Message, id FROM TTS ORDER BY id ASC")
    queue = cur.fetchone()

    if queue:
        engine.say(queue[0])
        engine.runAndWait()
        cur.execute(f"DELETE FROM TTS WHERE id = {queue[1]}")
        con.commit()

    else:
        pass


main()
