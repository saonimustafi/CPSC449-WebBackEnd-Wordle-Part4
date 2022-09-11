#Original Authors of this file are:Project4 Group 8-Priyansha Singh,Akshaya RK,Robin Khiv,Bhargav Navdiya
#

import redis
import uvicorn
from fastapi import FastAPI, Depends, Response, HTTPException, status


app = FastAPI()


r = redis.StrictRedis('localhost', 6379, charset="utf-8", decode_responses=True)


#flush redis cache before we start
#@app.on_event("startup")
#async def startup_event():
    #r.flushdb()


#Starting a new game. The client should supply a user ID and
#game ID when a game starts. If the user has already played the game,
#they should receive an error.
@app.post("/track")
def start_game(user_id: int, game_id: int):
    listname = str(user_id) + ":" + str(game_id)
    found = r.exists(listname)

    if found:
        raise HTTPException(status_code=403, detail="game already completed or started")
    else:
        guesses = 0
        r.rpush(listname, "started", guesses)
        return "game is ready for play"


# Updating the state of a game. When a user makes a new guess for a game,
# record the guess and update the number of guesses remaining. If a user
#tries to guess more than six times, they should receive an error.
@app.put("/track")
def update_game(user_id:int, game_id:int, guess:str):
    gameStatus = 0
    guessIDX = 1
    listname = str(user_id) + ":" + str(game_id)

    #check if game has started
    if not r.exists(listname):
        raise HTTPException(status_code=404, detail="sorry game has not started")

    status = str(r.lindex(listname, gameStatus))

    #add guess to list then update guess count and check if user made 6 guesses, if user has, we end the game
    if status == "started":
        r.rpush(listname, guess)
        numguesses = int(r.lindex(listname, guessIDX))
        numguesses = numguesses + 1
        r.lset(listname, guessIDX, numguesses)

        if numguesses == 6 :
            r.lset(listname, gameStatus, "ended")
        return {"status": "guess recorded successfully", "guessesRemaining": str(6 - numguesses)}

    else:
        raise HTTPException(status_code=403, detail="Already made 6 guesses")


#Restoring the state of a game. Upon request, the user should be able
# to retrieve an object containing the current state of a game,
#including the words guessed so far and the number of guesses remaining.
@app.get("/track")
def get_game_info(user_id:int, game_id:int):
    listname = str(user_id) + ":" + str(game_id)

    #check if game has started
    if not r.exists(listname):
        raise HTTPException(status_code=404, detail="sorry game has not started")

    list = r.lrange(listname, 0, -1)
    status = list[0]
    guessesRemaining = 6 - int(list[1])

    results = {"status": status, "guessesRemaining": guessesRemaining}

    #if user made guesses we will loop over list for guesses
    if guessesRemaining < 6:
        guesscount = 1;
        guesses = {}
        print(list, ' list')
        for x in range(2, len(list)):
            guesses.update({"guess_"+str(guesscount): list[x]})
            guesscount = guesscount + 1
        results.update({"guesses": guesses})

    return results


if __name__ == "__main__":
    uvicorn.run("track:app", host="0.0.0.0", port=5001, log_level="info")
