from django.shortcuts import render
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import io
import datetime


database_engine = create_engine(
    'postgresql+psycopg2://' + 'postgres' + ':' + 'wyh638' + '@localhost' + ':' + str(5432) + '/' + 'Project2')


def write_to_table(df, table_name, flag):
    # 链接数据库
    db_engine = create_engine(
        'postgresql+psycopg2://' + 'postgres' + ':' + 'wyh638' + '@localhost' + ':' + str(5432) + '/' + 'Project2')
    string_data_io = io.StringIO()

    # 先将DataFrame转化为csv格式
    df.to_csv(string_data_io, sep='|', index=False)
    # 通过pandas的sql_bulider将数据转化为sql中的table的形式
    pd_sql_engine = pd.io.sql.pandasSQL_builder(db_engine)
    table = pd.io.sql.SQLTable(table_name, pd_sql_engine, frame=df,
                               index=False, if_exists=flag, schema='public')
    table.create()
    string_data_io.seek(0)

    # 通过sql的COPY命令将table复制到数据库中
    with db_engine.connect() as connection:
        with connection.connection.cursor() as cursor:
            copy_cmd = "COPY public.%s FROM STDIN HEADER DELIMITER '|' CSV" % table_name
            cursor.copy_expert(copy_cmd, string_data_io)
        connection.connection.commit()

#
order_fresh=pd.read_sql("select * from orders where order_type is not null",con=database_engine)
order_fresh['lodgement_d']=pd.to_datetime(order_fresh['lodgement_d'],format='%Y/%m/%d')
cur_time= datetime.date.today()
cur_time=np.datetime64(cur_time)
print('go!!!!!')
for i in range(len(order_fresh)):
        if order_fresh.iloc[i]['lodgement_d']<=cur_time:
            order_fresh.loc[i,'order_type']='Finished'
        else:
            order_fresh.loc[i,'order_type']='UnFinish'
write_to_table(order_fresh,'orders','replace')



def access_sourceData(filename, funcType, addlist, deleteIndex, deleteFlag, deleteJudge,
                      updateFlag, updateJudge, updateCol, updateData, selectFlag, selectJudge):
    curFile = pd.read_csv('C:\\Users\\WYH\\django_test\\'+filename, encoding='utf-8')
    if (funcType == 'add'):
        #curFile = curFile.append(addlist, ignore_index=True)
        curFile.loc[len(curFile.index)]=addlist
        print(curFile)
    elif (funcType == 'delete'):

        if (deleteFlag != None):
            curFile.drop(curFile[curFile[deleteFlag] == deleteJudge].index, inplace=True)
        else:
            curFile.drop(deleteIndex-1,axis=0,inplace=True)
    elif (funcType == 'update'):
        curFile.loc[curFile[updateFlag] == updateJudge, updateCol] = updateData
    elif (funcType == 'select'):
        if (isinstance(selectFlag, list)):
            temp = curFile[(curFile[selectFlag[0]] == selectJudge[0]) & (curFile[selectFlag[1]] == selectJudge[1])]
        else:
            temp = curFile[(curFile[selectFlag] == selectJudge)]
        print(temp)
    else:
        print('invalid access')
    curFile.to_csv('C:\\Users\\WYH\\django_test\\'+filename, index=False)


def place_order(ori_data):
    for i in range(len(ori_data)):
        model = ori_data.iloc[i]['model']
        supply_center = ori_data.iloc[i]['supply_center']
        judge = pd.read_sql(
            "select model,cur_num,supply_center,unit_price from product where model='" + model + "' and supply_center='" +
            supply_center + "'", con=database_engine)
        t1 = judge['cur_num'].values[0]
        t3 = judge['unit_price'].values[0]
        t2 = ori_data.iloc[i]['quantity']
        if ((t1 >= t2)):
            pd.read_sql("update product set cur_num=cur_num-" + str(
                ori_data.iloc[i]['quantity']) + " where model='" + model +
                        "' and supply_center='" + supply_center + "'", con=database_engine, chunksize=1000)
            pd.read_sql("update sale_detail set volume=volume+" + str(ori_data.iloc[i]['quantity']) +
                        " where model='" + model + "'", con=database_engine, chunksize=1000)
            pd.read_sql("update sale_detail set saleroom=saleroom+(" + str(ori_data.iloc[i]['quantity'])+
                        "*"+str(t3) +") where model='" + model + "'", con=database_engine, chunksize=1000)
            pd.read_sql("update sale_detail set profit=(saleroom-cost) where model='" + model + "'", con=database_engine, chunksize=1000)
            ori_data.iloc[i, 12] = 1
    ori_data = ori_data[ori_data['flag'] == 1]
    ori_data.reset_index(drop=True, inplace=True)
    temp_type = ['UnFinish'] * len(ori_data)
    temp_type = pd.DataFrame(temp_type, columns=['order_type'])
    ori_data = pd.concat([ori_data, temp_type], axis=1)
    cur_time = datetime.date.today()
    cur_time = np.datetime64(cur_time)

    for i in range(len(ori_data)):
        if ori_data.iloc[i]['lodgement_date'] <= cur_time:
            ori_data.loc[i, 'order_type'] = 'Finished'
    return ori_data


