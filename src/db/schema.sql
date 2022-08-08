CREATE TABLE IF NOT EXISTS "server_preferences" (
	"name"	TEXT,
	"value"	TEXT,
	PRIMARY KEY("name")
);
CREATE TABLE IF NOT EXISTS "member_preferences" (
	"user"	INTEGER,
	"name"	TEXT,
	"value"	TEXT
);