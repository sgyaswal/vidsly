import json
from custom_lib.helper import camel_case_to_snake_case
import re
from datetime import datetime #used in eval

def validate_dict(data_dict, schema):
    required = schema.get("required", [])
    length = schema.get("length", {})
    enum = schema.get("enum", {})
    regex = schema.get("regex", {})
    to_return = {}
    required_done = set()
    for key in data_dict.keys():
        dt = data_dict[key]
        req_done = set()
        if dt==None:
            continue
        if type(dt) == dict:
            req_done, dt = validate_dict(dt, schema)
        elif type(dt) == list:
            req_done, dt = validate_list(dt, schema)
        else:
            if key in required and not str(dt).strip():
                raise Exception(f"Provide non-empty value {key}")
            if key in length and ( len(dt)) > length[key]:
                raise Exception(f"Invalid length of {key}")
            if key in enum and dt not in enum[key]:
                raise Exception(
                    f"Invalid values for {key}.Accepted values- {','.join(enum[key])} ")
            if key in regex and not re.search(regex[key],dt):
                raise Exception(
                    f"Invalid values for {key}.Accepted values- {','.join(enum[key])} ")
        req_done.add(key)
        required_done.update(req_done)
        to_return[camel_case_to_snake_case(key)] = dt
    return required_done, to_return


def validate_list(lis,schema):
    to_return=[]
    required_done=set()
    for li in lis:
        if type(li)==dict:
            required_done,dt = validate_dict(li,schema)
            to_return.append(dt)
    return required_done,to_return


import re
list_valid={
    "datetime.strptime":"([2][0-9]{3}(-[0-9]{1,2}){2}),([2][0-9]{3}(-[0-9]{1,2}){2})",
    "str":"[a-zA-Z]+",
    "int":"-?[0-9]+"
}
def input_list_field_converter(field='',value="['']",formatter="str"):
    try:
        if not list_valid.get(formatter):
            raise Exception()
        inputs=re.findall(re.compile(list_valid.get(formatter)),value)
        if not inputs:
            raise Exception('1a')
        if formatter.count("date")>0:
            if len(inputs[0])!=4:
                raise Exception() 
            return [inputs[0][0],inputs[0][2]]
        return inputs
    except:
        raise Exception(f"please provide '{field}' in valid format")


def field_validator(checks={},field="",userInput=[]):
    if not isinstance(userInput,list):
        userInput = [userInput]
    formatter = checks.get("formatter","")
    format = checks.get("format","")
    min = checks.get("min","")
    max = checks.get("max","")
    choices = checks.get("choices","")
    minStrLen = checks.get("minLen","")
    try:
        if formatter == "datetime.strptime":
            userInput = list(map(eval(formatter), userInput,[format]*len(userInput)))
        elif formatter == "int"or  formatter == "str":
            userInput = list(map(eval(formatter), userInput))
    except:
        raise Exception(f"please provide '{field}' in valid {format}")
    userInput.sort()
    if not userInput:
        raise Exception(f"please provide at least one value for '{field}' ")
    elif choices:
        if userInput[0] not in choices:
            raise Exception(f"please provide a valid choice: {choices}")
    elif minStrLen:
        if  minStrLen > len(userInput[0]):
            raise Exception(f"please provide minimum {minStrLen} characters in '{field}'")
    elif "__" in field and len(userInput) !=2:
        raise Exception(f"please provide exact two values for '{field}'")
    elif min != "" and max != "" and (userInput[0] < min or userInput[-1] > max):
        raise Exception(f"please provide '{field}' in range: {min,max}")
    elif min != "" and userInput[0] < min:
        raise Exception(f"please provide '{field}' greater than equal to: {min}")
    elif max != "" and userInput[-1] > max:
        raise Exception(f"please provide '{field}' less than equal to: {max}")
    elif "__" in field :
        userInput = {"gte":userInput[0],"lte":userInput[1]}
    
    return userInput[0] if checks.get("type")!="list" and "__" not in field else userInput

