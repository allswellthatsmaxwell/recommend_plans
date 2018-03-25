create table members (
    member_id varchar(2) unique primary key
);

create table searches (
    member_id varchar(2),
    service varchar(100)
);

create table plans (
    plan varchar(10) unique primary key,
    price float
);

create table plan_coverage (
    plan varchar(10),
    service varchar(100)
);

create table services (
    service varchar(100) unique primary key,
    cost float
);
