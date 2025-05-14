create table players (
  id integer primary key autoincrement,
  name text not null unique,
  mu real not null default 25.0,
  sigma real not null default 8.3333333
);

create table player_days (
  id integer primary key autoincrement,
  player_id integer not null references players(id) on delete cascade,
  date text default (date('now')),
  mu real not null,
  sigma real not null,
  unique (player_id, date)
);

create table teams (
  id integer primary key autoincrement
);

create table team_players (
  id integer primary key autoincrement,
  team_id integer not null references teams(id) on delete cascade,
  player_id integer not null references players(id) on delete cascade,
  unique (team_id, player_id)
);

create table matches (
  id integer primary key autoincrement,
  datetime text default (datetime('now'))
);

create table match_teams (
  id integer primary key autoincrement,
  match_id integer not null references matches(id) on delete cascade,
  team_id integer not null references teams(id) on delete cascade,
  place integer check (place > 0), -- may be null
  score integer check (score >= 0) -- may be null
);