from rest_framework.routers import DefaultRouter
from .views import UniversidadViewSet, ProvinciaViewSet, TasasViewSet, AverageViewSet

#TODO: consider: http://www.django-rest-framework.org/api-guide/routers/#custom-routers
router = DefaultRouter()
router.register(r'provincias/(?P<provincia>[A-Za-z\ ]+)', ProvinciaViewSet)
router.register(r'universidad/(?P<universidad>[a-z\-]+)/tasas', TasasViewSet, base_name="universidad")
router.register(r'universidad', UniversidadViewSet, base_name="universidad")
router.register(r'average', AverageViewSet, base_name="average_detail")
#router.register(r'average', AverageViewSet, base_name="average")

urlpatterns = router.urls
