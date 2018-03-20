import sqlite3

db = 'icedb.db'

def addFave(user,song):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute("SELECT * FROM favorite_songs WHERE user=? AND song=?",(user,song))
    if len(c.fetchall()) > 0:
        conn.close()
        return False
    else:
        c.execute("INSERT INTO favorite_songs VALUES(?,?)",(user,song))
        conn.commit()
        conn.close()
        return True

def getFaves(user):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute("SELECT song FROM favorite_songs WHERE user=?",(user,))

    retVal = c.fetchall()
    conn.close()
    return retVal

