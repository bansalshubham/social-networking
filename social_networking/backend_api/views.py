from django.contrib.auth.models import User
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status, pagination
from .pagination import UserSearchPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.authtoken.models import Token
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.db.models import Q
from .models import FriendRequest, User
from .serializers import (
    SignUpSerializer,
    FriendRequestSerializer,
    ListFriendRequestSerializer,
    UserSearchSerializer,
    LoginSerializer,
    SendFriendRequestSerializer
)

import logging
logger = logging.getLogger("social_app")


class SignUpAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve the email from the request data
            email = request.data.get('email', None)
            # If the email is unique, proceed with creating the user
            serializer = SignUpSerializer(data=request.data)

            if serializer.is_valid():
                email = email.lower()
                # Check if a user with the given email already exists
                if User.objects.filter(email__iexact=email).exists():
                    return Response({'detail': 'User with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
                serializer.save()
                return Response({"email": email, "message": "signed up successfully."}, status=status.HTTP_201_CREATED)

            return Response({"message": "Please provide email to signup."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": "Some Internal server error."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class LoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            serializer = LoginSerializer(data=request.data)

            if serializer.is_valid():
                user = serializer.validated_data['user']
                # token, created = Token.objects.get_or_create(user=user)
                refresh = RefreshToken.for_user(user)

                access_token = str(refresh.access_token)
                refresh = str(refresh)
                response = Response({'token': access_token}, status=status.HTTP_200_OK)
                response['Authorization'] = f'Bearer {access_token}'
                return response
            

            return Response({"message": "Email and password required."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": "Some Internal server error."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class UserSearchAPIView(APIView):

    def get(self, request, *args, **kwargs):
        try:
            serializer = UserSearchSerializer(data=request.query_params)

            if serializer.is_valid():
                email = serializer.validated_data.get('email', '')
                name = serializer.validated_data.get('name', '')

                try:
                    if email:
                        users = User.objects.filter(email__iexact=email).order_by("id")
                    elif name:
                        users = User.objects.filter(first_name__contains=name).order_by("id")

                    pg = UserSearchPagination()
                    paginated_users = pg.paginate_queryset(users, request, view=self)

                    serializer = UserSearchSerializer(paginated_users, many=True)
                    return pg.get_paginated_response(serializer.data)

                except User.DoesNotExist:
                    return Response({'error': 'No users found'}, status=status.HTTP_404_NOT_FOUND)
                
            return Response({"message": "Either provide email or name to search"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": "Some Internal server error."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class SendRequestAPIView(APIView):

    throttle_classes = [UserRateThrottle]

    def post(self, request, *args, **kwargs):
        try:
            serializer = SendFriendRequestSerializer(data=request.query_params)

            if serializer.is_valid():

                from_user = request.user  # The authenticated user sending the request
                to_user_id = serializer.validated_data['user_id']

                if from_user.id == to_user_id:
                    return Response({"message": "User can not send friend request to itself."}, status=status.HTTP_400_BAD_REQUEST)
                if FriendRequest.objects.filter(from_user__in=[from_user, to_user_id], to_user_id__in=[to_user_id, from_user]).exists():
                    return Response({'message': 'Friend request already there'}, status=status.HTTP_400_BAD_REQUEST)

                FriendRequest.objects.create(from_user=from_user, to_user_id=to_user_id)

                return Response({"message": "Friend Request Send Successfully"}, status=status.HTTP_201_CREATED)
                
            return Response({"message": "Please provide user_id"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": "Some Internal server error."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class AcceptFriendRequestAPIView(APIView):

    def patch(self, request):
        try:
            serializer = FriendRequestSerializer(data=request.query_params)

            if serializer.is_valid():
                try:
                    user = request.user  # The authenticated user sending the request
                    friend_request_id = serializer.validated_data['id']
                    friend_request = FriendRequest.objects.get(to_user=user, id=friend_request_id, request_status='PENDING')
                except FriendRequest.DoesNotExist:
                    return Response({'message': 'Friend request not found or already accepted/rejected'}, status=status.HTTP_404_NOT_FOUND)

                friend_request.request_status = 'ACCEPTED'
                friend_request.save()

                return Response({'message': 'Friend request accepted'}, status=status.HTTP_200_OK)
            return Response({"message": "Please provide request id"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"message": "Some Internal server error."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class RejectFriendRequestAPIView(APIView):

    def patch(self, request):
        try:
            serializer = FriendRequestSerializer(data=request.query_params)

            if serializer.is_valid():
                try:
                    user = request.user  # The authenticated user sending the request
                    friend_request_id = serializer.validated_data['id']
                    friend_request = FriendRequest.objects.get(to_user=user, id=friend_request_id, request_status='PENDING')
                except FriendRequest.DoesNotExist:
                    return Response({'message': 'Friend request not found or already accepted/rejected'}, status=status.HTTP_404_NOT_FOUND)

                friend_request.request_status = 'REJECTED'
                friend_request.save()

                return Response({'message': 'Friend request REJECTED'}, status=status.HTTP_200_OK)
            
            return Response({"message": "Please provide request id"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"message": "Some Internal server error."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        



@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class ListFriendsAPIView(APIView):
    def get(self, request):
        try:
            user = request.user
            friends = FriendRequest.objects.filter(Q(from_user=user) | Q(to_user=user), request_status='ACCEPTED').select_related('to_user', 'from_user')

            serializer = ListFriendRequestSerializer(friends, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": "Some Internal server error."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class ListPendingFriendsAPIView(APIView):
    def get(self, request):
        try:
            user = request.user
            friends = FriendRequest.objects.filter(to_user=user, request_status='PENDING').select_related('to_user')

            serializer = ListFriendRequestSerializer(friends, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": "Some Internal server error."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


