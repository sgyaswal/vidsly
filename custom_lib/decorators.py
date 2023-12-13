import functools
import json
# from custom_lib.request_validator import validate
from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator
import re
from custom_lib.helper import valid_serializer


def validate_request_serializer(**serializer_dt):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            req_data=None
            serializer=None
            if serializer_dt.get("request_body")and request.method in ["POST","PUT"]:
                serializer=serializer_dt.get("request_body")
                req_data=data=request.data
            if serializer_dt.get("query_serializer")and request.method=="GET":
                serializer=serializer_dt.get("query_serializer")
                req_data=data=request.GET

            if serializer:
                data=valid_serializer(serializer(data=req_data))
                if request.method in ["POST","PUT"]:
                    request._full_data =data# json.dumps(data).encode('utf-8')  
                else: 
                    request._request.GET=data
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

def camel_case_to_snake_case(str):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def swagger_auto_schema_with_serializer_validation(**kwargs):
    def inner(func):
        @swagger_auto_schema(**kwargs)
        @method_decorator(validate_request_serializer(**kwargs))
        @functools.wraps(func)  # Not required, but generally considered good practice
        def newfunc(*args, **kwargs):
            return func(*args, **kwargs)
        return newfunc
    return inner

def change_case(qSerializer):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if request.method=="GET":
                data=request.query_params
                if qSerializer:
                    data = valid_serializer(qSerializer(data=data))
                updated_dt={}
                for key,value in data.items():
                    updated_dt[camel_case_to_snake_case(key)]=value
                request._request.GET=updated_dt
            return func(request, *args, **kwargs)
        return wrapper
    return decorator




def swagger_auto_schema_with_case_change(**kwargs):
    def inner(func):
        @swagger_auto_schema(**kwargs)
        @method_decorator(change_case(kwargs.get("query_serializer","")))
        @functools.wraps(func)  # Not required, but generally considered good practice
        def newfunc(*args, **kwargs):
            return func(*args, **kwargs)
        return newfunc
    return inner

# def swagger_auto_schema_with_array_inputs_validation(**kwargs):
#     def inner(func):
#         @swagger_auto_schema(**kwargs)
#         @method_decorator(array_input_valiadtion())
#         @functools.wraps(func)  # Not required, but generally considered good practice
#         def newfunc(*args, **kwargs):
#             return func(*args, **kwargs)
#         return newfunc
#     return inner