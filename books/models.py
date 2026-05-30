from django.db import models
from django.contrib.auth.models import User


class Book(models.Model):
    title = models.CharField('书名', max_length=200)
    author = models.CharField('作者', max_length=100)
    isbn = models.CharField('ISBN', max_length=13, unique=True)
    category = models.CharField('分类', max_length=50, default='其他')
    total_quantity = models.IntegerField('总数量', default=1)
    available_quantity = models.IntegerField('可借数量', default=1)
    cover = models.ImageField(upload_to='covers/', blank=True, null=True)
    publish_date = models.DateField('出版日期', null=True, blank=True)

    def __str__(self):
        return self.title


class BorrowRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='借阅人')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='图书')
    borrow_date = models.DateField('借书日期', auto_now_add=True)
    due_date = models.DateField('应还日期')
    return_date = models.DateField('实际归还日期', null=True, blank=True)
    status = models.CharField('状态', max_length=10, default='borrowed',
                              choices=[('borrowed', '借出'), ('returned', '已还')])

    class Meta:
        ordering = ['-borrow_date']