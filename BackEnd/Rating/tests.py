from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import Pationt, Psychiatrist, Rating
from reservation.models import Reservation
# from accounts.models import User




class RatingViewSetTestCase(TestCase):
    
    def setUp(self):
        # Create a mock user
        self.user = User.objects.create(
            email="testuser@example.com",
            password=make_password("oldpassword123"),
            is_email_verified=True,
            role=User.TYPE_USER
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create mock Psychiatrist user and object
        self.psychiatrist_user = User.objects.create(
            email="psychiatrist@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_USER
        )
        self.psychiatrist = Psychiatrist.objects.create(
            user=self.psychiatrist_user,
            image=None,  # Default to None for testing
            field=Psychiatrist.TYPE_INDIVIDUAL,
            clinic_address="123 Mock Street, City",
            clinic_telephone_number="1234567890",
            doctorate_code="DOC123"
        )

        # Create mock Patient
        self.pationt = Pationt.objects.create(user=self.user)

        # Create a Reservation object and assign it to self.reservation
        chosen_date = "2024-12-01"  # Example date for the reservation
        chosen_time = "14:00"       # Example time for the reservation
        self.reservation = Reservation.objects.create(
            type="Standard",  # Example type of reservation
            date=chosen_date,
            time=chosen_time,
            psychiatrist=self.psychiatrist,
            day=chosen_date,  # Assuming `chosen_date` is passed as a day; adjust if needed
            pationt=self.pationt
        )

        # Valid payload for rating
        self.valid_payload = {
            "psychiatrist": self.psychiatrist.id,
            "rating": 4,
            "comments": "Great psychiatrist!"
        }

        # Invalid payload for testing
        self.invalid_payload = {
            "psychiatrist": self.psychiatrist.id,  # Invalid psychiatrist
            "rating": -1,          # Out of valid range (assume range is 1-5)
            "comments": ""
        }

        self.rating_url = f"{settings.WEBSITE_URL}Rating/Rate/"


    @patch('Rating.models.Rating.objects.filter')  # Mock database filters
    def test_rating_creation_success(self, mock_rating_filter):
        # Ensure no duplicate rating exists
        mock_rating_filter.return_value.exists.return_value = False

        response = self.client.post(self.rating_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['psychiatrist'], self.valid_payload['psychiatrist'])
        self.assertEqual(response.data['rating'], self.valid_payload['rating'])
        self.assertEqual(response.data['comments'], self.valid_payload['comments'])

    def test_rating_creation_no_reservation(self):
        # Remove reservation
        Reservation.objects.filter(
            pationt=self.pationt, psychiatrist=self.psychiatrist
        ).delete()

        response = self.client.post(self.rating_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['error'],
            'You can only rate a psychiatrist if you have had a reservation with them.'
        )

    def test_rating_creation_duplicate(self):
        # Create a duplicate rating
        Rating.objects.create(
            psychiatrist=self.psychiatrist,
            pationt=self.pationt,
            rating=4,
            comments="Already rated."
        )

        response = self.client.post(self.rating_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['error'],
            'You have already rated this psychiatrist.'
        )

    def test_invalid_payload(self):
        # rating': [ErrorDetail(string='"-1" is not a valid choice.', code='invalid_choice')]}
        response = self.client.post(self.rating_url, self.invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('"-1" is not a valid choice.', str( response.data['rating'][0]))
