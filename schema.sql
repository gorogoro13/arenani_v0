drop table if exists entries;
create table entries (
  id serial4 primary key ,
  title char(24) not null,
  text text not null
);