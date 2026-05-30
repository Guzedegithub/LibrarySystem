import os
import csv
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LibraryProject.settings')
django.setup()

from books.models import Book

csv_file = 'books.csv'

with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # 检查是否已存在，根据 isbn 去重
        obj, created = Book.objects.get_or_create(
            isbn=row['isbn'],
            defaults={
                'title': row['title'],
                'author': row['author'],
                'category': row['category'],
                'total_quantity': int(row['total_quantity']),
                'available_quantity': int(row['available_quantity']),
            }
        )
        if created:
            print(f"已添加: {obj.title}")
        else:
            print(f"已存在: {obj.title} (跳过)")