import sqlite3

con = sqlite3.connect('YOUR_PATH.DB', check_same_thread=True)

c = con.cursor()

# c.execute("""CREATE TABLE users(
#     userid text,
#     username text,
#     address text,
#     balance real
#     )""")

# c.execute("INSERT INTO users VALUES ('Test','Test', '0')")

# c.execute("SELECT * FROM users")


def createWallet(raw, username, address, balance):
    c.execute("INSERT INTO users VALUES (?, ?, ?, ?)",
              (str(raw), str(username), str(address), str(balance)))
    con.commit()


c.execute("SELECT * FROM users")
# print(c.fetchall())

con.commit()
# con.close()
