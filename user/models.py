from django.db import models
from custom_lib.base_model import BaseFields



class User(BaseFields):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False)
    username = models.CharField(max_length=255, null=False)
    email = models.EmailField(max_length=255, null=False)
    password = models.CharField(max_length=50)
    # ifLogged = models.BooleanField(default=False)
    token = models.CharField(max_length=500, null=True, default="")

    class Meta:
        managed = False
        db_table = 'user'