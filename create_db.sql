create table members (
    member_id varchar(2) primary key
);

create table searches (
    member_id varchar(2),
    search_term varchar(100)
);

create table plans (
    plan_name varchar(10),
    service varchar(100),
    covered varchar(1) default 'N'
);

create table services (
    service varchar(100),
    cost float
);

.import members.csv members