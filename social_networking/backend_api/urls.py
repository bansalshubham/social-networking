# yourapp/urls.py
from django.urls import path
from .views import SignUpAPIView, LoginAPIView, UserSearchAPIView, SendRequestAPIView, AcceptFriendRequestAPIView, RejectFriendRequestAPIView, ListFriendsAPIView, ListPendingFriendsAPIView

urlpatterns = [
    path('signup/', SignUpAPIView.as_view(), name='signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('search-user/', UserSearchAPIView.as_view(), name="search-user"),
    path('send-request/', SendRequestAPIView.as_view(), name='send-request'),
    path('accept-request/', AcceptFriendRequestAPIView.as_view(), name='accept-request'),
    path('reject-request/', RejectFriendRequestAPIView.as_view(), name='reject-request'),
    path('list-friends/', ListFriendsAPIView.as_view(), name='list-friends'),
    path('pending-friends/', ListPendingFriendsAPIView.as_view(), name='pending-requests')
]
