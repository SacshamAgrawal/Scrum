from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('sprint',views.SprintViewSet)
router.register('task',views.TaskViewSet)
router.register('user',views.UserViewSet)
