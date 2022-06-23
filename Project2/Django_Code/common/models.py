from django.db import models


# Create your models here.
class Users(models.Model):  # 定义用户类，用来创建用户信息的表
    # 用户名称
    name = models.CharField(max_length=200)

    # 用户电话
    phone = models.CharField(max_length=100)

    # 用户住址
    addr = models.CharField(max_length=500)
