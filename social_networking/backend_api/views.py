# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .models import User, FriendRequest  # Import the User model
# from .serializers import SignUpSerializer
# from rest_framework.permissions import IsAuthenticated
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework.decorators import authentication_classes, permission_classes
# from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
# from .models import FriendRequest
# from .serializers import FriendRequestSerializer
# from rest_framework_simplejwt.tokens import AccessToken
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from .serializers import ListFriendRequestSerializer
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status, pagination
# from .models import User
# from .serializers import UserSearchSerializer
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.authtoken.models import Token
# from rest_framework_simplejwt.tokens import RefreshToken
# from .serializers import LoginSerializer, FriendRequestSerializer

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



# def get_user_email(request):
#     # Decode the token
#     token = request.auth
#     decoded_token = AccessToken()
#     decoded_token = decoded_token.payload # .decode(token, verify=False)  # Set verify to False for now
#     print(decoded_token)
#     # Extract user email
#     user_email = decoded_token['payload']['email'] if 'email' in decoded_token['payload'] else None

#     return Response({'email': user_email})


class SignUpAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve the email from the request data
            email = request.data.get('email', None)

            # Check if a user with the given email already exists
            if User.objects.filter(email=email).exists():
                return Response({'detail': 'User with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

            # If the email is unique, proceed with creating the user
            serializer = SignUpSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response("Some Internal server error.", status=status.HTTP_503_SERVICE_UNAVAILABLE)

    
# yourapp/views.py


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
            

            return Response("Email and password required.", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response("Some Internal server error.", status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
# class Test(APIView):
    
#     def get(self, request):
#         # email = get_user_email(request)
#         print(request.auth.payload)
#         print(request.user)
#         return Response(f"Hello")
    

# views.py




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
                        users = User.objects.filter(email=email.lower())
                    elif name:
                        users = User.objects.filter(first_name__contains=name)

                    # Use pagination from the pagination_class
                    pg = UserSearchPagination()
                    paginated_users = pg.paginate_queryset(users, request, view=self)

                    serializer = UserSearchSerializer(paginated_users, many=True)
                    return pg.get_paginated_response(serializer.data)

                except User.DoesNotExist:
                    return Response({'error': 'No users found'}, status=status.HTTP_404_NOT_FOUND)
                
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response("Some Internal server error.", status=status.HTTP_503_SERVICE_UNAVAILABLE)

    


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
                    return Response("not possible")
                if FriendRequest.objects.filter(from_user=from_user, to_user_id=to_user_id).exists():
                    return Response({'error': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)

                FriendRequest.objects.create(from_user=from_user, to_user_id=to_user_id)

                # Use pagination from the pagination_class
                return Response("Friend Request Send Successfully")
                
            return Response("Please provide user_id", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response("Some Internal server error.", status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class AcceptFriendRequestAPIView(APIView):

    def patch(self, request):
        try:
            serializer = FriendRequestSerializer(data=request.query_params)

            if serializer.is_valid():
                try:
                    from_user = request.user  # The authenticated user sending the request
                    friend_request_id = serializer.validated_data['id']
                    friend_request = FriendRequest.objects.get(from_user=from_user, id=friend_request_id, request_status='PENDING')
                except FriendRequest.DoesNotExist:
                    return Response({'error': 'Friend request not found or already accepted/rejected'}, status=status.HTTP_404_NOT_FOUND)

                friend_request.request_status = 'ACCEPTED'
                friend_request.save()

                return Response({'status': 'Friend request accepted'}, status=status.HTTP_200_OK)
            return Response("Please provide request id", status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response("Some Internal server error.", status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class RejectFriendRequestAPIView(APIView):

    def patch(self, request):
        try:
            serializer = FriendRequestSerializer(data=request.query_params)

            if serializer.is_valid():
                try:
                    from_user = request.user  # The authenticated user sending the request
                    friend_request_id = serializer.validated_data['id']
                    friend_request = FriendRequest.objects.get(from_user=from_user, id=friend_request_id, request_status='PENDING')
                except FriendRequest.DoesNotExist:
                    return Response({'error': 'Friend request not found or already accepted/rejected'}, status=status.HTTP_404_NOT_FOUND)

                friend_request.request_status = 'REJECTED'
                friend_request.save()
                logger.info(f"Friend request REJECTED from {from_user.id} for {friend_request.id}")
                return Response({'status': 'Friend request REJECTED'}, status=status.HTTP_200_OK)
            
            return Response("Please provide request id", status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response("Some Internal server error.", status=status.HTTP_503_SERVICE_UNAVAILABLE)
        



@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class ListFriendsAPIView(APIView):
    def get(self, request):
        user = request.user
        friends = FriendRequest.objects.filter(from_user=user, request_status='ACCEPTED').select_related('to_user')

        serializer = ListFriendRequestSerializer(friends, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class ListPendingFriendsAPIView(APIView):
    def get(self, request):
        user = request.user
        friends = FriendRequest.objects.filter(from_user=user, request_status='PENDING').select_related('to_user')

        serializer = ListFriendRequestSerializer(friends, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


