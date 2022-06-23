create table orders(
    contract_number char(10) not null
    references contract(c_number)
    constraint "isValid"
                   check ( contract_number like 'CSE%' and length((contract_number)::text) = 10),
    product_m varchar(80),
    quantity integer not null
    constraint "quantity>0"
                   check ( quantity>0 ),
    estimated_d date default null,
    lodgement_d date default null,
    salemans_id int not null
        references staff(number),
    order_type char(8) not null
    check (order_type='Finished' or order_type='UnFinish')
);

select * from product where cur_num!=0;
create table staff(
    number int
        constraint "number is valid?"
            check ( 10000000<=number and number<=99999999)
    primary key ,
    name varchar(25) not null,
    gender varchar(6) not null
        constraint "gender is valid?"
                     check ( lower(gender)like 'male' or lower(gender)like 'female'),
    age int not null
        constraint "age is valid?"
            check ( 0<age ),
    mobile_phone char(15) not null unique,
    supply_center varchar(50) not null
    references supply_center(center),
    type varchar(25) not null
);

--新建表contract，表示合同编号
create table contract(
    c_number char(10)
    primary key,
    contract_manger int
    references staff(number),
    client_enterprise varchar(80) not null
    references enterprise(en_name),
    create_date date not null,
    contract_type char(10) not null
    check (contract_type='Finished' or contract_type='UnFinish')
);

create table enterprise(
    en_name varchar(80)
    primary key ,
    country varchar(30) not null,
    city varchar(20),
    industry varchar(50) not null,
    supply_center varchar(50) not null
    references supply_center(center)
);

create table supply_center(
    center varchar(50)
    primary key,
    id int
);

create table product(
    model varchar(80),
    code char(7) not null ,
    name varchar(80) not null ,
    unit_price int
                    constraint "price>0?"
                    check ( unit_price>0 ),
    cur_num int default 0
                    constraint "cur_num>=0?"
                    check ( cur_num>=0 ),
    supply_center varchar(50) not null
    references supply_center(center),
    primary key (model,supply_center)
);


create table sale_detail(
    model varchar(80) primary key,
    volume int,
    saleroom bigint default 0,
    cost bigint default 0,
    profit bigint default 0
);

drop table supply_center;
drop table enterprise;
drop table contract;
drop table staff;
drop table product;
drop table orders;
drop table sale_detail;

create index product_index on product using btree(model);
create index staff_index on staff using btree(type);
create index order_index on orders using btree(contract_number,salemans_id);
create index sale_detail_index on sale_detail using btree(volume);
create index contract_index on contract using  btree(c_number);


