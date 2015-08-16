DROP TABLE IF EXISTS users;

CREATE TABLE users (
	user_id INTEGER PRIMARY KEY,
	screen_name TEXT NOT NULL,
	favs_given INTEGER DEFAULT 0,
	favs_received INTEGER DEFAULT 0,
	rts_given INTEGER DEFAULT 0,
	rts_received INTEGER DEFAULT 0,
	mentions_given INTEGER DEFAULT 0,
	mentions_received INTEGER DEFAULT 0,
	quotes_received INTEGER DEFAULT 0,
	tweets_seen INTEGER DEFAULT 0
);

-- TODO
--DROP TABLE IF EXISTS username_history;
--
--CREATE TABLE username_history (
--	user_id INTEGER,
--	src_name TEXT,
--	dest_name TEXT
--);
-- END TODO

DROP TABLE IF EXISTS meta;

CREATE TABLE meta (
	schema_ver INTEGER,
	last_event_date TEXT,
	last_event_num INTEGER
);

INSERT INTO meta (schema_ver, last_event_date, last_event_num) VALUES (1, NULL, NULL);

