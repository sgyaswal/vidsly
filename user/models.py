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