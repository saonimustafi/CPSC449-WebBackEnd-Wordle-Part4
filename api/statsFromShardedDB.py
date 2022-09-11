#Original Authors of this file are:Project3 Group 8-Priyansha Singh,Akshaya RK,Robin Khiv,Bhargav Navdiya
#
#


import contextlib
import logging.config
import sqlite3
import uuid

import uvicorn
from fastapi import FastAPI, Depends, Response, HTTPException, status
from pydantic import BaseSettings, BaseModel


class Settings(BaseSettings):
    shard1: str
    shard2: str
    shard3: str
    shard4: str
    logging_config: str

    class Config:
        env_file = ".env"


def get_shard1():
    with contextlib.closing(sqlite3.connect(settings.shard1)) as db:
        db.row_factory = sqlite3.Row
        yield db


def get_shard2():
    with contextlib.closing(sqlite3.connect(settings.shard2)) as db:
        db.row_factory = sqlite3.Row
        yield db


def get_shard3():
    with contextlib.closing(sqlite3.connect(settings.shard3)) as db:
        db.row_factory = sqlite3.Row
        yield db


def get_shard4():
    with contextlib.closing(sqlite3.connect(settings.shard4)) as db:
        db.row_factory = sqlite3.Row
        yield db


def get_logger():
    return logging.getLogger(__name__)


settings = Settings()
# Uncomment below line to test without traefik
app = FastAPI()
logging.info(app.docs_url)
# Uncomment below line to test with traefik
# app = FastAPI(root_path="/api/v1")

logging.config.fileConfig(settings.logging_config)

def get_user_uuid(id:int, db:sqlite3.Connection):
    try:
        cur = db.execute("SELECT * from users WHERE user_id = ? LIMIT 1;", [int(id)])
        query = cur.fetchall()
        for row in query:
            return str(row[2])
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": type(e).__name__, "msg": str(e)},
        )


# common function to get records based on user wins
def get_top10WinRecords(db: sqlite3.Connection):
    try:
        cur = db.execute("select user_id,wins from wins limit 10")
        rows = cur.fetchall()
        dicts = {}

        for row in rows:
            dicts[row["user_id"]] = row["wins"]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"information not available"}
        )
    return dicts


# get top10 records for user wins from shard1
def get_top10usersFromShard(db: sqlite3.Connection):
    return get_top10WinRecords(db)


def check_for_game(game: int, id: int, db: sqlite3.Connection):
    try:
        cur = db.execute("select exists(SELECT * from games WHERE user_id = ? AND game_id = ? LIMIT 1);", (id, game))
        query = cur.fetchone()[0]
        return query
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": type(e).__name__, "msg": str(e)},
        )


# common function to get records based on user streaks
def get_top10StreakRecords(db: sqlite3.Connection):
    try:
        cur = db.execute("select user_id,streak from streaks order by streak desc LIMIT 10")
        rows = cur.fetchall()
        dicts = {}

        for row in rows:
            dicts[row["user_id"]] = row["streak"]
    except Exception as e:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"information not available"}
        )
    return dicts


# get top10 records for streaks from shard1
def get_top10streaksFromShard(
        db: sqlite3.Connection
):
    return get_top10StreakRecords(db)


# get streak data by id
def get_streaks(id: int, db: sqlite3.Connection):
    try:
        maxStreak = 0
        currentStreak = 0
        cur = db.execute("select * from streaks where user_id = ?", [int(id)])
        query = cur.fetchall()
        dict = {}
        for row in query:
            if maxStreak < int(row[1]):
                maxStreak = int(row[1])
            currentStreak = int(row[1])
        dict.update({"currentStreak": currentStreak, "maxStreak": maxStreak})
        return dict
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": type(e).__name__, "msg": str(e)},
        )


#get guesses stats by id
def get_guesses(user_id:int, db: sqlite3.Connection):
    try:
        cur = db.execute("SELECT * from games WHERE user_id = ? ORDER by games.game_id", [user_id])
        query = cur.fetchall()
        dict = {}
        guesses = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
        wins = 0
        loses = 0
        winPercentage = 0
        gamesPlayed = 0
        i = 1
        for row in query:
            if int(row[4]) == 0:
                loses = loses + 1
            else:
                wins = wins + 1
                guesses[int(row[3])] = guesses[int(row[3])] + 1
                i  = i + 1
            gamesPlayed = gamesPlayed + 1
        winPercentage = int(float(wins/gamesPlayed) * 100)
        guesses.update({"fail": loses})
        dict.update({"guesses": guesses, "winPercentage": winPercentage,"gamesPlayed": gamesPlayed})
        return dict
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": type(e).__name__, "msg": str(e)},
        )


#function to combine streak with guesses
def get_stats(user_id: int, db: sqlite3.Connection):
    results = {}
    streak = get_streaks(user_id, db)
    guesses = get_guesses(user_id, db)
    results.update(streak)
    results.update(guesses)
    return results


# post game results to db
def post_game_service(win:bool, guesses: int, user_id: int, game_id:int, db: sqlite3.Connection):
    try:
        cur = db.execute("INSERT into games (user_id, game_id, guesses, won) VALUES (?, ?, ?,?);",(user_id, game_id,guesses,win))
        db.commit()
        return
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": type(e).__name__, "msg": str(e)},
        )


