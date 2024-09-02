from django.urls import path
from .views import UserSearchView, FriendRequestView, FriendRequestUpdateView, FriendsListView, PendingFriendRequestsView

urlpatterns = [
    path('search/', UserSearchView.as_view(), name='user-search'),
    path('friend-request/', FriendRequestView.as_view(), name='friend-request'),
    path('friend-request/<int:pk>/', FriendRequestUpdateView.as_view(), name='friend-request-update'),
    path('friends/', FriendsListView.as_view(), name='friends-list'),
    path('pending-requests/', PendingFriendRequestsView.as_view(), name='pending-requests'),
]
