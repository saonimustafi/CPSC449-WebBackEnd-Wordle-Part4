PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS users;

CREATE TABLE users(
    user_id INTEGER PRIMARY KEY,
    username VARCHAR UNIQUE,
    uuid VARCHAR UNIQUE
);


PRAGMA analysis_limit=1000;
PRAGMA optimize;
