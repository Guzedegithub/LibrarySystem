from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'category', 'total_quantity', 'available_quantity', 'publish_date']
        widgets = {
            'publish_date': forms.DateInput(attrs={'type': 'date'}),
        }