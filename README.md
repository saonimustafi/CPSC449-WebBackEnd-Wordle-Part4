# 449-p5

Note - The authors for Project 5 and Group 16 are - Priyansha Singh, Saoni Mustafi, Anant Jain and Shameer Sheikh. The services used from the previous projects were authored by - Priyansha Singh, Akshaya, Robin Khiv.

POSTing a username to the /game/new endpoint should:
1. Find the user ID for the specified username
2. Choose a new game ID for the user to play

Here, we are calling the 'game/getuserid' and retrieving the user id of the user name being passed in the '/game/new'. We are also generating a game id randomly using the random.randint() function. We then call the '/track/' endpoint and pass the user id and game id as parameters. The response received is then analyzed to find what the status code is. If the status code is 403, it means that the user has already played the game. Else, it returns the user id, game id and the status.

Changes to existing services to accomplish this service:

We added a new 'game/getuserid' endpoint in project 3 to retrieve the id of the user name that we are passing as a parameter to the '/game/new' endpoint in Project 5. We had to add this, as we did not have this service available in the previous projects and we could not use redis or SQLite3 connections in this project. We added this endpoint in the 'statsFromShardedDB.py' file. 

Verify that the guess is a word allowed by the dictionary - 

This service takes a guess from the user and verifies if it is a valid dictionary word. For this, the service calls the '/validate/guess' endpoint with the 'guess' parameter to validate this guess entered by the user. If it is a valid dictionary word, it sets the 'successflag' to True else it sets the flag to False. The service then returns this flag.

Check that the user has guesses remaining -

This service takes the user id, game_id, and the guess from the user and checks if the user has any more guesses remaining for this game id. It calls the '/track' endpoint with user id, game id and the guess as parameters and checks for the 'guessesRemaining' in the response returned by this endpoint. If the 'guessesRemaining' is >= 0 and <6,it sets the 'successFlag' to True, else it remains False. This flag is then returned by the service.

Endpoint to play the game:

This service runs 'validateresponse' and 'checkremainingguess' and if both are true, it calls the '/track' endpoint with parameters user id, game id and the guess, records it, and updates the 'guessesRemaining' for this game id and user. 
It then calls '/compare' endpoint and passes the guess as a query parameter. It then checks the 'WrongPosition' and 'wrong' keys and if they are null, the service records a win by updating the '/stats/' service. The user id, game id, guesses, and win - set to True, are sent as parameters to this sevice. The '/stats/user' service is then used for this user id to return the user score for this game and the current user statistics.
If the guess is incorrect and the number of guesses 'guessesRemaining' < 6, the user is allowed to continue guessing.

If the guess is incorrect and no other guesses remain for the user for the game id, it updates the stats of the user by calling the '/stats/' service with the user id, game id, guesses - set to 6, and win - set to False, as parameters. The user score is then displayed by calling the '/stats/user' service for this user id which shows the 'gamestatus' for the game id as 'loss' and the current game statistics.

If validateresponse - is False, it displays the message as 'not a valid word in the dictionary'.

If 'checkremainingguess' is False, it displays the message as 'Sorry!You dont have any guesses left for the game'.  


-------------------------------------------------------------

##services urls:
validate-http://localhost:8001/docs
Description-to validate word in dictionary

compare-http://localhost:8000/docs
Description-to compare word with actual guess

track-http://localhost:5001/docs
Description-to keep track of guesses made

stats-http://localhost:6003/docs
Description-to update and get games stats

gameService-http://localhost:5003/docs
Description-actual service to be called by client to play word game

## To start Microservices
Go inside the api folder and use the below command to run the Fastapi services

foreman start
  
## Directions to create sharded databases for games and users db.
You can use the already present sharded databases in the var folder or choose from one option below to create:

Option 1:</br>
  
  first create the single database supplied by Professor Kenytt Avery <br/>
  by running the python script in
  
  ```./bin/stats.py```</br>
  
  then shard that single database into 4 (1 users database and 3 games database) </br>
  with the python script in 
  
  ```./bin/sharddata.py```</br>
  
Option 2:</br>
  
  Run the sql dump files to create the databases </br>
  
  ```./bin/init.sh```</br>

## Directions to create answers and word databases.
You can use the already present answer and word databases in the var folder or run the below shellscript to create databases:
  
  Run the sql dump files to create the databases </br>
  
  ```./bin/init.sh```</br>
  
Note:if permission denied error comes when running init.sh file then give permissions to file by going inside bin folder and running below command
 chmod 777 init.sh
 then come out of bin folder and run command 2 again
 
 ##About Project Files Authors
 validate.py-Original Authors of this file are: Project1 Group 22-Priyansha Singh,Akshaya RK,Robin Khiv
 
 compare.py-Original Authors of this file are: Project2 Group 22-Priyansha Singh,Akshaya RK,Robin Khiv
 
 track.py-Original Authors of this file are: Project3 Group 8-Priyansha Singh,Akshaya RK,Robin Khiv,Bhargav Navdiya
 
 statsFromShardedDB.py-Original Authors of this file are: Project4 Group 8-Priyansha Singh,Akshaya RK,Robin Khiv,Bhargav Navdiya
 new end point added in this file for project 5 by Saoni Mustafi
 
 gameService.py-Original Authors of this file are: Project5 Group 16-Priyansha Singh,Saoni Mustafi,Anant Jain,Shameer Sheikh
