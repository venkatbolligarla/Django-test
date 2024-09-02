from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import UserSerializer
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.response import Response
from .models import FriendRequest, User
from .serializers import FriendRequestSerializer
from django.utils import timezone
from datetime import timedelta


class UserSearchView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    #pagination_class = PageNumberPagination

    def get_queryset(self):
        query = self.request.query_params.get('q', None)
        if query:
            return User.objects.filter(Q(email__iexact=query) | Q(username__icontains=query))
        return User.objects.none()
    
    

class FriendRequestView(generics.CreateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        to_user = User.objects.get(id=request.data['to_user_id'])
        from_user = request.user

        # Rate limiting (no more than 3 requests per minute)
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        if FriendRequest.objects.filter(from_user=from_user, created_at__gte=one_minute_ago).count() >= 3:
            return Response({'error': 'Rate limit exceeded. Try again later.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        friend_request, created = FriendRequest.objects.get_or_create(from_user=from_user, to_user=to_user)
        if not created:
            return Response({'error': 'Friend request already sent.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'status': 'Friend request sent.'}, status=status.HTTP_201_CREATED)

class FriendRequestUpdateView(generics.UpdateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        friend_request = self.get_object()
        friend_request.status = request.data['status']
        friend_request.save()
        return Response({'status': f'Friend request {friend_request.status}.'})

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user)

class FriendsListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        friends = User.objects.filter(
            Q(sent_requests__to_user=user, sent_requests__status='accepted') |
            Q(received_requests__from_user=user, received_requests__status='accepted')
        )
        return friends

class PendingFriendRequestsView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user, status='pending')


