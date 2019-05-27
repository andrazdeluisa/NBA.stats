-- Shema za NBA.stats bazo

CREATE TABLE IF NOT EXISTS uporabnik (
  username TEXT PRIMARY KEY,
  password TEXT NOT NULL,
  ime TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS trac (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  avtor TEXT NOT NULL REFERENCES uporabnik (username),
  cas INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
  vsebina TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS komentar (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  vsebina TEXT NOT NULL,
  trac INTEGER NOT NULL REFERENCES trac (id),
  avtor TEXT NOT NULL REFERENCES uporabnik (username),
  cas INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
);
