from django.db import models
from custom_lib.base_model import BaseFields



class User(BaseFields):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=255, null=False)
    last_name = models.CharField(max_length=255, null=False)
    user_type_code = models.CharField(max_length=255, null=False)
    mobile_number = models.CharField(max_length=255, null=False)
    username = models.CharField(max_length=255, null=False)
    email = models.EmailField(max_length=255, null=False)
    password = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'users'

class PageInfo(BaseFields):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False)
    user_id  = models.IntegerField(null=False)
    page_access_token = models.CharField(max_length=500, null=False)
    page_id = models.CharField(max_length=255, null=False)
    facebook_earning = models.CharField(max_length=255)
    instagram_earning = models.CharField(max_length=255)
    snapchat_earning = models.CharField(max_length=255)
    youtube_earning = models.CharField(max_length=255)


    class Meta:
        managed = False
        db_table = 'page_info'


class UserDetails(BaseFields):
    id = models.BigAutoField(primary_key=True)
    user_id  = models.IntegerField(null=False)
    image_url = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=20)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    pincode = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'user_details'