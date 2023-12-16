from rest_framework.test import APITestCase
from rest_framework import status
from .models import FriendRequest, User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password


class ListFriendsAPITestCase(APITestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create(username='user1', password='password1', email="user1@gmail.com")
        self.user2 = User.objects.create(username='user2', password='password2', email='user2@gmail.com')

        # Create friend requests
        FriendRequest.objects.create(from_user=self.user1, to_user=self.user2, request_status='ACCEPTED')
        FriendRequest.objects.create(from_user=self.user2, to_user=self.user1, request_status='ACCEPTED')

    def test_list_friends_authenticated(self):
        # Authenticate user1
        self.client.force_authenticate(user=self.user1)

        # Make a GET request to the list-friends endpoint
        response = self.client.get('/api/list-friends/')

        # Ensure the request was successful (status code 200)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure the correct number of friends are returned
        self.assertEqual(len(response.data), 1)

        # Ensure the correct friend data is returned
        friend_data = response.data[0]
        self.assertEqual(friend_data['to_user']['username'], 'user2')

    def test_list_friends_unauthenticated(self):
        # Do not authenticate user

        # Make a GET request to the list-friends endpoint
        response = self.client.get('/api/list-friends/')

        # Ensure the request returns a 401 Unauthorized status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



class ListPendingFriendsAPITestCase(APITestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create(username='user1', password='password1', email='user1@gmail.com')
        self.user2 = User.objects.create(username='user2', password='password2', email='user2@gmail.com')
        self.user3 = User.objects.create(username='user3', password='password3', email='user3@gmail.com')

        # Create friend requests
        FriendRequest.objects.create(from_user=self.user1, to_user=self.user2, request_status='PENDING')
        FriendRequest.objects.create(from_user=self.user2, to_user=self.user1, request_status='ACCEPTED')
        FriendRequest.objects.create(from_user=self.user1, to_user=self.user3, request_status='PENDING')
        FriendRequest.objects.create(from_user=self.user3, to_user=self.user1, request_status='REJECTED')

    def test_list_pending_friends_authenticated(self):
        # Authenticate user1
        self.client.force_authenticate(user=self.user1)

        # Make a GET request to the list-pending-friends endpoint
        response = self.client.get('/api/pending-friends/')  # Replace with the actual URL

        # Ensure the request was successful (status code 200)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure the correct number of pending friend requests are returned
        self.assertEqual(len(response.data), 2)

    def test_list_pending_friends_unauthenticated(self):
        # Do not authenticate user

        # Make a GET request to the list-pending-friends endpoint
        response = self.client.get('/api/pending-friends/')  # Replace with the actual URL

        # Ensure the request returns a 401 Unauthorized status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SendRequestAPITestCase(APITestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create(username='user1', password='password1', email='user1@gmail.com')
        self.user2 = User.objects.create(username='user2', password='password2', email='user2@gmail.com')

        # Authenticate user1 and get the token
        refresh = RefreshToken.for_user(self.user1)
        self.access_token = str(refresh.access_token)

    def test_send_request_authenticated(self):
        # Authenticate user1
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Make a POST request to the send-request endpoint
        response = self.client.post(f'/api/send-request/?user_id={self.user2.id}')

        # Ensure the request was successful (status code 200)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Ensure the response message is correct
        self.assertEqual(response.data, {'message': 'Friend Request Send Successfully'})

    def test_send_request_authenticated_self_request(self):
        # Authenticate user1
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Make a POST request to the send-request endpoint with self as the user_id
        data = {'user_id': self.user1.id}
        response = self.client.post('/api/send-request/', data)

        # Ensure the request returns a 400 Bad Request status
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_request_authenticated_duplicate_request(self):
        # Authenticate user1
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Create a friend request from user1 to user2
        FriendRequest.objects.create(from_user=self.user1, to_user=self.user2, request_status='PENDING')

        # Make a POST request to the send-request endpoint with the same user_id
        data = {'user_id': self.user2.id}
        response = self.client.post('/api/send-request/', data)

        # Ensure the request returns a 400 Bad Request status
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_request_unauthenticated(self):
        # Do not authenticate user

        # Make a POST request to the send-request endpoint
        data = {'user_id': self.user2.id}
        response = self.client.post('/api/send-request/', data)

        # Ensure the request returns a 401 Unauthorized status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



class AcceptFriendRequestAPITestCase(APITestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create(username='user1', password='password1', email='user1@gmail.com')
        self.user2 = User.objects.create(username='user2', password='password2', email='user2@gmail.com')

        # Create a friend request from user2 to user1
        self.friend_request = FriendRequest.objects.create(from_user=self.user1, to_user=self.user2, request_status='PENDING')

        # Authenticate user1 and get the token
        refresh = RefreshToken.for_user(self.user1)
        self.access_token = str(refresh.access_token)

    def test_accept_friend_request_authenticated(self):
        # Authenticate user1
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Make a PATCH request to the accept-friend-request endpoint with query parameters
        response = self.client.patch(f'/api/accept-request/?id={self.friend_request.id}')

        # Ensure the request was successful (status code 200)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure the response message is correct
        # self.assertEqual(response.data, {'status': 'Friend request accepted'})

        # Refresh the friend request from the database
        self.friend_request.refresh_from_db()

        # Ensure the friend request's status is now 'ACCEPTED'
        self.assertEqual(self.friend_request.request_status, 'ACCEPTED')

    def test_accept_friend_request_authenticated_invalid_request_id(self):
        # Authenticate user1
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Make a PATCH request to the accept-friend-request endpoint with an invalid request_id
        response = self.client.patch('/api/accept-request/?id=invalid_id')

        # Ensure the request returns a 404 Not Found status
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accept_friend_request_authenticated_already_accepted(self):
        # Authenticate user1
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Mark the friend request as 'ACCEPTED'
        self.friend_request.request_status = 'ACCEPTED'
        self.friend_request.save()

        # Make a PATCH request to the accept-friend-request endpoint
        response = self.client.patch(f'/api/accept-request/?id={self.friend_request.id}')

        # Ensure the request returns a 404 Not Found status
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_accept_friend_request_unauthenticated(self):
        # Do not authenticate user

        # Make a PATCH request to the accept-friend-request endpoint with query parameters
        response = self.client.patch(f'/api/accept-request/?id={self.friend_request.id}')

        # Ensure the request returns a 401 Unauthorized status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RejectFriendRequestAPITestCase(APITestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create(username='user1', password='password1', email='user1@gmail.com')
        self.user2 = User.objects.create(username='user2', password='password2', email='user2@gmail.com')

        # Create a friend request from user2 to user1
        self.friend_request = FriendRequest.objects.create(from_user=self.user2, to_user=self.user1, request_status='PENDING')

        # Authenticate user1 and get the token
        refresh = RefreshToken.for_user(self.user2)
        self.access_token = str(refresh.access_token)

    def test_reject_friend_request_authenticated(self):
        # Authenticate user1
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Make a PATCH request to the reject-friend-request endpoint with query parameters
        response = self.client.patch(f'/api/reject-request/?id={self.friend_request.id}')

        # Ensure the request was successful (status code 200)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure the response message is correct
        self.assertEqual(response.data, {'message': 'Friend request REJECTED'})

        # Refresh the friend request from the database
        self.friend_request.refresh_from_db()

        # Ensure the friend request's status is now 'REJECTED'
        self.assertEqual(self.friend_request.request_status, 'REJECTED')

    def test_reject_friend_request_authenticated_invalid_request_id(self):
        # Authenticate user1
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Make a PATCH request to the reject-friend-request endpoint with an invalid request_id
        response = self.client.patch('/api/reject-request/?id=invalid_id')

        # Ensure the request returns a 404 Not Found status
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_friend_request_authenticated_already_rejected(self):
        # Authenticate user1
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Mark the friend request as 'REJECTED'
        self.friend_request.request_status = 'REJECTED'
        self.friend_request.save()

        # Make a PATCH request to the reject-friend-request endpoint
        response = self.client.patch(f'/api/reject-request/?id={self.friend_request.id}')

        # Ensure the request returns a 404 Not Found status
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_reject_friend_request_unauthenticated(self):
        # Do not authenticate user

        # Make a PATCH request to the reject-friend-request endpoint with query parameters
        response = self.client.patch(f'/api/reject-request/?id={self.friend_request.id}')

        # Ensure the request returns a 401 Unauthorized status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reject_friend_request_missing_request_id(self):
        # Authenticate user1
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Make a PATCH request to the reject-friend-request endpoint without providing the request_id
        response = self.client.patch('/api/reject-request/')

        # Ensure the request returns a 400 Bad Request status
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



class UserSearchAPITestCase(APITestCase):
    def setUp(self):
        # Create users for testing
        self.user1 = User.objects.create(username='user1', password='password1', email='user1@example.com', first_name='John')
        self.user2 = User.objects.create(username='user2', password='password2', email='user2@example.com', first_name='Jane')
        self.user3 = User.objects.create(username='user3', password='password3', email='user3@example.com', first_name='Doe')

        # Authenticate user1 and get the token
        refresh = RefreshToken.for_user(self.user1)
        self.access_token = str(refresh.access_token)

    def test_user_search_authenticated(self):
        # Authenticate user1
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Make a GET request to the user-search endpoint with query parameters
        response = self.client.get('/api/search-user/?email=user1@example.com')

        # Ensure the request was successful (status code 200)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure the response contains the user's details
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['email'], 'user1@example.com')

    def test_user_search_authenticated_no_results(self):
        # Authenticate user1
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Make a GET request to the user-search endpoint with query parameters for a non-existent user
        response = self.client.get('/api/search-user/?email=nonexistent@example.com')

        # Ensure the request returns a 404 Not Found status
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_user_search_unauthenticated(self):
        # Do not authenticate user

        # Make a GET request to the user-search endpoint with query parameters
        response = self.client.get('/api/search-user/?email=user1@example.com')

        # Ensure the request returns a 401 Unauthorized status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_search_pagination_authenticated(self):
        # Authenticate user1
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Create additional users for testing pagination
        for i in range(4, 12):
            User.objects.create_user(username=f'user{i}', password=f'password{i}', email=f'user{i}@example.com', first_name=f'User{i}')

        # Make a GET request to the user-search endpoint with query parameters and pagination
        response = self.client.get('/api/search-user/?name=User&page_size=5&page=1')

        # Ensure the request was successful (status code 200)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure the response contains the paginated user details
        self.assertEqual(len(response.data['results']), 5)
        self.assertEqual(response.data['count'], 8)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)

    def test_user_search_pagination_unauthenticated(self):
        # Do not authenticate user

        # Make a GET request to the user-search endpoint with query parameters and pagination
        response = self.client.get('/api/search-user/?name=User&page_size=5&page=1')

        # Ensure the request returns a 401 Unauthorized status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



class LoginAPITestCase(APITestCase):
    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create(username='testuser', password=make_password('testpassword'), email='testuser@gmail.com')

    def test_login_authenticated(self):
        # Make a POST request to the login endpoint with valid credentials
        response = self.client.post('/api/login/', {'email': 'testuser@gmail.com', 'password': 'testpassword'})
        # Ensure the request was successful (status code 200)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure the response contains the access token and refresh token
        self.assertIn('token', response.data)

    def test_login_authenticated_wrong_password(self):
        # Make a POST request to the login endpoint with invalid credentials
        response = self.client.post('/api/login/', {'email': 'testuser@gmail.com', 'password': 'wrongpassword'})

        # Ensure the request returns a 400 Bad Request status
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_unauthenticated(self):
        # Make a POST request to the login endpoint with invalid credentials
        response = self.client.post('/api/login/', {'email': 'nonexistentuser@gmail.com', 'password': 'password'})

        # Ensure the request returns a 400 Bad Request status
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_credentials(self):
        # Make a POST request to the login endpoint without providing credentials
        response = self.client.post('/api/login/')

        # Ensure the request returns a 400 Bad Request status
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



class SignUpAPITestCase(APITestCase):
    def setUp(self):
        # Create a user for testing
        self.existing_user = User.objects.create(username='existinguser', email='existinguser@example.com', password=make_password('existingpassword'))

    def test_signup_successful(self):
        # Make a POST request to the signup endpoint with valid data
        response = self.client.post('/api/signup/', {'username': 'newuser', 'email': 'newuser@example.com', 'password': 'newpassword'})

        # Ensure the request was successful (status code 201)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Ensure the response contains the new user's details
        self.assertEqual(response.data['email'], 'newuser@example.com')

        # Ensure the new user is created in the database
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_signup_duplicate_email(self):
        # Make a POST request to the signup endpoint with an existing email
        response = self.client.post('/api/signup/', {'username': 'duplicateuser', 'email': 'existinguser@example.com', 'password': 'duplicatepassword'})

        # Ensure the request returns a 400 Bad Request status
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Ensure the response contains an error message
        self.assertIn('User with this email already exists.', response.data['detail'])

        # Ensure the existing user is not overwritten in the database
        self.assertEqual(User.objects.get(email='existinguser@example.com').username, 'existinguser')
        