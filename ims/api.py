from rest_framework import routers
from django.urls import path, include
from authentication.views import (
    MyTokenObtainPairView,
    LogoutView,
    UserView,
    ProfileView,
    UserCreate,
)
from attendance.views import AttendanceView
from task.views import TaskView

router = routers.DefaultRouter()
router.register(r'user', UserView, 'user')
router.register(r'profile', ProfileView, 'profile')
router.register(r'attendance', AttendanceView, 'attendance')
router.register(r'task', TaskView, 'task')
# router.register(r'parties', PoliticalPartyViewSet, 'parties')

app_name = 'api'
urlpatterns = [
        path('', include(router.urls)),
        # path('get-report/', get_report, name='get-report'),
        path('login/', MyTokenObtainPairView.as_view(), name='login'),
        path('logout/', LogoutView.as_view(), name='logout'),
        path('register/', UserCreate.as_view(), name='register'),
    
]