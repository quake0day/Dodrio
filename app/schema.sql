drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  type integer not null,
  title text not null,
  author text not null,
  confname text not null,
  urlpaper text,
  urlslides text,
  urlcite text,
  cite integer not null,
  place integer not null,
  year integer not null,
  text text
);