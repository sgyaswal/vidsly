import requests
import json
from django.conf import settings
def api_call(**kwrgs):
    try:
        reqArgs = {}
        url = kwrgs["url"]
        if "data" in kwrgs:
            reqArgs["json"] = kwrgs["data"]
        if "params" in kwrgs:
            reqArgs['params']=kwrgs['params']
        if "headers" in kwrgs:
            reqArgs["headers"] = kwrgs["headers"]
            reqArgs["headers"]['Cache-Control']='no-cache'
        r = getattr(requests, kwrgs["type"].lower())(url, **reqArgs)
        
        if r.status_code == 500:
            raise Exception("Internal server error",500)
        elif not r.text:
            raise Exception("Unknown error occured")
        elif (
            kwrgs["type"].upper() == "GET" or kwrgs["type"].upper() == "PATCH"
        ) and r.status_code not in [200,201]:
            raise Exception(r.text)
        elif kwrgs["type"].upper() == "POST" and (r.status_code == 204):
            return {"success": True, "data": {}}
        elif kwrgs["type"].upper() == "POST" and (
            r.status_code > 203 or r.status_code < 200
        ):
            raise Exception(r.text)
        elif kwrgs["type"].upper() == "DELETE" and (r.status_code == 204):
            return {"success": True, "data": {}}
        responsedata = json.loads(r.text)
        
        
        if "responseCode" in responsedata:
            if responsedata.get("responseCode")==0:
                responsedata=responsedata.get("responseData")
            else:
                raise Exception(responsedata.get("message"),responsedata.get("responseCode"))
        elif "errorCode" in responsedata:
            if responsedata.get("errorCode")==0:
                responsedata=responsedata.get("data")
            else:
                raise Exception(responsedata.get("errorMessage",responsedata.get("message")),responsedata.get("errorCode"))
        elif "statusCode" in responsedata:
            if responsedata.get("statusCode")==0:
                responsedata=responsedata.get("data")
            else:
                raise Exception(responsedata.get("message"),responsedata.get("statusCode"))
        return {"success": True, "data": responsedata}
    except Exception as e:
        return {"success": False, "error":str(e)}