def login(request):
    return render(request, 'test.html')


def API0(request):
    data_ent = pd.read_csv("C:\\Users\\WYH\\django_test\\enterprise.csv", encoding='utf-8')
    data_center = pd.read_csv("C:\\Users\\WYH\\django_test\\center.csv", encoding='utf-8')
    data_model = pd.read_csv("C:\\Users\\WYH\\django_test\\model.csv", encoding='utf-8')
    data_staff = pd.read_csv("C:\\Users\\WYH\\django_test\\staff.csv", encoding='utf-8')
    header = ['name', 'id']
    center = data_center[header]
    write_to_table(center, 'supply_center', 'append')

    header = ['model', 'number', 'name', 'unit_price', 'cur_num', 'supply_center']
    center = data_center
    center.insert(2, 'cur_num', [0, 0, 0, 0, 0, 0, 0, 0])
    center.rename(columns={'name': 'supply_center'}, inplace=True)

    model = pd.merge(data_model, center, how='cross', on=None)
    model = model[header]
    write_to_table(model, 'product', 'append')

    model = model.drop_duplicates(subset=['model'], keep='first')
    model = model.reset_index()[['model', 'cur_num']]
    temp = np.zeros(len(model)).reshape(len(model), -1)
    temp = pd.DataFrame(temp, columns=['saleroom']).astype(int)
    model = pd.concat([model, temp], axis=1)
    temp = np.zeros(len(model)).reshape(len(model), -1)
    temp = pd.DataFrame(temp, columns=['cost']).astype(int)
    model = pd.concat([model, temp], axis=1)
    temp = np.zeros(len(model)).reshape(len(model), -1)
    temp = pd.DataFrame(temp, columns=['profit']).astype(int)
    model = pd.concat([model, temp], axis=1)
    write_to_table(model, 'sale_detail', 'append')

    header = ['name', 'country', 'city', 'industry', 'supply_center']
    enterprise = data_ent[header]
    write_to_table(enterprise, 'enterprise', 'append')

    header = ['number', 'name', 'gender', 'age', 'mobile_number', 'supply_center', 'type']
    staff = data_staff[header]
    write_to_table(staff, 'staff', 'append')
    return render(request, 'API0.html')


