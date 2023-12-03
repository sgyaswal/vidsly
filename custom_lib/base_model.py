from django.db import models
from rest_framework import serializers
import numbers


class BaseSerializer(serializers.Serializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        non_null_ret = {}
        for key in ret.keys():
            if ret[key] or isinstance(ret[key], numbers.Number):
                non_null_ret[(key)] = ret[key]
        return non_null_ret


class BaseFields(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True