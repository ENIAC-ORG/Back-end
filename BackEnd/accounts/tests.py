from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from django.contrib.auth import get_user_model
# from accounts.models import User


from django.conf import settings
from unittest.mock import patch
import jwt
from .utils import generate_tokens
from jwt.exceptions import InvalidSignatureError
from django.contrib.auth.hashers import make_password
from unittest.mock import patch, MagicMock
       
class SignUpViewTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('signup')  # Update with your actual URL name for the SignUpView
        self.valid_data = {
            "email": "user22@example.com",
            "password1": "#password123#",
            "password2": "#password123#",
            "is_doctor": False,
        }
        self.website_url = settings.WEBSITE_URL
       

    @patch('accounts.views.random.randint', return_value=6795)  
    @patch('accounts.views.EmailThread.start')  
    def test_signup_success(self, mock_email_thread, mock_randint):
        User = get_user_model()
        response = self.client.post(self.url, self.valid_data)
        # Check the HTTP response status
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Validate response structure
        self.assertIn("user", response.data)
        self.assertIn("message", response.data)
        self.assertIn("code", response.data)
        self.assertIn("url", response.data)
        
        # Validate user object in the response
        user_data = response.data["user"]
        self.assertEqual(user_data["email"], self.valid_data["email"])
        self.assertEqual(user_data["role"], "user")
        self.assertIsNone(user_data["date_of_birth"])
        self.assertIsNone(user_data["gender"])
        self.assertIsNone(user_data["firstname"])
        self.assertIsNone(user_data["lastname"])
        self.assertIsNone(user_data["phone_number"])
        self.assertIsInstance(user_data["id"], int)
        
        # Validate other fields
        self.assertEqual(response.data["message"], "User created successfully. Please check your email to activate your account.")
        self.assertEqual(response.data["code"], "6795")
        url = "http://46.249.100.141:8070/accounts/activation_confirm/"
        print(f"hthis is urlllllllll : {url}")
        print(f"this is real url " , response.data["url"])
        self.assertTrue(response.data["url"].startswith(url))
        # Check if the user is created in the database
        self.assertTrue(User.objects.filter(email=self.valid_data["email"]).exists())
        
        # Check if email thread was started
        mock_email_thread.assert_called_once()

    @patch('accounts.views.random.randint', return_value=6795)
    @patch('accounts.views.EmailThread.start')
    def test_signup_password_mismatch(self, mock_email_thread, mock_randint):
        invalid_data = self.valid_data.copy()
        invalid_data["password2"] = "differentpassword"  # Introduce a mismatch

        response = self.client.post(self.url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Passwords must match.", response.data["password1"])
        self.assertIn("Passwords must match.", response.data["password2"])

class ActivationConfirmViewTest(APITestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create(
            email="user@example.com",
            password="#password123#",
            verification_code="1234",
            role=User.TYPE_USER
        )
        self.token = jwt.encode({"user_id": self.user.id}, settings.SECRET_KEY, algorithm="HS256")
        self.url = reverse('activation_confirm', args=[self.token])  # Ensure the name matches your URL configuration
        

    @patch('accounts.views.jwt.decode')
    def test_activation_confirm_success(self, mock_jwt_decode):
        mock_jwt_decode.return_value = {"user_id": self.user.id}
        valid_data = {"verification_code": "1234"}
        response = self.client.post(self.url, valid_data)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "successfully verified"})
        self.assertTrue(self.user.is_email_verified)
        self.assertIsNone(self.user.verification_code)
    
    @patch('accounts.views.jwt.decode')
    def test_activation_confirm_invalid_token(self, mock_jwt_decode):
        # Simulate an exception being raised when decoding the token
        mock_jwt_decode.side_effect = InvalidSignatureError("Invalid signature")
        
        response = self.client.post(self.url, {"verification_code": "1234"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"message": "Invalid token"})

    @patch('accounts.views.jwt.decode')
    def test_activation_confirm_invalid_code(self, mock_jwt_decode):
        # Mock jwt.decode to return a valid payload
        mock_jwt_decode.return_value = {"user_id": self.user.id}

        invalid_data = {"verification_code": "code"}
        response = self.client.post(self.url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"message": "Invalid code"})

    @patch('accounts.views.jwt.decode')
    def test_activation_confirm_invalid_user(self, mock_jwt_decode):
        # Mock jwt.decode to return a valid payload but simulate no user found
        mock_jwt_decode.return_value = {"user_id": 999}  # Non-existent user ID
        response = self.client.post(self.url, {"verification_code": "1234"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"message": "Invalid user"})

