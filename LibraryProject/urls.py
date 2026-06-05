from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

from books.views import BookViewSet, BorrowRecordViewSet, StatisticsViewSet, login_api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('books.urls')),
    path('logs/', include('logs.urls')),
    path('api/login/', login_api, name='api_login'),
]

router = DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'borrow-records', BorrowRecordViewSet, basename='borrowrecord')
router.register(r'statistics', StatisticsViewSet, basename='statistics')

urlpatterns += [
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)