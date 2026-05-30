from django.db import models
from django.contrib.auth.models import User


class OperationLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    operation_type = models.CharField('操作类型', max_length=50)  # 登录、借书、还书、添加图书等
    detail = models.TextField('详情')
    ip_address = models.GenericIPAddressField('IP地址', null=True)
    create_time = models.DateTimeField('操作时间', auto_now_add=True)

    def __str__(self):
        return f'{self.create_time} - {self.user} - {self.operation_type}'