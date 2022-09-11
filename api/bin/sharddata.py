#!/usr/bin/env python3

import contextlib
import datetime
import random
import sqlite3
import uuid

print('Sharding DB from previous single db')

USERSCHEMA = "./share/user.sql"
GAMESCHEMA = "./share/game.sql"
SINGLEDB = "./var/stats.db"
USERDB = "./var/user.db"
GAMEDB1 = "./var/game1.db"
GAMEDB2 = "./var/game2.db"
GAMEDB3 = "./var/game3.db"

#Create game db for each shard
with contextlib.closing(sqlite3.connect(GAMEDB1)) as db:
    with open(GAMESCHEMA) as f:
        db.executescript(f.read())
        db.commit()

with contextlib.closing(sqlite3.connect(GAMEDB2)) as db:
    with open(GAMESCHEMA) as f:
        db.executescript(f.read())
        db.commit()

with contextlib.closing(sqlite3.connect(GAMEDB3)) as db:
    with open(GAMESCHEMA) as f:
        db.executescript(f.read())
        db.commit()

# create user db then loop through full db. insert uuid to new user db
# then compare that user_id in game and insert games into correct shard by shard id
with contextlib.closing(sqlite3.connect(USERDB)) as db:
    with open(USERSCHEMA) as f:
        db.executescript(f.read())
        db.commit()

    con = sqlite3.connect(SINGLEDB)
    cur = con.execute("select * from users;")
    query = cur.fetchall()

    #loop through each user and insert to new user db with uuid. Then grab that user_id from the user db and find the games played and split then according to uuid
    for row in query:
        try:
            uid = uuid.uuid4()
            db.execute("INSERT INTO users(user_id, username, uuid) VALUES(?, ?, ?);", [int(row[0]), str(row[1]), str(uid)])

            shardID = int(uid) % 3

            game = con.execute("SELECT * from games WHERE user_id = ?;", [int(row[0])])
            gamequery = game.fetchall()

            if shardID == 0:
                con1 = sqlite3.connect(GAMEDB1)
                for row1 in gamequery:
                    con1.execute("INSERT INTO games(user_id, game_id, finished, guesses, won, uuid) VALUES(?,?,?,?,?,?);",[int(row[0]),int(row1[1]), str(row1[2]), int(row1[3]), int(row1[4]), str(uid)])
                con1.commit()

            elif shardID == 1:
                con1 = sqlite3.connect(GAMEDB2)

                for row1 in gamequery:
                    con1.execute("INSERT INTO games(user_id, game_id, finished, guesses, won, uuid) VALUES(?,?,?,?,?,?);",[int(row[0]),int(row1[1]), str(row1[2]), int(row1[3]), int(row1[4]), str(uid)])
                con1.commit()

            else:
                con1 = sqlite3.connect(GAMEDB3)

                for row1 in gamequery:
                    con1.execute("INSERT INTO games(user_id, game_id, finished, guesses, won, uuid)  VALUES(?,?,?,?,?,?);",[int(row[0]),int(row1[1]), str(row1[2]), int(row1[3]), int(row1[4]), str(uid)])
                con1.commit()

        except sqlite3.IntegrityError:
                continue

    db.commit()