class ChangePasswordViewTest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create(
            email="testuser@example.com",
            password=make_password("oldpassword123"),
            is_email_verified= True ,
            role = User.TYPE_USER 
        )
        self.url = "/accounts/change_password/"
        self.tokens = generate_tokens(self.user.id)
        self.access_token = self.tokens['access']
        
    @patch('rest_framework_simplejwt.authentication.JWTAuthentication.authenticate')
    def test_change_password_success(self, mock_authenticate):
        # Mock the authentication to return the user
        mock_authenticate.return_value = (self.user, None)
        response = self.client.post(
            self.url,
            data={
                "old_password": "oldpassword123",
                "new_password": "newpassword123",
                "new_password1": "newpassword123",
            },
        )
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Password changed successfully."})
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword123"))

    @patch('rest_framework_simplejwt.authentication.JWTAuthentication.authenticate')
    def test_change_password_invalid_old_password(self,mock_authenticate):
        mock_authenticate.return_value = (self.user, None)
        # Send a POST request with an incorrect old password and include JWT token in headers
        response = self.client.post(
            self.url,
            data={
                "old_password": "wrongpassword",
                "new_password": "newpassword123",
                "new_password1": "newpassword123",
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "Invalid current password."})

    @patch('rest_framework_simplejwt.authentication.JWTAuthentication.authenticate')
    def test_change_password_missing_fields(self,mock_authenticate):
        mock_authenticate.return_value = (self.user, None)
        # Send a POST request with missing fields and include JWT token in headers
        response = self.client.post(
            self.url,
            data={
                "old_password": "oldpassword123"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)

    @patch('rest_framework_simplejwt.authentication.JWTAuthentication.authenticate')
    def test_change_password_serializer_validation_failure(self ,mock_authenticate):
        mock_authenticate.return_value = (self.user, None)
        # Mock the serializer to simulate validation failure
        response = self.client.post(
            self.url,
            data={
                "old_password": "oldpassword123",
                "new_password": "",  # Invalid password field to simulate failure
                "new_password1": "",  # Should match new_password
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)




class LogoutViewTest(APITestCase):
    def setUp(self):
        User = get_user_model()
        # Create a test user
        self.user = User.objects.create(
            email="testuser@example.com",
            password=make_password("oldpassword123"),
            is_email_verified= True ,
            role = User.TYPE_USER 
        )
        self.url = "/accounts/Logout/"
        self.client.force_authenticate(user=self.user)  # Authenticate user for tests

    @patch("rest_framework_simplejwt.tokens.RefreshToken.blacklist")
    def test_logout_with_valid_token(self, mock_blacklist):
        # Simulate valid token in cookies
        refresh = RefreshToken.for_user(self.user)
        self.client.cookies["token"] = str(refresh)
        mock_blacklist.return_value = None

        response = self.client.get(self.url)
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"detail": "Logged out successfully"})
        self.assertNotIn("refresh_token", response.cookies)
        self.assertNotIn("access_token", response.cookies)

    def test_logout_with_invalid_token(self):
        # Simulate invalid token in cookies
        self.client.cookies["token"] = "invalid_refresh_token"

        response = self.client.get(self.url)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"detail": "Invalid token"})

    def test_logout_authenticated_without_token(self):
        # Test session-based logout (no token in cookies)
        response = self.client.get(self.url)
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"detail": "Logged out successfully"})

    # @patch('rest_framework_simplejwt.authentication.JWTAuthentication.authenticate')
    # def test_unauthenticated_access(self, mock_authenticate):
    #     self.client.logout()
    #     # Simulate no valid authentication
    #     mock_authenticate.return_value = None # Simulates no user authentication
    #     # Send the GET request
    #     response = self.client.get(self.url)
    #     # Assertions
    #     print("server response , " , response.data )
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    #     self.assertEqual(
    #         response.data["detail"], "Authentication credentials were not provided."
    #     )

class LoginViewTest(APITestCase):
    def setUp(self):
        # Create a test user
        User = get_user_model()
        self.user = User.objects.create(
            email="testuser@example.com",
            password=make_password("oldpassword123"),
            is_email_verified= True ,
            role = User.TYPE_USER 
        )
        self.url = "/accounts/Login/"

    @patch("accounts.views.generate_tokens")
    def test_login_success(self, mock_generate_tokens):
        mock_generate_tokens.return_value = {
            "refresh": "mocked_refresh_token",
            "access": "mocked_access_token"
        }

        # Send valid login data
        response = self.client.post(
            self.url,
            data={
                "email": "testuser@example.com",
                "password": "oldpassword123",
            },
        )
    
        # Assertions
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], "testuser@example.com")
        self.assertEqual(response.data["refresh"], "mocked_refresh_token")
        self.assertEqual(response.data["access"], "mocked_access_token")

    def test_login_invalid_credentials(self):
        # Send invalid login data
        response = self.client.post(
            self.url,
            data={
                "email": "testuser@example.com",
                "password": "wrongpassword",
            },
        )
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data['message'][0]),
            "Incorrect password." # Adjusted to match the actual response format
        )
         
    def test_login_missing_fields(self):
        # Send incomplete login data (missing password)
        response = self.client.post(
            self.url,
            data={
                "email": "testuser@example.com",
            },
        )

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_login_user_does_not_exist(self):
        # Send login data for a non-existent user
        response = self.client.post(
            self.url,
            data={
                "email": "nonexistent@example.com",
                "password": "irrelevantpassword",
            },
        )

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data['email']['message']),
            "Email does not exist."
        )