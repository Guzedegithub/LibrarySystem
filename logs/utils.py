from logs.models import OperationLog

def log_operation(user, op_type, detail, ip=None):
    if user and not user.is_authenticated:
        user = None
    OperationLog.objects.create(
        user=user,
        operation_type=op_type,
        detail=detail,
        ip_address=ip
    )