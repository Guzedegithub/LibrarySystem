from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .utils import log_operation

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    log_operation(user, '登录', '用户登录成功', request.META.get('REMOTE_ADDR'))