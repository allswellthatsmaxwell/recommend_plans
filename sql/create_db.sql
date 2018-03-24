create table members (
    member_id varchar(2) primary key
);

create table searches (
    member_id varchar(2),
    search_term varchar(100)
);

create table plans (
    plan varchar(10),
    service varchar(100)
);

create table services (
    service varchar(100),
    cost float
);

.mode csv
.separator ","
.import data/members.csv members
.import data/searches.csv searches
.import data/plans.csv plans
.import data/services.csv services
