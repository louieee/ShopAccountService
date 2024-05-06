from django.urls import path
from rest_framework.routers import SimpleRouter

from core import views


app_name = "core"
router = SimpleRouter()
router.register("staffs", views.StaffAPI)
router.register("admins", views.AdminAPI)
router.register("customers", views.CustomerAPI)


urlpatterns = [
    path("auth/login/", views.LoginAPI.as_view()),
    path("auth/signup/", views.SignupAPI.as_view()),
    path("auth/profile/", views.ProfileAPI.as_view())
]
urlpatterns.extend(router.urls)
