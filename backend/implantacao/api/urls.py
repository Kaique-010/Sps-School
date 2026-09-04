from django.urls import include, path

from .router import router
from .views import HealthView

urlpatterns = [
    path('health/', HealthView.as_view(), name='health'),
    path('', include(router.urls)),
]
