from django.urls import path,re_path
from .views import ToAliPayPageAPIView

urlpatterns = [
    path("alipay",ToAliPayPageAPIView.as_view()),
]