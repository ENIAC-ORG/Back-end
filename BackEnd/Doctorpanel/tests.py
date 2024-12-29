from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.conf import settings
from .models import FreeTime
from Rating.models import Rating
from counseling.models import Psychiatrist , Pationt
from reservation.models import Reservation
from accounts.models import User , Pending_doctor
from datetime import datetime, timedelta
import calendar
from django.contrib.auth.hashers import make_password
import logging
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import User
from counseling.models import Psychiatrist
from django.utils import timezone
from accounts.models import User, Pending_doctor
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)

class DoctorPanelViewTest(TestCase):

    def setUp(self):

        self.psychiatrist_user = User.objects.create(
            email="psychiatrist@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_USER
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.psychiatrist_user)
        self.psychiatrist = Psychiatrist.objects.create(
            user=self.psychiatrist_user,
            image=None,  
            field=Psychiatrist.TYPE_INDIVIDUAL,
            clinic_address="123 Mock Street, City",
            clinic_telephone_number="1234567890",
            doctorate_code="DOC123"
        )
        self.client.login(username="psychiatrist@example.com", password="password123")

        self.valid_data = {
            "month": "January",
            "day": "شنبه",  
            "time": "10:00,11:00,12:00"
        }
        self.free_time_1 = FreeTime.objects.create(
            psychiatrist=self.psychiatrist,
            month="January",
            day="یکشنبه",  
            date=timezone.now().date(),
            time="10:00"
        )
        self.free_time_2 = FreeTime.objects.create(
            psychiatrist=self.psychiatrist,
            month="January",
            day="یکشنبه",
            date=timezone.now().date() + timedelta(days=7),
            time="11:00"
        )
        self.free_time_3 = FreeTime.objects.create(
            psychiatrist=self.psychiatrist,
            month="January",
            day="یکشنبه",
            date=timezone.now().date() - timedelta(days=7),
            time="11:00"
        )

    def test_post_free_times_success(self):
        response = self.client.post('https://eniacgroup.ir/DoctorPanel/doctor/post-free-times/', self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_free_times = response.data
        current_year = datetime.now().year
        january_start = datetime(current_year, 1, 1)
        january_end = datetime(current_year, 1, 31)

        saturdays_in_january = []
        current_date = january_start
        while current_date <= january_end:
            if current_date.weekday() == 5: 
                saturdays_in_january.append(current_date)
            current_date += timedelta(days=1)

        expected_free_times = len(saturdays_in_january) * 3  
        self.assertEqual(len(created_free_times), expected_free_times)

        time_slots = ["10:00", "11:00", "12:00"]
        for time_slot in time_slots:
            matching_free_times = [
                ft for ft in created_free_times
                if ft['month'] == "January" and ft['day'] == "شنبه" and ft['time'] == time_slot
            ]
            self.assertEqual(len(matching_free_times), 4, f"Expected 4 free times for time slot {time_slot}, but found {len(matching_free_times)}.")

    def test_post_free_times_failure(self):
        # # 1. Missing fields
        # missing_fields_data = {"month": "January", "day": "شنبه"}  # Missing time
        # response = self.client.post('https://eniacgroup.ir/DoctorPanel/doctor/post-free-times/', missing_fields_data)
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertIn('All fields are required.', response.data.get('non_field_errors', []))

        # 2. Invalid day name
        # invalid_day_data = {"month": "January", "day": "InvalidDay", "time": "10:00,11:00,12:00"}
        # response = self.client.post('https://eniacgroup.ir/DoctorPanel/doctor/post-free-times/', invalid_day_data)
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertIn('Invalid day name.', response.data.get('error', ''))

        # 3. Duplicate free times
        self.client.post('https://eniacgroup.ir/DoctorPanel/doctor/post-free-times/', self.valid_data)  # Create free times
        response = self.client.post('https://eniacgroup.ir/DoctorPanel/doctor/post-free-times/', self.valid_data)  # Attempt duplicate
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
        response.data.get('error', ''),
        'Free times already exist for this date. Use UpdateFreeTime to modify existing times.'
    )

        # # 4. Invalid time format
        # invalid_time_data = {"month": "January", "day": "شنبه", "time": "invalid_time"}
        # response = self.client.post('https://eniacgroup.ir/DoctorPanel/doctor/post-free-times/', invalid_time_data)
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertIn('Invalid time format', response.data.get('error', ''))

        # 5. Psychiatrist not found (simulating an unauthenticated user)
        self.client.logout()  # Simulate an unauthenticated request
        response = self.client.post('https://eniacgroup.ir/DoctorPanel/doctor/post-free-times/', self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get('detail', ''), 'Authentication credentials were not provided.')

        # Re-authenticate for subsequent tests
        self.client.force_authenticate(user=self.psychiatrist_user)

        # 2. Psychiatrist not found
        # Simulate a request with a user who is not a psychiatrist
        new_user = User.objects.create(
            email="not_a_psychiatrist@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_USER
        )
        self.client.force_authenticate(user=new_user)  # Authenticate as the new user
        response = self.client.post('https://eniacgroup.ir/DoctorPanel/doctor/post-free-times/', self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get('error', ''), 'Psychiatrist not found.')

        # Restore psychiatrist user for further tests
        self.client.force_authenticate(user=self.psychiatrist_user)

        # # 6. Invalid month name
        # invalid_month_data = {"month": "InvalidMonth", "day": "شنبه", "time": "10:00,11:00,12:00"}
        # self.client.force_authenticate(user=self.psychiatrist_user)  # Re-authenticate
        # response = self.client.post('https://eniacgroup.ir/DoctorPanel/doctor/post-free-times/', invalid_month_data)
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertIn('Invalid month name.', response.data.get('error', ''))

        # 7. No Saturdays in the given month
        # no_saturdays_data = {"month": "February", "day": "شنبه", "time": "10:00,11:00,12:00"}
        # response = self.client.post('https://eniacgroup.ir/DoctorPanel/doctor/post-free-times/', no_saturdays_data)
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertIn('No valid dates found for the given day in this month.', response.data.get('error', ''))

    def test_get_free_times_success(self):
        response = self.client.get("https://eniacgroup.ir/DoctorPanel/doctor/get-free-times/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        free_times = response.data['Free Time List']
        self.assertEqual(len(free_times), 2)

        expected_times = [
            {"month": "January", "day": "یکشنبه", "date": self.free_time_1.date.isoformat(), "time": self.free_time_1.time},
            {"month": "January", "day": "یکشنبه",  "date": self.free_time_2.date.isoformat(), "time": self.free_time_2.time}
        ]
        free_times_normalized = [
        {
            "month": ft["month"],
            "day": ft["day"],
            "date": ft["date"],
            "time": ft["time"].strftime("%H:%M")
        } for ft in free_times
    ]
        self.assertEqual(free_times_normalized, expected_times)

    def test_get_free_times_failure(self):
        # 1. Unauthenticated user
        self.client.logout()  # Simulate an unauthenticated request
        response = self.client.get("https://eniacgroup.ir/DoctorPanel/doctor/get-free-times/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get('detail', ''), 'Authentication credentials were not provided.')

        # Re-authenticate for subsequent tests
        self.client.force_authenticate(user=self.psychiatrist_user)

        # 2. Psychiatrist not found
        # Simulate a request with a user who is not a psychiatrist
        new_user = User.objects.create(
            email="not_a_psychiatrist@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_USER
        )
        self.client.force_authenticate(user=new_user)  # Authenticate as the new user
        response = self.client.get("https://eniacgroup.ir/DoctorPanel/doctor/get-free-times/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get('error', ''), 'Psychiatrist not found.')

        # Restore psychiatrist user for further tests
        self.client.force_authenticate(user=self.psychiatrist_user)

        # 3. No free times available
        FreeTime.objects.all().delete()  # Remove all free times for the psychiatrist
        response = self.client.get("https://eniacgroup.ir/DoctorPanel/doctor/get-free-times/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['Free Time List']), 0)

    def test_update_free_times_success(self):
        update_data = {
            "month": "January",
            "day": "یکشنبه",
            "time": "14:00,15:00,16:00"
        }
        response = self.client.put('https://eniacgroup.ir/DoctorPanel/doctor/update-free-times/', update_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_free_times = response.data
        current_year = datetime.now().year
        january_start = datetime(current_year, 1, 1)
        january_end = datetime(current_year, 1, 31)

        sunday_in_january = []
        current_date = january_start
        while current_date <= january_end:
            if current_date.weekday() == 6: 
                sunday_in_january.append(current_date)
            current_date += timedelta(days=1)

        expected_free_times = len(sunday_in_january) * 3  
        self.assertEqual(len(created_free_times), expected_free_times)

        time_slots = ["14:00","15:00","16:00"]
        for time_slot in time_slots:
            matching_free_times = [
                ft for ft in created_free_times
                if ft['month'] == "January" and ft['day'] == "یکشنبه" and ft['time'] == time_slot
            ]
            self.assertEqual(len(matching_free_times), 4, f"Expected 4 free times for time slot {time_slot}, but found {len(matching_free_times)}.")

    def test_update_free_times_failure(self):
        # 1. Unauthenticated user
        self.client.logout()  # Simulate an unauthenticated request
        update_data = {
            "month": "January",
            "day": "یکشنبه",
            "time": "14:00,15:00,16:00"
        }
        response = self.client.put('https://eniacgroup.ir/DoctorPanel/doctor/update-free-times/', update_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get('detail', ''), 'Authentication credentials were not provided.')

        # Re-authenticate for subsequent tests
        self.client.force_authenticate(user=self.psychiatrist_user)

        # 2. Psychiatrist not found
        new_user = User.objects.create(
            email="not_a_psychiatrist@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_USER
        )
        self.client.force_authenticate(user=new_user)  # Authenticate as a non-psychiatrist user
        response = self.client.put('https://eniacgroup.ir/DoctorPanel/doctor/update-free-times/', update_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get('error', ''), 'Psychiatrist not found.')

        # Restore psychiatrist user for further tests
        self.client.force_authenticate(user=self.psychiatrist_user)

        # # 3. Missing fields (e.g., missing time field)
        # incomplete_data = {"month": "January", "day": "یکشنبه"}  # Missing 'time'
        # response = self.client.put('https://eniacgroup.ir/DoctorPanel/doctor/update-free-times/', incomplete_data)
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertIn('All fields are required.', response.data.get('non_field_errors', []))

        # 4. No free times exist for this date
        non_existing_date_data = {
            "month": "February",
            "day": "سه‌شنبه",
            "time": "10:00,11:00,12:00"
        }
        response = self.client.put('https://eniacgroup.ir/DoctorPanel/doctor/update-free-times/', non_existing_date_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('error', ''),
            'No free times exist for this date. Use PostFreeTime to add new free times.'
        )

    def test_delete_free_time_success(self):
        post_data = {
            "month": "January",
            "day": "شنبه", 
            "time": "14:00,15:00,16:00"
        }

        response = self.client.post('https://eniacgroup.ir/DoctorPanel/doctor/post-free-times/', post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_free_times = response.data

        current_year = datetime.now().year
        january_start = datetime(current_year, 1, 1)
        january_end = datetime(current_year, 1, 31)

        saturdays_in_january = []
        current_date = january_start
        while current_date <= january_end:
            if current_date.weekday() == 5:  # Monday
                saturdays_in_january.append(current_date)
            current_date += timedelta(days=1)

        # Check if the number of created free times matches expectations
        expected_free_times = len(saturdays_in_january) * 3  # 3 time slots per Monday
        self.assertEqual(len(created_free_times), expected_free_times)

        delete_data = {
            "month": "January",
            "day": "شنبه",
            "time": "14:00,15:00"
        }

        response = self.client.post('https://eniacgroup.ir/DoctorPanel/doctor/delete-free-times/', delete_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('success', response.data)
        self.assertEqual(response.data['success'], 'All specified free times deleted successfully.')
        self.assertIn('deleted_times', response.data)
        self.assertEqual(sorted(response.data['deleted_times']), sorted(["14:00", "15:00"]))

        deleted_free_times = FreeTime.objects.filter(
            psychiatrist=self.psychiatrist,
            month="January",
            day="شنبه",
            time__in=["14:00", "15:00"]
        )
        self.assertEqual(deleted_free_times.count(), 0)  

        remaining_free_times = FreeTime.objects.filter(
            psychiatrist=self.psychiatrist,
            month="January",
            day="شنبه",
            time="16:00"
        )
        self.assertEqual(remaining_free_times.count(), len(saturdays_in_january)) 

    def test_delete_free_time_failure(self):
        # 1. Unauthenticated user
        self.client.logout()  # Simulate an unauthenticated request
        delete_data = {
            "month": "January",
            "day": "شنبه", 
            "time": "14:00,15:00"
        }
        response = self.client.post('https://eniacgroup.ir/DoctorPanel/doctor/delete-free-times/', delete_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get('detail', ''), 'Authentication credentials were not provided.')

        # Re-authenticate for subsequent tests
        self.client.force_authenticate(user=self.psychiatrist_user)

        # 2. Psychiatrist not found
        new_user = User.objects.create(
            email="not_a_psychiatrist@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_USER
        )
        self.client.force_authenticate(user=new_user)  # Authenticate as a non-psychiatrist user
        response = self.client.post('https://eniacgroup.ir/DoctorPanel/doctor/delete-free-times/', delete_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get('error', ''), 'Psychiatrist not found.')

        # Restore psychiatrist user for further tests
        self.client.force_authenticate(user=self.psychiatrist_user)

        # # 3. Missing fields (e.g., missing time field)
        # incomplete_data = {"month": "January", "day": "شنبه"}  # Missing 'time'
        # response = self.client.post('https://eniacgroup.ir/DoctorPanel/doctor/delete-free-times/', incomplete_data)
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertIn('All fields are required.', response.data.get('non_field_errors', []))

        # # 4. Invalid day name
        # invalid_day_data = {
        #     "month": "January",
        #     "day": "InvalidDay",
        #     "time": "14:00,15:00"
        # }
        # response = self.client.post('https://eniacgroup.ir/DoctorPanel/doctor/delete-free-times/', invalid_day_data)
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertIn('Invalid day name.', response.data.get('error', ''))

        # # 5. Invalid month name
        # invalid_month_data = {
        #     "month": "InvalidMonth",
        #     "day": "شنبه",
        #     "time": "14:00,15:00"
        # }
        # response = self.client.post('https://eniacgroup.ir/DoctorPanel/doctor/delete-free-times/', invalid_month_data)
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertIn('Invalid month name.', response.data.get('error', ''))

        # # 6. Invalid time format
        # invalid_time_data = {
        #     "month": "January",
        #     "day": "شنبه",
        #     "time": "invalid_time"
        # }
        # response = self.client.post('https://eniacgroup.ir/DoctorPanel/doctor/delete-free-times/', invalid_time_data)
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertIn('Invalid time format', response.data.get('error', ''))

        # 7. No free times exist for the specified time slots
        non_existing_time_data = {
            "month": "January",
            "day": "شنبه",
            "time": "17:00,18:00"
        }
        response = self.client.post('https://eniacgroup.ir/DoctorPanel/doctor/delete-free-times/', non_existing_time_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get('error', ''), 'Some free times were not found.')

    def test_get_rating_success(self):
        patient_user_1 = User.objects.create(
            email="patient1@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_USER
        )
        patient_user_2 = User.objects.create(
            email="patient2@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_USER
        )

        patient_1 = Pationt.objects.create(user=patient_user_1)
        patient_2 = Pationt.objects.create(user=patient_user_2)

        Rating.objects.create(psychiatrist=self.psychiatrist, pationt=patient_1, rating=5, comments="Excellent!", date=timezone.now().date())
        Rating.objects.create(psychiatrist=self.psychiatrist, pationt=patient_2, rating=4, comments="Good service.", date=timezone.now().date())

        expected_average = (5 + 4 ) / 2  
        expected_total_ratings = 2  
        expected_rating_count = {
            "1 star": 0,
            "2 stars": 0,
            "3 stars": 0,  
            "4 stars": 1,  
            "5 stars": 1   
        }

        response = self.client.get('https://eniacgroup.ir/DoctorPanel/get_rating/')
        logger.warning(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('average_score', response.data)
        self.assertEqual(response.data['average_score'], expected_average)

        self.assertIn('total_ratings_count', response.data)
        self.assertEqual(response.data['total_ratings_count'], expected_total_ratings)

        self.assertIn('ratings_count', response.data)
        for choice, label in Rating.CHOICES:
            self.assertEqual(response.data['ratings_count'].get(label, 0), expected_rating_count[label])

    def test_get_rating_failure(self):
        # 1. Unauthenticated user
        self.client.logout()  # Simulate an unauthenticated request
        response = self.client.get('https://eniacgroup.ir/DoctorPanel/get_rating/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get('detail', ''), 'Authentication credentials were not provided.')

        # Re-authenticate for subsequent tests
        self.client.force_authenticate(user=self.psychiatrist_user)

        # 2. Psychiatrist not found
        new_user = User.objects.create(
            email="not_a_psychiatrist@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_USER
        )
        self.client.force_authenticate(user=new_user)  # Authenticate as a non-psychiatrist user
        response = self.client.get('https://eniacgroup.ir/DoctorPanel/get_rating/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get('error', ''), 'Psychiatrist not found.')

        # Restore psychiatrist user for further tests
        self.client.force_authenticate(user=self.psychiatrist_user)

        # 3. No ratings exist for this psychiatrist
        # Ensure there are no ratings for this psychiatrist
        Rating.objects.filter(psychiatrist=self.psychiatrist).delete()
        response = self.client.get('https://eniacgroup.ir/DoctorPanel/get_rating/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('average_score', response.data)
        self.assertEqual(response.data['average_score'], 0)  # No ratings, so average should be 0
        self.assertIn('total_ratings_count', response.data)
        self.assertEqual(response.data['total_ratings_count'], 0)  # No ratings, so total count should be 0
        self.assertIn('ratings_count', response.data)
        for choice, label in Rating.CHOICES:
            self.assertEqual(response.data['ratings_count'].get(label, 0), 0)  # All counts should be 0



# class AdminDoctorPannelTestCase(TestCase):
#     def setUp(self):
#         # Create an admin user
#         self.admin_user = User.objects.create_superuser(
#             email="admin@example.com",
#             password="password123"
#         )
#         # Create separate users for each pending doctor
#         self.user_1 = User.objects.create_user(
#             email="user1@example.com",
#             firstname="John",
#             lastname="Doe",
#             gender="M",
#             date_of_birth="1990-01-01",
#             phone_number="+989123456789",
#             password="password123"
#         )
#         self.user_2 = User.objects.create_user(
#             email="user2@example.com",
#             firstname="Jane",
#             lastname="Smith",
#             gender="F",
#             date_of_birth="1992-02-02",
#             phone_number="+989987654321",
#             password="password123"
#         )
#         # Create pending doctor entries for each user
#         self.pending_doctor_1 = Pending_doctor.objects.create(
#             user=self.user_1,
#             doctorate_code="DOC123",
#             firstname="John",
#             lastname="Doe",
#             number_of_application=5
#         )
#         self.pending_doctor_2 = Pending_doctor.objects.create(
#             user=self.user_2,
#             doctorate_code="DOC456",
#             firstname="Jane",
#             lastname="Smith",
#             number_of_application=5
#         )
#         # Authenticate as admin
#         self.client = APIClient()
#         refresh = RefreshToken.for_user(self.admin_user)
#         self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        
#     def test_get_queryset_success(self):
#         # Test retrieving all pending doctors without a search query
#         response = self.client.get('https://eniacgroup.ir/DoctorPanel/pending_doctor/')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data['data']), 2)  # Expect 2 pending doctors
#         self.assertIn('John', response.data['data'][0]['firstname'])
#         self.assertIn('Jane', response.data['data'][1]['firstname'])

#         # Test searching for a specific doctor by name
#         response = self.client.get('https://eniacgroup.ir/DoctorPanel/pending_doctor/', {'search': 'John'})
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data['data']), 1)  # Expect only John Doe
#         self.assertIn('John', response.data['data'][0]['firstname'])

#         # Test searching for a specific doctor by doctorate_code
#         response = self.client.get('https://eniacgroup.ir/DoctorPanel/pending_doctor/', {'search': 'DOC456'})
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data['data']), 1)  # Expect only Jane Smith
#         self.assertIn('Jane', response.data['data'][0]['firstname'])


