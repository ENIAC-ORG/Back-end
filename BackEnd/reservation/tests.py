from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from counseling.models import Psychiatrist, Pationt
from Doctorpanel.models import FreeTime
from .models import Reservation
from datetime import date, timedelta
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from django.conf import settings
from reservation.models import Reservation
from accounts.models import User
from django.contrib.auth.hashers import make_password
import logging

logger = logging.getLogger(__name__)


class ReservationTestCase(APITestCase):

    def setUp(self):
        # Create a mock user
        self.user = User.objects.create(
            email="testuser@example.com",
            password=make_password("oldpassword123"),
            is_email_verified=True,
            role=User.TYPE_USER
        )
        # self.client = APIClient()
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

        # Log in the user
        self.client.login(username="testuser", password="password")

        # Create FreeTime for the psychiatrist
        self.free_time1 = FreeTime.objects.create(
            psychiatrist=self.psychiatrist,
            date=date.today() + timedelta(days=1),
            time="10:00:00",
            month='October',
            day='دوشنبه'
        )

        self.free_time2 = FreeTime.objects.create(
            psychiatrist=self.psychiatrist,
            date=date.today() + timedelta(days=2),
            time="14:00:00",
            month='January',
            day='سه‌شنبه'
        )

        self.free_time3 = FreeTime.objects.create(
            psychiatrist=self.psychiatrist,
            date=date.today() + timedelta(days=32),
            time="16:00:00",
            month='November',
            day='چهارشنبه'
        )
        self.create = f"{settings.WEBSITE_URL}reserve/create/"
        self.destroy = f"{settings.WEBSITE_URL}reserve/delete/"
        self.freetimelist = f"{settings.WEBSITE_URL}reserve/get-free-time/"
        self.betweendate = f"{settings.WEBSITE_URL}reserve/between_dates/"
        self.lastmonth = f"{settings.WEBSITE_URL}reserve/last_month/"
        self.lastweek = f"{settings.WEBSITE_URL}reserve/last_week/"


    def test_create_reservation_success(self):
        data = {
            "type": "مجازی",
            "date": str(self.free_time1.date),
            "time": self.free_time1.time,
            "doctor_id": self.psychiatrist.id
        }

        response = self.client.post(self.create, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "reservation successfully created")

    def test_destroy_reservation_success(self):
        reservation = Reservation.objects.create(
            type="حضوری",
            date=self.free_time1.date,
            time=self.free_time1.time,
            psychiatrist=self.psychiatrist,
            pationt=self.pationt,
            day=self.free_time1.day
        )

        response = self.client.delete(f"{self.destroy}{reservation.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_month_success(self):
        Reservation.objects.create(
            type="حضوری",
            date=self.free_time1.date,
            time=self.free_time1.time,
            psychiatrist=self.psychiatrist,
            pationt=self.pationt,
            day=self.free_time1.day
        )

        data = {
            "month": self.free_time1.date.month,
            "year": self.free_time1.date.year,
            "doctor_id": self.psychiatrist.id
        }

        response = self.client.post(self.lastmonth, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_last_week_success(self):
        Reservation.objects.create(
            type="حضوری",
            date=self.free_time1.date,
            time=self.free_time1.time,
            psychiatrist=self.psychiatrist,
            pationt=self.pationt,
            day=self.free_time1.day
        )

        data = {
            "date": str(self.free_time1.date),
            "doctor_id": self.psychiatrist.id
        }

        response = self.client.post(self.lastweek, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_between_dates_success(self):
        Reservation.objects.create(
            type="حضوری",
            date=self.free_time1.date,
            time=self.free_time1.time,
            psychiatrist=self.psychiatrist,
            pationt=self.pationt,
            day=self.free_time1.day
        )

        data = {
            "start_date": str(self.free_time1.date - timedelta(days=1)),
            "end_date": str(self.free_time1.date + timedelta(days=1)),
            "doctor_id": self.psychiatrist.id
        }

        response = self.client.post(self.betweendate, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


    def test_create_reservation_time_not_available(self):
        # Test creating a reservation for a time not available
        data = {
            "type": "مجازی",
            "date": str(date.today() + timedelta(days=5)),
            "time": "12:00:00",
            "doctor_id": self.psychiatrist.id
        }

        response = self.client.post(self.create, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'This time is not available for the chosen doctor.')

    def test_create_reservation_role_not_patient(self):
        # Test reservation creation with a user role not "patient"
        self.user.role = "doctor"
        self.user.save()

        data = {
            "type": "حضوری",
            "date": str(self.free_time1.date),
            "time": self.free_time1.time,
            "doctor_id": self.psychiatrist.id
        }

        response = self.client.post(self.create, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'The role must be paitient')

    def test_create_reservation_under_8_days_drift(self):
        # Test reservation within 8 days of the last reservation
        Reservation.objects.create(
            type="حضوری",
            date=self.free_time1.date - timedelta(days=5),
            time=self.free_time1.time,
            psychiatrist=self.psychiatrist,
            pationt=self.pationt,
            day=self.free_time1.day
        )

        data = {
            "type": "حضوری",
            "date": str(self.free_time1.date),
            "time": self.free_time1.time,
            "doctor_id": self.psychiatrist.id
        }

        response = self.client.post(self.create, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'you can not reservere 2 times under 8 days drift')

    def test_create_reservation_freetime_deleted(self):
        # Test successful reservation creation and free time deletion
        data = {
            "type": "حضوری",
            "date": str(self.free_time1.date),
            "time": self.free_time1.time,
            "doctor_id": self.psychiatrist.id
        }

        response = self.client.post(self.create, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(FreeTime.objects.filter(id=self.free_time1.id).exists())

    def test_destroy_reservation_not_found(self):
        # Test deleting a reservation that does not exist
        response = self.client.delete(f"{self.destroy}9999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Reservation not found')

    def test_destroy_reservation_freetime_added(self):
        # Test deleting a reservation and free time being added back
        reservation = Reservation.objects.create(
            type="حضوری",
            date=self.free_time1.date,
            time=self.free_time1.time,
            psychiatrist=self.psychiatrist,
            pationt=self.pationt,
            day=self.free_time1.day
        )

        response = self.client.delete(f"{self.destroy}{reservation.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(FreeTime.objects.filter(
            psychiatrist=self.psychiatrist,
            date=reservation.date,
            time=reservation.time
        ).exists())

    def test_list_free_times_multiple_instances(self):
        # Test retrieving multiple free times
        response = self.client.get(f"{self.freetimelist}{self.psychiatrist.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["Free Time List"]), 2)
