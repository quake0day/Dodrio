DROP TABLE IF EXISTS entries;
CREATE TABLE entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type INTEGER NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    confname TEXT NOT NULL,
    urlpaper TEXT,
    urlslides TEXT,
    urlcite TEXT,
    cite INTEGER NOT NULL,
    place INTEGER NOT NULL,
    year INTEGER NOT NULL,
    text TEXT,
    video TEXT,
    cluster TEXT,
    urlpdf TEXT
);