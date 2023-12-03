from django.conf import settings
from datetime import datetime
from django.utils import timezone
from drf_yasg import openapi
import re
from datetime import datetime,timedelta
import json
import base64
import requests


BASE_RESPONSE = {
    "errorMessage": "Success",
    "errorCode": 0,
    "data": []
}

def get_now_time():
    return datetime.now(tz=timezone.utc)


def valid_serializer(serializer):
    if serializer.is_valid():
        return serializer.data
    for x, y in serializer.errors.items():
        error = str(x)+' : '+str(y)
        raise Exception(error)


# def convert_column_name_to_camelcase(data, cols=[], return_df=False):
#     import pandas as pd
#     df = pd.DataFrame(list(data), columns=cols)
#     if df.empty:
#         return data
#     cols = df.columns
#     rename = {}
#     for col in cols:
#         rename[col] = ''.join(x if i == 0 else x.capitalize()
#                               for i, x in enumerate(col.split('_')))
#     df = df.rename(columns=rename)
#     if return_df:
#         return df
#     return df.to_dict('records')


def convert_columns_to_camelcase(cols=[]):
    if not cols:
        return {}
    rename = {}
    for col in cols:
        rename[col] = ''.join(x if i == 0 else x.capitalize()
                              for i, x in enumerate(col.split('_')))
    return rename


def camel_case_to_snake_case(str):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def create_swagger_params(name, required=True, type='string',header_type="header",extra={}):
    swagger_type = openapi.TYPE_STRING
    header = openapi.IN_HEADER
    if type == "int":
        swagger_type = openapi.TYPE_INTEGER
    elif type == "bool":
        swagger_type = openapi.TYPE_BOOLEAN
    
    if header_type=="query":
        header=openapi.IN_QUERY
    return openapi.Parameter(name, header, type=swagger_type, required=required,**extra)

def dict_fetch_all(cursor):
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]


from multiprocessing import Process
def run_process_parallel(*fns):
    proc=[]
    for fn in fns:
        p = Process(target=fn["func"],args=fn["args"])
        p.start()
        proc.append(p)
    for p in proc:
        p.join()


def date_converter(date):
    today = datetime.today()
    date=str(date).replace(" ","").lower()
    value = int(re.search(r'\d+', date).group())
    unit = re.search(r'[A-Za-z]+', date).group()

    if unit == 's':
        calculated_date = today - timedelta(seconds=value)
    elif unit == 'm':
        calculated_date = today - timedelta(minutes=value)
    elif unit == 'h':
        calculated_date = today - timedelta(hours=value)
    elif unit == 'd':
        calculated_date = today - timedelta(days=value)
    elif unit == 'w':
        calculated_date = today - timedelta(weeks=value)
    elif unit == 'mo':
        calculated_date = today - timedelta(days=value*30)
    elif unit == 'y':
        calculated_date = today - timedelta(days=value*365)
    else:
        calculated_date = None

    return calculated_date.date()