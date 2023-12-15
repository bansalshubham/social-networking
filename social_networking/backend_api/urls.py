# yourapp/urls.py
from django.urls import path
from .views import SignUpAPIView, LoginAPIView, UserSearchAPIView, SendRequestAPIView, AcceptFriendRequestAPIView, RejectFriendRequestAPIView, ListFriendsAPIView, ListPendingFriendsAPIView

# urls.py
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


urlpatterns = [
    path('signup/', SignUpAPIView.as_view(), name='signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('search-user/', UserSearchAPIView.as_view(), name="search-user"),
    path('send-request/', SendRequestAPIView.as_view(), name='send-request'),
    path('accept-request/', AcceptFriendRequestAPIView.as_view(), name='accept-request'),
    path('reject-request/', RejectFriendRequestAPIView.as_view(), name='reject-request'),
    path('list-friends/', ListFriendsAPIView.as_view(), name='list-friends'),
    path('pending-friends/', ListPendingFriendsAPIView.as_view(), name='pending-requests')
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
