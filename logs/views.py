from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import OperationLog

@staff_member_required
def log_list(request):
    logs = OperationLog.objects.all().order_by('-create_time')
    return render(request, 'logs/log_list.html', {'logs': logs})