DROP TABLE IF EXISTS text;
DROP TABLE IF EXISTS keyphrase;

CREATE TABLE text (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  content TEXT NOT NULL
);

CREATE TABLE keyphrase (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  text_id INTEGER NOT NULL,
  keyphrase TEXT NOT NULL,
  wiki_url TEXT,
  is_exists BOOL,
  is_disambiguation BOOL,
  FOREIGN KEY (text_id) REFERENCES text (id)
);