def API1(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        #print(name)
        # access_sourceData('center.csv', 'update', None, None, None, None, 'id', 1, ['id', 'name'],
        #                   [10, 'america'], None, None)
        # access_sourceData('center.csv', 'update', None, None, None, None, 'id', 10, ['id', 'name'],
        #                   [1, 'America'], None, None)
        # access_sourceData('center.csv', 'add', ['9','SUST'], None, None, None, None, None, None,
        #                   None, None, None)
        # access_sourceData('center.csv', 'delete',None, 9, None, None, None, None, None,
        #                   None, None, None)
        # access_sourceData('center.csv', 'select', None, None, None, None, None, None, None,
        #                   None, 'id', 8)
        access_sourceData('enterprise.csv', 'select', None, None, None, None, None, None, None,
                          None, ['name','country'], ['Alcatel','France'])
    return render(request, 'API1.html')


def API2(request):
    model_judge = pd.read_sql("select distinct model from product", con=database_engine)
    staff_judge = pd.read_sql("select number,supply_center,type from staff where type='Supply Staff'",
                              con=database_engine)
    origin_data = pd.read_csv('C:\\Users\\WYH\\django_test\\in_stoke_test.csv', encoding='utf-8')
    origin_data.rename(columns={'product_model': 'model', 'supply_staff': 'number'}, inplace=True)
    temp_data = origin_data.copy()
    temp_data = temp_data.groupby(['model', 'supply_center'])['quantity'].sum()
    origin_data = origin_data.drop_duplicates(subset=['supply_center', 'model'], keep='first')
    origin_data = pd.merge(origin_data[['supply_center', 'model', 'number']], temp_data, on=['supply_center', 'model'])
    result = pd.merge(origin_data, model_judge, on='model')
    result = pd.merge(result, staff_judge, on=['number', 'supply_center'])

    change_table = pd.read_sql("select * from product", con=database_engine)
    change_table = pd.merge(change_table, result[['model', 'supply_center', 'quantity', ]],
                            on=['model', 'supply_center'], how='left')
    change_table = change_table.fillna(0)
    change_table['cur_num'] += change_table['quantity']
    change_table.drop('quantity', axis=1, inplace=True)
    change_table['cur_num'] = change_table['cur_num'].astype(int)
    change_table
    write_to_table(change_table, 'product', 'replace')


##去掉非法数据，改写sale_detail中商品对应成本的值
    origin_data = pd.read_csv('C:\\Users\\WYH\\django_test\\in_stoke_test.csv', encoding='utf-8')
    origin_data.rename(columns={'product_model': 'model', 'supply_staff': 'number'}, inplace=True)
    result = pd.merge(origin_data, model_judge, on='model')
    result = pd.merge(result, staff_judge, on=['number', 'supply_center'])
    for i in range(len(result)):
        model = result.iloc[i]['model']
        in_price = result.iloc[i]['purchase_price']
        quantity = result.iloc[i]['quantity']
        pd.read_sql("update sale_detail set cost=cost+" + str(in_price * quantity) + " where model='" + model + "'",
                    con=database_engine, chunksize=1000)
        pd.read_sql("update sale_detail set profit=(-cost) where model='"+model+"'",con=database_engine,chunksize=1000)
    return render(request, 'API2.html')


def API3(request):
    model_judge = pd.read_sql("select model,cur_num,supply_center from product", con=database_engine)
    staff_judge = pd.read_sql("select number,supply_center from staff where type='Salesman'", con=database_engine)
    origin_data = pd.read_csv('C:\\Users\\WYH\\django_test\\task2_test_data_final_public.tsv', sep='\t',
                              encoding='utf-8')
    origin_data.rename(
        columns={'salesman_num': 'number', 'product_model': 'model', ' lodgement_date': 'lodgement_date'}, inplace=True)

    origin_data = origin_data.join(staff_judge.set_index('number'), on='number')
    origin_data.dropna(inplace=True)
    origin_data = origin_data.join(model_judge.set_index(['model', 'supply_center']), on=['model', 'supply_center'])
    origin_data.dropna(inplace=True)
    origin_data = origin_data[origin_data['quantity'] <= origin_data['cur_num']]
    origin_data['contract_date'] = pd.to_datetime(origin_data['contract_date'], format='%Y/%m/%d')
    origin_data['estimated_delivery_date'] = pd.to_datetime(origin_data['estimated_delivery_date'], format='%Y/%m/%d')
    origin_data['lodgement_date'] = pd.to_datetime(origin_data['lodgement_date'], format='%Y/%m/%d')
    origin_data.sort_values(by=['contract_date'], kind='mergesort', ascending=True, inplace=True)
    origin_data.reset_index(drop=True, inplace=True)
    temp = np.zeros(len(origin_data)).reshape(len(origin_data), -1)
    temp = pd.DataFrame(temp, columns=['flag'])
    origin_data = pd.concat([origin_data, temp], axis=1)
    origin_data = place_order(origin_data)

    order_data = origin_data[
        ['contract_num', 'model', 'quantity', 'estimated_delivery_date', 'lodgement_date', 'number','order_type']].copy()
    contract_data = origin_data[
        ['contract_num', 'contract_manager', 'enterprise', 'contract_date', 'contract_type']].copy()

    contract_data['contract_date'] = pd.to_datetime(contract_data['contract_date'], format='%Y/%m/%d')
    contract_data = contract_data.drop_duplicates(subset=['contract_num'], keep='first')

    write_to_table(contract_data, 'contract', 'append')
    write_to_table(order_data, 'orders', 'append')
    return render(request, 'API3.html')


def API4(request):
    order_judge = pd.read_sql("select * from orders", con=database_engine)
    order_judge['salemans_id'] = order_judge['salemans_id'].astype(int)
    staff_judge = pd.read_sql("select number,supply_center from staff where type ='Salesman'", con=database_engine)

    update_order = pd.read_csv('C:\\Users\\WYH\\django_test\\update_final_test.tsv', sep='\t', encoding='utf-8')
    update_order.rename(
        columns={"contract": "contract_number", "salesman": "salemans_id", "product_model": "product_m"}, inplace=True)

    order_judge = order_judge.join(update_order.set_index(['contract_number', 'salemans_id', 'product_m']),
                                   on=['contract_number', 'salemans_id', 'product_m'], lsuffix='_x', rsuffix='_y')
    order_judge.dropna(inplace=True)
    order_judge.rename(columns={'salemans_id': 'number'}, inplace=True)
    order_judge = order_judge.join(staff_judge.set_index('number'), on='number')
    order_judge.dropna(inplace=True)

    for i in range(len(order_judge)):
        update_q = int(order_judge.iloc[i]['quantity_y'])
        old_q = int(order_judge.iloc[i]['quantity_x'])
        contract_number = order_judge.iloc[i]['contract_number']
        product_m = order_judge.iloc[i]['product_m']
        salemans_id = order_judge.iloc[i]['number']
        supply_center = order_judge.iloc[i]['supply_center']
        es_date = order_judge.iloc[i]['estimate_delivery_date']
        ld_date = order_judge.iloc[i]['lodgement_date']
        temp = pd.read_sql("select cur_num,unit_price from product where model='" + product_m + "' and supply_center='"
                           + supply_center + "'", con=database_engine)
        cur_num = temp['cur_num'].values[0]
        unit_price=temp['unit_price'].values[0]

        if (update_q == 0):
            pd.read_sql("delete from orders where contract_number='" + contract_number + "' and product_m='"
                        + product_m + "' and salemans_id ='" + str(salemans_id) + "'", con=database_engine,
                        chunksize=1000)
            pd.read_sql("update product set cur_num=cur_num+" + str(
                old_q) + " where model='" + product_m + "' and supply_center='"
                        + supply_center + "'", con=database_engine, chunksize=1000)
            pd.read_sql("update sale_detail set volume=volume-" + str(old_q) +
                        " where model='" + product_m + "'", con=database_engine, chunksize=1000)
            pd.read_sql("update sale_detail set profit=profit-"+str(old_q*unit_price)+
                        " where model='" + product_m + "'", con = database_engine, chunksize = 1000)
        elif ((update_q - old_q) <= cur_num):
            pd.read_sql("update orders set quantity=" + str(
                update_q) + " where contract_number='" + contract_number + "' and product_m='"
                        + product_m + "' and salemans_id ='" + str(salemans_id) + "'", con=database_engine,
                        chunksize=1000)
            if (update_q >= old_q):
                pd.read_sql("update product set cur_num=cur_num-" + str(
                    (update_q - old_q)) + " where model='" + product_m + "' and supply_center='"
                            + supply_center + "'", con=database_engine, chunksize=1000)
                pd.read_sql("update sale_detail set volume=volume+" + str((update_q - old_q)) +
                            " where model='" + product_m + "'", con=database_engine, chunksize=1000)
                pd.read_sql("update sale_detail set profit=profit+" + str((update_q-old_q) * unit_price) +
                            " where model='" + product_m + "'", con=database_engine, chunksize=1000)
            else:
                pd.read_sql("update product set cur_num=cur_num+" + str(
                    (old_q - update_q)) + " where model='" + product_m + "' and supply_center='"
                            + supply_center + "'", con=database_engine, chunksize=1000)
                pd.read_sql("update sale_detail set volume=volume-" + str((update_q - old_q)) +
                            " where model='" + product_m + "'", con=database_engine, chunksize=1000)
                pd.read_sql("update sale_detail set profit=profit-" + str((old_q-update_q) * unit_price) +
                            " where model='" + product_m + "'", con=database_engine, chunksize=1000)
            pd.read_sql("update orders set estimated_d=('" + str(
                es_date) + "'::date) where contract_number='" + contract_number + "' and product_m='"
                        + product_m + "' and salemans_id ='" + str(salemans_id) + "'", con=database_engine,
                        chunksize=1000)
            pd.read_sql("update orders set lodgement_d=('" + str(
                ld_date) + "'::date) where contract_number='" + contract_number + "' and product_m='"
                        + product_m + "' and salemans_id ='" + str(salemans_id) + "'", con=database_engine,
                        chunksize=1000)

    return render(request, 'API4.html')


def API5(request):
    order_judge_d = pd.read_sql("select * from orders", con=database_engine)
    order_judge_d['salemans_id'] = order_judge_d['salemans_id'].astype(int)
    order_judge_d['quantity'] = order_judge_d['quantity'].astype(float)
    order_judge_d['quantity'] = order_judge_d['quantity'].astype(int)
    delete_data = pd.read_csv("C:\\Users\\WYH\\django_test\\delete_final.csv", encoding='utf-8')
    delete_data.rename(columns={"salesman": "salemans_id", "contract": "contract_number"}, inplace=True)

    order_judge_d = pd.merge(order_judge_d, delete_data, on=['contract_number', 'salemans_id'])
    for i in range(len(order_judge_d)):
        seq = order_judge_d.iloc[i]['seq']
        contract_number = order_judge_d.iloc[i]['contract_number']
        salemans_id = order_judge_d.iloc[i]['salemans_id']
        orders_d = pd.read_sql("select * from orders where contract_number='" + contract_number + "' and salemans_id='"
                               + str(salemans_id) + "'", con=database_engine)
        orders_d['salemans_id'] = orders_d['salemans_id'].astype(int)
        orders_d['quantity'] = orders_d['quantity'].astype(float)
        orders_d['quantity'] = orders_d['quantity'].astype(int)
        if (seq <= len(orders_d)):
            orders_d = orders_d.sort_values(by=['estimated_d', 'product_m'])
            product_m = orders_d.iloc[seq - 1]['product_m']
            quantity = orders_d.iloc[seq - 1]['quantity']
            supply = pd.read_sql("select supply_center from staff where number='" + str(salemans_id) + "'",
                                 con=database_engine)
            supply_center = supply['supply_center'].values[0]
            price = pd.read_sql("select unit_price from product where model='"+product_m+"'",con=database_engine)
            price=price['unit_price'].values[0]

            pd.read_sql("delete from orders where contract_number='" + contract_number + "' and product_m='"
                        + product_m + "' and salemans_id ='" + str(salemans_id) + "'", con=database_engine,
                        chunksize=1000)
            pd.read_sql("update product set cur_num=cur_num+" + str(
                quantity) + " where model='" + product_m + "' and supply_center='"
                        + supply_center + "'", con=database_engine, chunksize=1000)
            pd.read_sql("update sale_detail set volume=volume-" + str(quantity) +
                        " where model='" + product_m + "'", con=database_engine, chunksize=1000)
            pd.read_sql("update sale_detail set profit=profit-" + str(quantity*price) +
                        " where model='" + product_m + "'", con=database_engine, chunksize=1000)
    return render(request, 'API5.html')


def api6():
    staff = pd.read_sql("select * from staff", con=database_engine)
    staff = staff.groupby('type')['type'].count()
    staff = staff.rename({'Contracts Manager': 'CM', 'Supply Staff': 'SS'})
    staff = staff.to_dict()
    return staff


def API6(request):
    staff = api6()
    return render(request, 'API6.html', staff)


def api7():
    count = pd.read_sql("select count(*) from contract", con=database_engine)
    count = (count['count'].values[0])
    count = {'count7': count}
    return count


def API7(request):
    count7 = api7()
    return render(request, 'API7.html', count7)


def api8():
    count = pd.read_sql("select count(*) from orders", con=database_engine)
    count = (count['count'].values[0])
    count = {'count8': count}

    return count


def API8(request):
    count8 = api8()
    return render(request, 'API8.html', count8)


def api9():
    product_nosale = pd.read_sql("select * from sale_detail where volume=0",
                                 con=database_engine)
    product_cur = pd.read_sql("select model,cur_num from product", con=database_engine)
    product_cur = product_cur.groupby('model')['cur_num'].sum()
    product_cur = product_cur[product_cur != 0]
    product_cur.reset_index()
    product_cur = pd.merge(product_cur, product_nosale, on=['model'])
    cou = len(product_cur)
    cou = {'cou': cou}
    return cou


def API9(request):
    cou = api9()
    return render(request, 'API9.html', cou)


def api10():
    max_sale = pd.read_sql("select model,volume from sale_detail where volume=(select max(volume) from sale_detail)",
                           con=database_engine)
    max_sale = max_sale.iloc[0, :]
    max_sale = max_sale.to_dict()
    return max_sale


def API10(request):
    max_sale = api10()
    return render(request, 'API10.html', max_sale)


def api11():
    model_groupby_supply = pd.read_sql("select model,cur_num,supply_center from product",
                                       con=database_engine)
    mySum = model_groupby_supply.groupby('supply_center')['cur_num'].sum()
    model_groupby_supply = model_groupby_supply[model_groupby_supply['cur_num'] != 0]
    myCount = model_groupby_supply.groupby('supply_center')['supply_center'].count()
    res = mySum / myCount
    res = res.round(decimals=1)
    res = res.rename({'Hong Kong, Macao and Taiwan regions of China': 'HMTRC', 'Northern China': 'NC',
                      'Southern China': 'SC', 'Southwestern China': 'SWC', 'Eastern China': 'EC'})
    res = res.to_dict()
    return res


def API11(request):
    res = api11()
    return render(request, 'API11.html', res)


def api12(name):
    model_num = name
    model_groupby_number = pd.read_sql("select model,code,cur_num,supply_center from product where cur_num!=0 "
                                       + "and code='" + model_num + "'", con=database_engine)
    model_groupby_number = model_groupby_number.groupby(['supply_center', 'model'])['cur_num'].sum()
    model_groupby_number = model_groupby_number.to_dict()
    return model_groupby_number


def API12(request):
    global model_groupby_number
    if request.method == 'POST':
        name = request.POST.get('name12')
        model_groupby_number = api12(name)
    return render(request, 'API12.html', {'model_groupby_number': model_groupby_number})


def api13(name):
    contract = name
    contract_num = pd.read_sql(
        "select c_number,client_enterprise as enterprise,contract_manger as number from contract" +
        " where c_number='" + contract + "'", con=database_engine)
    staff = pd.read_sql("select number,name,supply_center from staff", con=database_engine)
    contract_num = pd.merge(contract_num, staff, on=['number'])
    contract_num = contract_num[['c_number', 'enterprise', 'name', 'supply_center']]
    contract_num.rename(columns={'c_number': 'contract_number', 'name': 'manager'}, inplace=True)
    contract_num = {'contract_number': contract_num['contract_number'][0],
                    'enterprise': contract_num['enterprise'][0], 'manager': contract_num['manager'][0],
                    'supply_center': contract_num['supply_center'][0]}

    contract_detail = pd.read_sql(
        "select distinct product_m,staff.name,quantity,unit_price,estimated_d as estimate_delivery_date,lodgement_d as lodgement_date from orders" +
        " join staff on(orders.salemans_id::text=staff.number::text) join product on(product_m=model) where contract_number='" + contract + "'",
        con=database_engine)
    contract_detail.rename(columns={'product_m': 'product_model', 'name': 'salesman'}, inplace=True)
    con_final = {}
    for i in range(len(contract_detail)):
        con_final[str(i)] = contract_detail.iloc[i].values
    return [contract_num, con_final]


def API13(request):
    if request.method == 'POST':
        name = request.POST.get('name13')
        contract = api13(name)

        return render(request, 'API13.html', {'contract_num': contract[0], 'con_final': contract[1]})


def outputAPI(request):
    if request.method == 'POST':
        name = request.POST.get('name14')
        name1=str.split(name)[0]
        name2 = str.split(name)[1]
        a6 = api6()
        a7 = api7()
        a8 = api8()
        a9 = api9()
        a10 = api10()
        a11 = api11()
        a12 = api12(name1)
        a13 = api13(name2)
        return render(request, 'API.html', {'staff': a6, 'count7': a7['count7'], 'count8': a8['count8'], 'cou': a9['cou'], 'max_sale': a10, 'res': a11,
                                        'model_groupby_number': a12, 'contract_num': a13[0], 'con_final': a13[1]})
