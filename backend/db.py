import sqlite3

con = sqlite3.connect("gun-detection.db", check_same_thread=False)
cur = con.cursor()

def init():
    cur.execute("CREATE TABLE IF NOT EXISTS detection_source (id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT)")
    con.commit()
    
def create():
    cur.execute("INSERT INTO detection_source (source) VALUES ('123')")
    con.commit()
    cur.execute("SELECT id FROM detection_source WHERE id=" + str(cur.lastrowid))
    model = cur.fetchone()
    return str(model[0])
