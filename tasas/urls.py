from django.conf.urls import url, include
from .views import IndexView, UniversidadView

urlpatterns =[
    url(r'^$', IndexView.as_view(), name="index"),
    url(r'^universidad/(?P<universidad>[a-z\-]+)', UniversidadView.as_view(), name="edit")
]