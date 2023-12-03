import json
from loguru import logger
from django.conf import settings

from custom_lib.helper import get_client_ip, get_now_time

class BaseLog:
    def __init__(self):
        pass
    
    def print(self,log,level="info"):
        log_str=" "+str(log)
        try:
            getattr(logger,level)(log_str)
        except:
            logger.info(log_str)
            

class Log(BaseLog):
    def __init__(self,request,app_name,class_name):
        logger.add("logs/app_logs.log", rotation="00:00", retention=f"{settings.LOG_DELETION} days")
        data={}
        if request:
            method=request.method
            if method=="POST":
                data=request.body.decode("utf-8") 
            elif method=="GET":
                data=request.META.get("QUERY_STRING")
            hostName=request.META.get("HTTP_HOST")
            ipAddress=get_client_ip(request)
            port=request.META.get("SERVER_PORT")
            urlPath = request.path
        else:
            hostName=''
            ipAddress=''
            port=''
            method=''
            urlPath=''
        self.data={
            "methodName":method,
            "className":class_name,
            "moduleName":app_name,
            "url":urlPath,
            "logTime":str(get_now_time()),
            "data1":data,
            "data2":'',
            "data3":'',
            "data4":'',
            "hostName":hostName,
			"ipAddress":ipAddress,
			"port":port,
            "message":"START"
        }
        
    def print_log(self,message="",level="info",default_var=""):
        dt=self.data
        dt["message"]=""
        dt["level"]=level
        if message:
            dt["message"]=message
        if default_var:
            dt["data1"]["elapsedTime"] = default_var
        super().print(json.dumps(dt),level)

        