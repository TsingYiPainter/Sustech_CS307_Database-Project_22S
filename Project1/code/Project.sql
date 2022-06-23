--新建表orders，表示SUST公司的订单
create table orders(
    orders_number serial--设置自增
    primary key,
    contract_number char(10) not null
    references contract(c_number)
    constraint "isValid"
                   check ( contract_number like 'CSE%' and length((contract_number)::text) = 10),
    product_m varchar(80) not null
    references product(model),
    quantity integer not null
    constraint "quantity>0"
                   check ( quantity>0 ),
    estimated_d date default null,
    lodgement_d date default null,
    salemans_id int not null
        references salesman(number)
    check (lodgement_d is null or lodgement_d<='2022-03-02'::date)
);

--新建表contract，表示合同编号
create table contract(
    c_number char(10)
    primary key,
    client_enterprise varchar(80) not null
    references enterprise(en_name),
    supply_center varchar(30) not null
    references supply_center(center),
    create_date date not null
);

create table enterprise(
    en_name varchar(80)
    primary key ,
    country varchar(30) not null,
    city varchar(20),
    industry varchar(50) not null
);

create table supply_center(
    center varchar(30)
    primary key ,
    director varchar(20) not null unique
);

create table product(
    model varchar(80)
    primary key ,
    code char(7) not null ,
    name varchar(80) not null ,
    unit_price int
                    constraint "price>0?"
                    check ( unit_price>0 )

);

create table salesman(
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
    mobile_phone char(15) not null unique
);

delete from orders;
TRUNCATE orders RESTART IDENTITY;
delete from contract;
delete from enterprise;
delete from product;
delete from salesman;
delete from supply_center;

select * from orders where quantity=480 and estimated_d>('2022-01-01'::date);
select max(quantity) from orders group by (salemans_id);
select salemans_id,max(quantity) from orders group by (salemans_id);
select contract_number,product_m,p.name,p.code,s.name from orders join product p on orders.product_m=p.model join salesman s on orders.salemans_id = s.number;
update orders set quantity =quantity*2 where contract_number='CSE0004999';
update orders set product_m='PhotoBox60' where orders_number=50000;
select * from orders where orders_number>50000;
delete from orders where contract_number='CSE0004999';
insert into orders values ('CSE0004999','TvBaseR1',1,('2022-01-01'::date),('2022-01-01'::date),11211429);

SELECT SETVAL((SELECT pg_get_serial_sequence('public.orders', 'orders_number')),50001, false);

insert into orders values(50000,'CSE0004999','TvBaseR1',1,('2022-01-01'::date),('2022-01-01'::date),11211429);
insert into orders values(50001,'CSE0004999','TvBaseR1',1,('2022-01-01'::date),('2022-01-01'::date),11211429);
insert into orders values(50002,'CSE0004999','TvBaseR1',1,('2022-01-01'::date),('2022-01-01'::date),11211429);
insert into orders values(50003,'CSE0004999','TvBaseR1',1,('2022-01-01'::date),('2022-01-01'::date),11211429);
delete from orders where  orders_number=50003;
delete from orders where  orders_number=50002;
delete from orders where  orders_number=50001;
select * from orders where quantity=1;
delete from orders where quantity=1;


explain analyse
    select * from orders
where orders_number>1101000;

create index orders_index on orders using btree(orders_number);
explain analyse
    select * from orders
where orders_number>11101000;
drop index orders_index;

create index orders_index2 on orders using btree(orders_number,quantity);
explain analyse select * from orders where orders_number>11101000 and quantity>400;
explain analyse select * from orders where orders_number>11101000 or quantity>400;
explain analyse select * from orders where orders_number>11101000;
explain analyse select * from orders where quantity>400;
drop index orders_index2;

create index orders_index3 on orders using btree(orders_number);
create index orders_index4 on orders using btree(quantity);
explain analyse select * from orders where orders_number>11101000 and quantity>400;
explain analyse select * from orders where orders_number>11101000 or quantity>400;
explain analyse select * from orders where orders_number>11101000;
explain analyse select * from orders where quantity>400;