#function to decide whether game_id exists or we need to create a new one
def post_game(game_id:int, user_id:int, win: bool, guesses: int, db: sqlite3.Connection):
    if check_for_game(game_id, user_id, db):
        update_game_service(win, guesses, user_id, game_id, db)
    else:
        post_game_service(win, guesses, user_id, game_id, db)


# function to  update an exisiting game result
def update_game_service(win:bool, guesses: int, user_id:int, game_id:int, db: sqlite3.Connection):
    try:
        cur = db.execute("UPDATE games SET guesses = ?, won = ? WHERE user_id = ? AND game_id = ?;", (guesses,win,user_id,game_id))
        db.commit()
        return
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": type(e).__name__, "msg": str(e)},
        )


#Posting a win or loss for a particular game, along with a timestamp and number of guesses
@app.post("/stats/")
def post_stats_by_userid(win: bool, guesses: int, user_id: int, game_id: int, userdb: sqlite3.Connection = Depends(get_shard4),
gamedb1: sqlite3.Connection = Depends(get_shard1), gamedb2: sqlite3.Connection = Depends(get_shard2), gamedb3: sqlite3.Connection = Depends(get_shard3)):
    uid = get_user_uuid(user_id, userdb)
    shardID = int(uuid.UUID(uid)) % 3

    if shardID == 0:
        post_game(game_id, user_id, win, guesses, gamedb1)
    elif shardID == 1:
        post_game(game_id, user_id, win, guesses, gamedb2)
    else:
        post_game(game_id, user_id, win, guesses, gamedb3)
    return "game posted";


# get top10 records for user wins from all the sharded databases,combine the records
# then get the final top 10 users by number of wins from the combined records
@app.get("/stats/top10wins")
def get_top10users(db1: sqlite3.Connection = Depends(get_shard1), db2: sqlite3.Connection = Depends(get_shard2),
                   db3: sqlite3.Connection = Depends(get_shard3)):
    logging.info("inside first instance-getting top10wins")
    combined_records = {}
    combined_records.update(get_top10usersFromShard(db1))
    combined_records.update(get_top10usersFromShard(db2))
    combined_records.update(get_top10usersFromShard(db3))

    sorted_dict = sorted(combined_records.items(), key=lambda x: x[1], reverse=True)
    win_list = []
    top10_initial_dict = {}
    top10_final_dict = {}
    top10_initial_dict.update(sorted_dict)
    for key, val in top10_initial_dict.items():
        win_list.append([key, val])
    for x in range(0, 10):
        top10_final_dict[x] = win_list[x].__getitem__(0)
    return {"Top 10 users by number of wins are": top10_final_dict}



# get top10 records for streaks from all the sharded databases,combine the records
# then get the final top 10 users by streaks from the combined records
@app.get("/stats/top10streaks")
def get_top10streaks(
        db1: sqlite3.Connection = Depends(get_shard1), db2: sqlite3.Connection = Depends(get_shard2),
        db3: sqlite3.Connection = Depends(get_shard3)
):
    logging.info("inside first instance-getting top10streaks")
    combined_records = {}
    combined_records.update(get_top10streaksFromShard(db1))
    combined_records.update(get_top10streaksFromShard(db2))
    combined_records.update(get_top10streaksFromShard(db3))
    sorted_dict = sorted(combined_records.items(), key=lambda x: x[1], reverse=True)
    streaks_list = []
    top10_initial_dict = {}
    top10_final_dict = {}
    top10_initial_dict.update(sorted_dict)
    for key, val in top10_initial_dict.items():
        streaks_list.append([key, val])
    for x in range(0, 10):
        top10_final_dict[x] = streaks_list[x].__getitem__(0)
    return {"Top 10 users by longest streak are": top10_final_dict}


#retrieve data for player stats
@app.get("/stats/user")
def retrieve_stats(user_id: int, response: Response, userdb: sqlite3.Connection = Depends(get_shard4),
gamedb1: sqlite3.Connection = Depends(get_shard1), gamedb2: sqlite3.Connection = Depends(get_shard2), gamedb3: sqlite3.Connection = Depends(get_shard3)):
    results = {}
    uid = get_user_uuid(user_id, userdb)
    shardID = int(uuid.UUID(uid)) % 3

    if shardID == 0:
        data = get_stats(user_id, gamedb1)
    elif shardID == 1:
        data = get_stats(user_id, gamedb2)
    else:
        data = get_stats(user_id, gamedb3)
    return data;

#newly added code by Author Project 5 Group16 Saoni Mustafi
@app.get("/game/getuserid")
def get_name(user_name: str, userdb: sqlite3.Connection = Depends(get_shard4),
gamedb1: sqlite3.Connection = Depends(get_shard1), gamedb2: sqlite3.Connection = Depends(get_shard2), gamedb3: sqlite3.Connection = Depends(get_shard3)):
    cur = userdb.execute("select user_id from users where username = ? ;",[user_name])
    query = cur.fetchone()[0]
    return {"user_id": query}

if __name__ == "__main__":
    uvicorn.run("statsFromShardedDB:app", host="0.0.0.0", port=6003, log_level="info")
