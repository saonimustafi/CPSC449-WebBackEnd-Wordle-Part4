#!/bin/sh

sqlite3 ./var/user.db < ./share/usershard.sql
sqlite3 ./var/game1.db < ./share/game1shard.sql
sqlite3 ./var/game2.db < ./share/game2shard.sql
sqlite3 ./var/game3.db < ./share/game3shard.sql
sqlite3 ./var/answers.db < ./share/answers.sql
sqlite3 ./var/words.db < ./share/words.sql

