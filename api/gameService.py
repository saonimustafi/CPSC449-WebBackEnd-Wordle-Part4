# Original Authors of this file are:Project5 Group 16-Priyansha Singh,Saoni Mustafi,Anant Jain,Shameer Sheikh
#
#
import json

import uvicorn
from fastapi import FastAPI, Depends, Response, HTTPException, status
import httpx
import requests
import asyncio
from pydantic import BaseSettings
import random

app = FastAPI()


class Settings(BaseSettings):
    validateapiurl: str
    checkingapiurl: str
    trackguessapiurl: str
    gamestatsapiurl: str
    postgamestatusapiurl: str
    logging_config: str

    class Config:
        env_file = ".env"


# 1 Verify that the guess is a word allowed by the dictionary
async def validateguess(guess: str):
    async with httpx.AsyncClient() as client:
        valparams = {'word': guess}
        response = await client.post("http://localhost:8001/validate/guess", params=valparams)
        print(response)
        successflag = False
        if response.text.__contains__("isValidWord"):
            successflag = True
        return successflag


# 2 Check that the user has guesses remaining
async def checkremainingguess(user_id: int, game_id: int, guess: str):
    async with httpx.AsyncClient() as client:
        reqparams = {'user_id': user_id, 'game_id': game_id, 'guess': guess}
        response = await client.get("http://localhost:5001/track", params=reqparams)
        print(response)
        successflag = False
        if response.text.__contains__("guessesRemaining"):
            guesses = (response.json()["guessesRemaining"])
            if (guesses > 0 and guesses <= 6):
                successflag = True
        return successflag


# end point to play word game
@app.post("/game/{game_id}")
def play_wordgame(guess: str, user_id: int, game_id: int):
    validateresponse = asyncio.run(validateguess(guess))
    checkguessresponse = asyncio.run(checkremainingguess(user_id, game_id, guess))
    if (validateresponse and checkguessresponse):
        # 3 Record the guess and update the number of guesses remaining
        reqparams = {'user_id': user_id, 'game_id': game_id, 'guess': guess}
        r = httpx.put("http://localhost:5001/track", params=reqparams)
        print(r.json())
        remainingguesses = r.json()["guessesRemaining"]
        # 4 check to see if the guess is correct
        r = httpx.post("http://localhost:8000/compare/?word=" + guess)
        # if guess is correct
        if (r.json()["WrongPosition"] == "" and r.json()["wrong"] == ""):
            # record win
            params = {'user_id': user_id, 'game_id': game_id, 'guesses': 6 - int(remainingguesses) + 1, 'win': True}
            r = httpx.post("http://localhost:6003/stats/", params=params)
            # return user score
            params = {'user_id': user_id}
            r = httpx.get("http://localhost:6003/stats/user", params=params)
            print(r.json())
            return {'gamestatus': 'won', 'userstatistics': r.json()}
        # if guess is incorrect and additional guesses remaining
        elif (int(remainingguesses) > 0 and int(remainingguesses) <= 6):
            print("continue guessing")
            print(remainingguesses)
            print(r.json())
            return {'guessstatus': 'incorrect', 'results': r.json()}
        # if guess is incorrect and no additional guess remains
        else:
            # record loss
            params = {'win': False, 'guesses': 6, 'user_id': user_id, 'game_id': game_id}
            r = httpx.post("http://localhost:6003/stats/", params=params)
            print(r.text)
            # return user score
            params = {'user_id': user_id}
            r = httpx.get("http://localhost:6003/stats/user", params=params)
            print(r.json())
            return {'gamestatus': 'loss', 'userstatistics': r.json()}
    elif (not validateresponse):
        return "not a valid word in the dictionary"
    else:
        return "Sorry!You dont have any guesses left for the game"


# end point to generate and start a new game
@app.post("/game/new/", status_code=status.HTTP_201_CREATED)
async def new_game(user_name: str):
    async with httpx.AsyncClient() as client:
        game_id = random.randint(0, 250000000)
        print(game_id)
        user_id_response = await client.get("http://localhost:6003/game/getuserid?user_name=" + user_name)

        if user_id_response.text.__contains__("user_id"):
            user_id = user_id_response.json()['user_id']
            print(user_id)
            params = {'user_id': user_id, 'game_id': game_id}
            print(params)
            response = await client.post(
                "http://www.localhost:5001/track", params=params)

            if response.text.__contains__("status"):
                status = (response.json()["status"])
                if status == 403:
                    return {"message": "game already completed or started"}
            else:
                return {"status": "new", "user_id": user_id, "game_id": game_id}
        else:
            return {"user details not found"}


if __name__ == "__main__":
    uvicorn.run("gameService:app", host="0.0.0.0", port=5003, log_level="info")
