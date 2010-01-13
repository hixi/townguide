drop table queue;
create table queue (
                 jobNo serial primary key,
                 status int,
                 title varchar(256),
		 originLat float,
		 originLon float,
                 subDate timestamp,
                 statusDate timestamp,
                 xml varchar(10000)
                 );
