from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Book
from .forms import BookForm
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from logs.utils import log_operation
def is_admin(user):
    return user.is_authenticated and user.is_staff
@login_required
def book_list(request):
    books = Book.objects.all()
    return render(request, 'books/book_list.html', {'books': books})

@login_required
@user_passes_test(is_admin)
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            log_operation(request.user, '添加图书', f'添加了图书《{form.instance.title}》', request.META.get('REMOTE_ADDR'))
            return redirect('book_list')
    else:
        form = BookForm()

    return render(request, 'books/book_form.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            log_operation(request.user, '编辑图书', f'编辑了图书《{book.title}》', request.META.get('REMOTE_ADDR'))
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'books/book_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        log_operation(request.user, '删除图书', f'删除了图书《{book.title}》', request.META.get('REMOTE_ADDR'))
        return redirect('book_list')
    return render(request, 'books/book_confirm_delete.html', {'book': book})
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import BorrowRecord
from logs.utils import log_operation

@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if book.available_quantity < 1:
        messages.error(request, f'《{book.title}》 暂无库存，不能借阅')
    else:
        due_date = timezone.now().date() + timedelta(days=30)
        BorrowRecord.objects.create(
            user=request.user,
            book=book,
            due_date=due_date
        )
        book.available_quantity -= 1
        book.save()
        log_operation(request.user, '借书', f'借阅了《{book.title}》', request.META.get('REMOTE_ADDR'))
        messages.success(request, f'成功借阅《{book.title}》，应还日期：{due_date}')
    return redirect('book_list')

@login_required
def return_book(request, borrow_id):
    record = get_object_or_404(BorrowRecord, id=borrow_id, user=request.user, status='borrowed')
    record.return_date = timezone.now().date()
    record.status = 'returned'
    record.save()
    book = record.book
    book.available_quantity += 1
    book.save()
    log_operation(request.user, '还书', f'归还了《{book.title}》', request.META.get('REMOTE_ADDR'))
    messages.success(request, f'成功归还《{book.title}》')
    return redirect('my_borrows')
@login_required
def my_borrows(request):
    records = BorrowRecord.objects.filter(user=request.user).order_by('-borrow_date')
    return render(request, 'books/my_borrows.html', {'records': records})


from django.db.models import Count, Q
from datetime import date, timedelta
from django.utils import timezone


@login_required
def statistics(request):
    # 1. 最近7天借阅趋势数据
    end_date = date.today()
    start_date = end_date - timedelta(days=7)
    daily_data = []
    for i in range(8):
        day = start_date + timedelta(days=i)
        count = BorrowRecord.objects.filter(borrow_date=day).count()
        daily_data.append({'date': day.strftime('%m-%d'), 'count': count})

 
    hot_books = Book.objects.annotate(borrow_count=Count('borrowrecord')).order_by('-borrow_count')[:5]


    overdue_records = BorrowRecord.objects.filter(due_date__lt=date.today(), status='borrowed').select_related('book',
                                                                                                               'user')


    from django.contrib.auth.models import User
    active_users = User.objects.annotate(borrow_count=Count('borrowrecord')).order_by('-borrow_count')[:5]


    records = BorrowRecord.objects.filter(status='returned').values('user_id', 'book_id')
    if records.exists() and len(set(r['user_id'] for r in records)) > 1:
        import pandas as pd
        from sklearn.metrics.pairwise import cosine_similarity
        df = pd.DataFrame(list(records))
        pivot = df.pivot_table(index='user_id', columns='book_id', aggfunc='size', fill_value=0)
        pivot = pivot.applymap(lambda x: 1 if x > 0 else 0)
        current_user_id = request.user.id
        if current_user_id in pivot.index:
            similarities = cosine_similarity(pivot)
            user_index = list(pivot.index).index(current_user_id)
            sim_scores = list(enumerate(similarities[user_index]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            similar_users = [pivot.index[i] for i, score in sim_scores[1:3] if score > 0]
            recommend_book_ids = set()
            for uid in similar_users:
                user_books = set(pivot.loc[uid][pivot.loc[uid] == 1].index)
                recommend_book_ids.update(user_books)
            current_books = set(pivot.loc[current_user_id][pivot.loc[current_user_id] == 1].index)
            recommend_book_ids = recommend_book_ids - current_books
            recommend_books = Book.objects.filter(id__in=recommend_book_ids)[:5]
        else:
            recommend_books = []
    else:

        recommend_books = Book.objects.annotate(borrow_count=Count('borrowrecord')).order_by('-borrow_count')[:5]


    context = {
        'daily_data': daily_data,
        'hot_books': hot_books,
        'overdue_records': overdue_records,
        'active_users': active_users,
        'recommend_books': recommend_books,
    }
    return render(request, 'books/statistics.html', context)