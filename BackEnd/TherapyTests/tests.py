import json
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import User
from .models import GlasserTest, TherapyTests, MedicalRecord ,TreatementHistory , MedicalRecordPermission
from counseling.models import Pationt ,Psychiatrist
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import date, timedelta
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)



class MedicalRecordViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            email="testuser@example.com",
            password=make_password("oldpassword123"),
            is_email_verified=True,
            role=User.TYPE_USER,
            date_of_birth=date(1990, 1, 1),
            firstname="Test",
            lastname="Name"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.pationt = Pationt.objects.create(user=self.user)
        self.treatment_history1 = {
            "end_date": "2023-12-25",
            "length": 6,
            "is_finished": True,
            "reason_to_leave": "Patient recovered",
            "approach": "CBT",
            "special_drugs": "None"
        }

        self.treatment_history2 = {
            "end_date": "2023-06-30",
            "length": 3,
            "is_finished": False,
            "reason_to_leave": "Ongoing",
            "approach": "Psychoanalysis",
            "special_drugs": "Anti-depressants"
        }
        
        self.treatment_history3 = {
            "end_date": "Invalid Date",
            "length": 3,
            "is_finished": False,
            "reason_to_leave": "Ongoing",
            "approach": "Psychoanalysis",
            "special_drugs": "Anti-depressants"
        }

    def test_create_medical_record_success(self):

        treatment_histories = [self.treatment_history1, self.treatment_history2]

        data = {
            "child_num": 2,
            "name": "Test Name",
            "age": 35,
            "gender": "مرد",
            "nationalID": "1234567890",
            "family_history": True,
            "treatment_histories": treatment_histories
        }

        response = self.client.post(reverse('records_ops'), data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        medical_record_data = json.loads(response.data["medical_record"])
        
        medical_record = MedicalRecord.objects.get(id=medical_record_data["id"])
        self.assertEqual(medical_record.pationt, self.pationt)
        self.assertEqual(medical_record.child_num, data["child_num"])
        self.assertEqual(medical_record.name, data["name"])
        self.assertEqual(medical_record.age, data["age"])
        self.assertEqual(medical_record.gender, data["gender"])
        self.assertEqual(medical_record.nationalID, data["nationalID"])
        self.assertEqual(medical_record.family_history, data["family_history"])
        
        treatment_history_objects = TreatementHistory.objects.filter(medical_record=medical_record)
        
        self.assertEqual(treatment_history_objects.count(), len(treatment_histories))

        for i, history in enumerate(treatment_history_objects):
            self.assertEqual(history.end_date.strftime("%Y-%m-%d"), treatment_histories[i]["end_date"])
            self.assertEqual(history.length, treatment_histories[i]["length"])
            self.assertEqual(history.is_finished, treatment_histories[i]["is_finished"])
            self.assertEqual(history.reason_to_leave, treatment_histories[i]["reason_to_leave"])
            self.assertEqual(history.approach, treatment_histories[i]["approach"])
            self.assertEqual(history.special_drugs, treatment_histories[i]["special_drugs"])

        self.assertEqual(response.data["message"], "record has been successfully created.")

    def test_create_medical_record_failure(self):
        treatment_histories = [
            self.treatment_history1,
            self.treatment_history2,
            self.treatment_history3
        ]

        data = {
            "pationt": self.pationt.id,
            "child_num": 2,
            "name": "Test Name",
            "age": 30,
            "gender": "مرد",
            "nationalID": "1234567890",
            "family_history": True,
            "treatment_histories": treatment_histories
        }
        response = self.client.post(reverse('records_ops'), data,format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_medical_record_success(self):
        medical_record = MedicalRecord.objects.create(
            pationt=self.pationt,
            child_num=2,
            name="Test Name",
            age=34,
            gender="مرد",
            nationalID="1234567890",
            family_history=True
        )
        initial_treatment_history1 = TreatementHistory.objects.create(
            medical_record=medical_record,
            end_date="2023-12-25",
            length=6,
            is_finished=True,
            reason_to_leave="Patient recovered",
            approach="CBT",
            special_drugs="None"
        )


        updated_treatment_history1 = {
            "id": initial_treatment_history1.id,
            "end_date": "2024-01-15",
            "length": 7,
            "is_finished": True,
            "reason_to_leave": "Fully recovered",
            "approach": "CBT",
            "special_drugs": "None"
        }

        new_treatment_history = {
            "end_date": "2024-02-10",
            "length": 2,
            "is_finished": False,
            "reason_to_leave": "Ongoing",
            "approach": "Group Therapy",
            "special_drugs": "Anxiolytics"
        }

        update_data = {
            "child_num": 3,
            "name": "Test Name",
            "age": 35,
            "gender": "مرد",
            "nationalID": "0987654321",
            "family_history": False,
            "treatment_histories": [updated_treatment_history1, new_treatment_history]
        }

        response = self.client.put(
            reverse('records_ops'),
            update_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        medical_record.refresh_from_db()
        self.assertEqual(medical_record.child_num, update_data["child_num"])
        self.assertEqual(medical_record.name, update_data["name"])
        self.assertEqual(medical_record.age, update_data["age"])
        self.assertEqual(medical_record.gender, update_data["gender"])
        self.assertEqual(medical_record.nationalID, update_data["nationalID"])
        self.assertEqual(medical_record.family_history, update_data["family_history"])

        treatment_history_objects = TreatementHistory.objects.filter(medical_record=medical_record)
        self.assertEqual(treatment_history_objects.count(), len(update_data["treatment_histories"]))

        for history in treatment_history_objects:
            if history.id == updated_treatment_history1["id"]:
                self.assertEqual(history.end_date.strftime("%Y-%m-%d"), updated_treatment_history1["end_date"])
                self.assertEqual(history.length, updated_treatment_history1["length"])
                self.assertEqual(history.is_finished, updated_treatment_history1["is_finished"])
                self.assertEqual(history.reason_to_leave, updated_treatment_history1["reason_to_leave"])
                self.assertEqual(history.approach, updated_treatment_history1["approach"])
                self.assertEqual(history.special_drugs, updated_treatment_history1["special_drugs"])
            else:
                self.assertEqual(history.end_date.strftime("%Y-%m-%d"), new_treatment_history["end_date"])
                self.assertEqual(history.length, new_treatment_history["length"])
                self.assertEqual(history.is_finished, new_treatment_history["is_finished"])
                self.assertEqual(history.reason_to_leave, new_treatment_history["reason_to_leave"])
                self.assertEqual(history.approach, new_treatment_history["approach"])
                self.assertEqual(history.special_drugs, new_treatment_history["special_drugs"])

        response_data = response.data
        self.assertEqual(response_data["pationt"], self.pationt.id)
        self.assertEqual(response_data["child_num"], update_data["child_num"])
        self.assertEqual(response_data["name"], update_data["name"])
        self.assertEqual(response_data["age"], update_data["age"])
        self.assertEqual(response_data["gender"], update_data["gender"])
        self.assertEqual(response_data["nationalID"], update_data["nationalID"])
        self.assertEqual(response_data["family_history"], update_data["family_history"])

        for i, history in enumerate(response_data["treatment_histories"]):
            self.assertEqual(history["end_date"], update_data["treatment_histories"][i]["end_date"])
            self.assertEqual(history["length"], update_data["treatment_histories"][i]["length"])
            self.assertEqual(history["is_finished"], update_data["treatment_histories"][i]["is_finished"])
            self.assertEqual(history["reason_to_leave"], update_data["treatment_histories"][i]["reason_to_leave"])
            self.assertEqual(history["approach"], update_data["treatment_histories"][i]["approach"])
            self.assertEqual(history["special_drugs"], update_data["treatment_histories"][i]["special_drugs"])

    def test_update_medical_record_failure(self):
        # Create an initial MedicalRecord for the patient
        medical_record = MedicalRecord.objects.create(
            pationt=self.pationt,
            child_num=2,
            name="Test Name",
            age=34,
            gender="مرد",
            nationalID="1234567890",
            family_history=True
        )

        # Invalid update data: missing required fields
        invalid_data_missing_fields = {
            "name": "Updated Name",
            # Missing 'child_num' and 'treatment_histories'
        }

        response = self.client.put(
            reverse('records_ops'),
            invalid_data_missing_fields,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


        # Invalid update data: invalid field values
        invalid_data_invalid_fields = {
            "child_num": "invalid",  # Should be an integer
            "name": "Test Name",
            "age": -5,  # Invalid age
            "gender": "invalid_gender",  # Invalid choice
            "nationalID": "12345",  # Too short
            "family_history": "not_boolean",  # Should be a boolean
            "treatment_histories": [
                {
                    "end_date": "invalid_date",  # Invalid date format
                    "length": -3,  # Negative length
                    "is_finished": "not_boolean",  # Should be a boolean
                    "reason_to_leave": "Updated reason",
                    "approach": "CBT",
                    "special_drugs": "None"
                }
            ]
        }

        response = self.client.put(
            reverse('records_ops'),
            invalid_data_invalid_fields,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


        # Invalid update data: malformed nested objects
        invalid_data_malformed_nested = {
            "child_num": 3,
            "name": "Updated Name",
            "age": 31,
            "gender": "زن",
            "nationalID": "1234567890",
            "family_history": True,
            "treatment_histories": "not_a_list"  # Should be a list
        }

        response = self.client.put(
            reverse('records_ops'),
            invalid_data_malformed_nested,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_list_all_success(self):
        # Create a psychiatrist user
        psychiatrist_user = User.objects.create(
            email="psychiatrist@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_DOCTOR,
            date_of_birth=date(1990, 1, 1)

        )
        psychiatrist = Psychiatrist.objects.create(user=psychiatrist_user)

        # Authenticate as the psychiatrist
        self.client.force_authenticate(user=psychiatrist_user)

        # Create multiple patients and medical records associated with this psychiatrist
        patient1_user = User.objects.create(
            email="patient1@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_USER,
            date_of_birth=date(1990, 1, 1)
        )
        patient1 = Pationt.objects.create(user=patient1_user)
        medical_record1 = MedicalRecord.objects.create(
            pationt=patient1,
            child_num=1,
            name="Patient One",
            age=34,
            gender="زن",
            nationalID="9876543210",
            family_history=False
        )
        MedicalRecordPermission.objects.create(
            pationt=patient1,
            psychiatrist=psychiatrist
        )

        patient2_user = User.objects.create(
            email="patient2@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_USER,
            date_of_birth=date(1990, 1, 1)
        )
        patient2 = Pationt.objects.create(user=patient2_user)
        medical_record2 = MedicalRecord.objects.create(
            pationt=patient2,
            child_num=2,
            name="Patient Two",
            age=34,
            gender="مرد",
            nationalID="1112223334",
            family_history=True
        )
        MedicalRecordPermission.objects.create(
            pationt=patient2,
            psychiatrist=psychiatrist
        )

        # Create additional unrelated medical records
        unrelated_user = User.objects.create(
            email="unrelated@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_USER,
            date_of_birth=date(1990, 1, 1)
        )
        unrelated_patient = Pationt.objects.create(user=unrelated_user)
        MedicalRecord.objects.create(
            pationt=unrelated_patient,
            child_num=0,
            name="Unrelated Patient",
            age=34,
            gender="مرد",
            nationalID="3334445556",
            family_history=True
        )

        # Call the endpoint
        response = self.client.get(reverse('record_all'))

        # Validate response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate response data
        records = response.data["records"]
        self.assertEqual(len(records), 2)  # Two medical records should be accessible

        # Validate the first record
        record1 = next(record for record in records if record["id"] == medical_record1.id)
        self.assertEqual(record1["name"], medical_record1.name)
        self.assertEqual(record1["age"], medical_record1.age)
        self.assertEqual(record1["gender"], medical_record1.gender)
        self.assertEqual(record1["nationalID"], medical_record1.nationalID)
        self.assertEqual(record1["family_history"], medical_record1.family_history)

        # Validate the second record
        record2 = next(record for record in records if record["id"] == medical_record2.id)
        self.assertEqual(record2["name"], medical_record2.name)
        self.assertEqual(record2["age"], medical_record2.age)
        self.assertEqual(record2["gender"], medical_record2.gender)
        self.assertEqual(record2["nationalID"], medical_record2.nationalID)
        self.assertEqual(record2["family_history"], medical_record2.family_history)

    def test_retrieve_list_all_failure(self):
            # Case 1: Ordinary user tries to access the records
        ordinary_user = User.objects.create(
            email="ordinary@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_USER
        )
        self.client.force_authenticate(user=ordinary_user)

        response = self.client.get(reverse('record_all'))

        # Validate response status code and message
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "ordinary user can not access this Information.")

        # Case 2: Psychiatrist without permissions tries to access the records
        psychiatrist_user = User.objects.create(
            email="psychiatrist_no_permissions@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_DOCTOR
        )
        Psychiatrist.objects.create(user=psychiatrist_user)

        self.client.force_authenticate(user=psychiatrist_user)

        response = self.client.get(reverse('record_all'))

        # Validate response status code and message
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["message"], "you do not have permission.")

    def test_retrieve_list_last_30_day_success(self):
        # Create a psychiatrist user
        psychiatrist_user = User.objects.create(
            email="psychiatrist@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_DOCTOR,
            date_of_birth=date(1990, 1, 1)

        )
        psychiatrist = Psychiatrist.objects.create(user=psychiatrist_user)

        # Authenticate as the psychiatrist
        self.client.force_authenticate(user=psychiatrist_user)

        # Create patients and medical records
        recent_patient_user = User.objects.create(
            email="recent_patient@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_USER,
            date_of_birth=date(1990, 1, 1)

        )
        recent_patient = Pationt.objects.create(user=recent_patient_user)
        recent_medical_record = MedicalRecord.objects.create(
            pationt=recent_patient,
            child_num=1,
            name="Recent Patient",
            age=28,
            gender="زن",
            nationalID="9876543210",
            family_history=False
        )
        # Create MedicalRecordPermission within the last 30 days
        MedicalRecordPermission.objects.create(
            pationt=recent_patient,
            psychiatrist=psychiatrist,
            created_date=timezone.now().date() - timedelta(days=10)
        )

        old_patient_user = User.objects.create(
            email="old_patient@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_USER,
            date_of_birth=date(1990, 1, 1)

        )
        old_patient = Pationt.objects.create(user=old_patient_user)
        old_medical_record = MedicalRecord.objects.create(
            pationt=old_patient,
            child_num=2,
            name="Old Patient",
            age=35,
            gender="مرد",
            nationalID="1112223334",
            family_history=True
        )
        # Create MedicalRecordPermission older than 30 days
        MedicalRecordPermission.objects.create(
            pationt=old_patient,
            psychiatrist=psychiatrist,
            created_date=timezone.now().date() - timedelta(days=40)
        )

        # Call the endpoint
        response = self.client.get(reverse('month_records_ops'))

        # Validate response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate response data
        records = response.data["records"]
        # self.assertEqual(len(records), 1)  # Only the recent record should be included

        # Validate the recent medical record
        self.assertEqual(records[0]["id"], recent_medical_record.id)
        self.assertEqual(records[0]["name"], recent_medical_record.name)
        self.assertEqual(records[0]["age"], recent_medical_record.age)
        self.assertEqual(records[0]["gender"], recent_medical_record.gender)
        self.assertEqual(records[0]["nationalID"], recent_medical_record.nationalID)
        self.assertEqual(records[0]["family_history"], recent_medical_record.family_history)

    def test_retrieve_list_last_30_day_failure(self):
        # Case 1: Ordinary user tries to access the records
        ordinary_user = User.objects.create(
            email="ordinary@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_USER
        )
        self.client.force_authenticate(user=ordinary_user)

        response = self.client.get(reverse('month_records_ops'))

        # Validate response status code and message
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "ordinary user can not access this Information.")

        # Case 2: Psychiatrist without records in the last 30 days
        psychiatrist_user = User.objects.create(
            email="psychiatrist_no_recent_records@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_DOCTOR
        )
        self.client.force_authenticate(user=psychiatrist_user)

        response = self.client.get(reverse('month_records_ops'))

        # Validate response status code and message
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["message"], "you do not have permission.")

    def test_retrieve_list_last_year_success(self):
            # Create a psychiatrist user
            psychiatrist_user = User.objects.create(
                email="psychiatrist@example.com",
                password=make_password("password123"),
                is_email_verified=True,
                role=User.TYPE_DOCTOR,
                date_of_birth=date(1990, 1, 1)

            )
            psychiatrist = Psychiatrist.objects.create(user=psychiatrist_user)

            # Authenticate as the psychiatrist
            self.client.force_authenticate(user=psychiatrist_user)

            # Create patients and medical records
            recent_patient_user = User.objects.create(
                email="recent_patient@example.com",
                password=make_password("password123"),
                is_email_verified=True,
                role=User.TYPE_USER,
                date_of_birth=date(1990, 1, 1)

            )
            recent_patient = Pationt.objects.create(user=recent_patient_user)
            recent_medical_record = MedicalRecord.objects.create(
                pationt=recent_patient,
                child_num=1,
                name="Recent Patient",
                age=28,
                gender="زن",
                nationalID="9876543210",
                family_history=False
            )
            # Create MedicalRecordPermission within the last year
            MedicalRecordPermission.objects.create(
                pationt=recent_patient,
                psychiatrist=psychiatrist,
                created_date=timezone.now().date() - timedelta(days=200)
            )

            old_patient_user = User.objects.create(
                email="old_patient@example.com",
                password=make_password("password123"),
                is_email_verified=True,
                role=User.TYPE_USER,
                date_of_birth=date(1990, 1, 1)

            )
            old_patient = Pationt.objects.create(user=old_patient_user)
            old_medical_record = MedicalRecord.objects.create(
                pationt=old_patient,
                child_num=2,
                name="Old Patient",
                age=35,
                gender="مرد",
                nationalID="1112223334",
                family_history=True
            )
            # Create MedicalRecordPermission older than year
            MedicalRecordPermission.objects.create(
                pationt=old_patient,
                psychiatrist=psychiatrist,
                created_date=timezone.now().date() - timedelta(days=400)
            )

            # Call the endpoint
            response = self.client.get(reverse('year_records_ops'))

            # Validate response status code
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Validate response data
            records = response.data["records"]
            # self.assertEqual(len(records), 1)  # Only the recent record should be included

            # Validate the recent medical record
            self.assertEqual(records[0]["id"], recent_medical_record.id)
            self.assertEqual(records[0]["name"], recent_medical_record.name)
            self.assertEqual(records[0]["age"], recent_medical_record.age)
            self.assertEqual(records[0]["gender"], recent_medical_record.gender)
            self.assertEqual(records[0]["nationalID"], recent_medical_record.nationalID)
            self.assertEqual(records[0]["family_history"], recent_medical_record.family_history)

    def test_retrieve_list_last_year_failure(self):
        # Case 1: Ordinary user tries to access the records
        ordinary_user = User.objects.create(
            email="ordinary@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_USER
        )
        self.client.force_authenticate(user=ordinary_user)

        response = self.client.get(reverse('year_records_ops'))

        # Validate response status code and message
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "ordinary user can not access this Information.")

        # Case 2: Psychiatrist without records in the last year
        psychiatrist_user = User.objects.create(
            email="psychiatrist_no_recent_records@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_DOCTOR
        )
        self.client.force_authenticate(user=psychiatrist_user)

        response = self.client.get(reverse('year_records_ops'))

        # Validate response status code and message
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["message"], "you do not have permission.")

    def test_get_record_by_id_success(self):

        treatment_histories = [self.treatment_history1, self.treatment_history2]

        create_data = {
            "child_num": 2,
            "name": "Test Name",
            "age": 35,
            "gender": "مرد",
            "nationalID": "1234567890",
            "family_history": True,
            "treatment_histories": treatment_histories
        }

        create_response = self.client.post(reverse('records_ops'), create_data, format='json')
        
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        # Extract the ID of the created record
        medical_record_data = json.loads(create_response.data["medical_record"])
        created_record_id = medical_record_data["id"]
                # Create a psychiatrist user
        psychiatrist_user = User.objects.create(
            email="psychiatrist@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_DOCTOR,
            date_of_birth=date(1990, 1, 1)

        )
        psychiatrist = Psychiatrist.objects.create(user=psychiatrist_user)

        # Authenticate as the psychiatrist
        self.client.force_authenticate(user=psychiatrist_user)

        # GET the created MedicalRecord by ID
        response = self.client.get(reverse('patient_record', kwargs={'id': created_record_id}))

        # Validate response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the returned medical record data
        self.assertEqual(response.data["id"], created_record_id)
        self.assertEqual(response.data["name"], create_data["name"])
        self.assertEqual(response.data["age"], create_data["age"])
        self.assertEqual(response.data["gender"], create_data["gender"])
        self.assertEqual(response.data["nationalID"], create_data["nationalID"])
        self.assertEqual(response.data["family_history"], create_data["family_history"])

    def test_get_record_by_id_failure(self):
        # Case 1: Unauthorized Access (Ordinary User)
        ordinary_user = User.objects.create(
            email="ordinary@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_USER,
            date_of_birth=date(1990, 1, 1)

        )
        self.client.force_authenticate(user=ordinary_user)

        # Call the endpoint with a valid record ID
        response = self.client.get(reverse('patient_record', kwargs={'id': 1}))

        # Validate response status code and message
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "Ordinary user cannot access this information.")

        # Case 2: Record Not Found
        psychiatrist_user = User.objects.create(
            email="psychiatrist_no_record@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_DOCTOR,
            date_of_birth=date(1990, 1, 1)
        )
        Psychiatrist.objects.create(user=psychiatrist_user)

        self.client.force_authenticate(user=psychiatrist_user)

        # Call the endpoint with a non-existent record ID
        response = self.client.get(reverse('patient_record', kwargs={'id': 999}))  # ID 999 does not exist

        # Validate response status code and message
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "There is no record with this ID.")

    def test_get_retrieve_success(self):

        treatment_histories = [self.treatment_history1, self.treatment_history2]

        create_data = {
            "child_num": 2,
            "name": "Test Name",
            "age": 35,
            "gender": "مرد",
            "nationalID": "1234567890",
            "family_history": True,
            "treatment_histories": treatment_histories
        }

        create_response = self.client.post(reverse('records_ops'), create_data, format='json')
        
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        # GET the created MedicalRecord by ID
        response = self.client.get(reverse('records_ops'))

        # Validate response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the returned medical record data
        self.assertEqual(response.data["name"], create_data["name"])
        self.assertEqual(response.data["age"], create_data["age"])
        self.assertEqual(response.data["gender"], create_data["gender"])
        self.assertEqual(response.data["nationalID"], create_data["nationalID"])
        self.assertEqual(response.data["family_history"], create_data["family_history"])

    def test_retrieve_retrieve_failure(self):

        # Call the retrieve endpoint
        response = self.client.get(reverse('records_ops'))

        # Assert that the request failed
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the error message is returned
        self.assertEqual(response.data["message"], "There is no record for this user.")

    def test_retrieve_check_success(self):
        treatment_histories = [self.treatment_history1, self.treatment_history2]

        create_data = {
            "child_num": 2,
            "name": "Test Name",
            "age": 35,
            "gender": "مرد",
            "nationalID": "1234567890",
            "family_history": True,
            "treatment_histories": treatment_histories
        }

        create_response = self.client.post(reverse('records_ops'), create_data, format='json')
        
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        # Call the retrieve_check endpoint
        response = self.client.get(reverse('record_check'))

        # Assert that the request was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert the response message indicates the record exists
        self.assertTrue(response.data["message"])

    def test_retrieve_check_failure(self):

        # Call the retrieve_check endpoint
        response = self.client.get(reverse('record_check'))

        # Assert that the request was successful
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Assert the response message indicates no record exists
        self.assertFalse(response.data["message"])

    def test_query_on_records_success(self):
        treatment_histories = [self.treatment_history1, self.treatment_history2]

        create_data = {
            "child_num": 2,
            "name": "Test Name",
            "age": 35,
            "gender": "مرد",
            "nationalID": "1234567890",
            "family_history": True,
            "treatment_histories": treatment_histories
        }

        # Create a MedicalRecord
        create_response = self.client.post(reverse('records_ops'), create_data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        # Extract the created record ID
        medical_record_data = json.loads(create_response.data["medical_record"])
        created_record_id = medical_record_data["id"]

        # Create a psychiatrist user
        psychiatrist_user = User.objects.create(
            email="psychiatrist@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_DOCTOR,
            date_of_birth=date(1990, 1, 1)
        )
        psychiatrist = Psychiatrist.objects.create(user=psychiatrist_user)

        # Assign permission for the psychiatrist to access the patient's record
        MedicalRecordPermission.objects.create(
            pationt=self.pationt,
            psychiatrist=psychiatrist
        )

        # Authenticate as the psychiatrist
        self.client.force_authenticate(user=psychiatrist_user)

        # Query by a partial match for the name
        query_data = {"name": "Test"}
        response = self.client.post(reverse('record_query'), query_data, format='json')

        # Log the response data for debugging
        print("Response data:", response.data)

        # Assert the request was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert the returned data contains the expected medical record
        self.assertIn("records", response.data)
        self.assertEqual(len(response.data["records"]), 1)
        self.assertEqual(response.data["records"][0]["id"], created_record_id)
        self.assertEqual(response.data["records"][0]["name"], create_data["name"])
        self.assertEqual(response.data["records"][0]["nationalID"], create_data["nationalID"])

    def test_query_on_records_failure(self):
        # Case 1: Ordinary User Access
        ordinary_user = User.objects.create(
            email="ordinary@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_USER
        )
        self.client.force_authenticate(user=ordinary_user)
        query_data = {"name": "Test"}
        response = self.client.post(reverse('record_query'), query_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "ordinary user can not access this Information.")

        # Reset client and create a psychiatrist user
        self.client.logout()
        psychiatrist_user = User.objects.create(
            email="psychiatrist@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_DOCTOR
        )
        psychiatrist = Psychiatrist.objects.create(user=psychiatrist_user)
        self.client.force_authenticate(user=psychiatrist_user)

        # Case 2: Psychiatrist Without Permission
        response = self.client.post(reverse('record_query'), query_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "you do not have permission.")

        # Grant permissions to the psychiatrist
        MedicalRecordPermission.objects.create(
            pationt=self.pationt,
            psychiatrist=psychiatrist
        )

        # Case 3: No Matching Records
        query_data = {"name": "Nonexistent"}
        response = self.client.post(reverse('record_query'), query_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "not found any similar data.")

        # # Case 4: Malformed Query Data
        # query_data = {"invalid_field": "Test"}
        # response = self.client.post("https://eniacgroup.ir/TherapyTests/record/query/", query_data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertIn("message", response.data)

        # Case 5: Empty Query
        # query_data = {}
        # response = self.client.post("https://eniacgroup.ir/TherapyTests/record/query/", query_data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertGreaterEqual(len(response.data.get("records", [])), 1)  # Ensure at least one record is retrieved

    def test_delete_medical_record_success(self):
        treatment_histories = [self.treatment_history1, self.treatment_history2]

        create_data = {
            "child_num": 2,
            "name": "Test Name",
            "age": 35,
            "gender": "مرد",
            "nationalID": "1234567890",
            "family_history": True,
            "treatment_histories": treatment_histories
        }

        create_response = self.client.post(reverse('records_ops'), create_data, format='json')
        
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        # Extract the ID of the created record
        medical_record_data = json.loads(create_response.data["medical_record"])
        created_record_id = medical_record_data["id"]
        # Create an admin user
        admin_user = User.objects.create(
            email="admin@example.com",
            password=make_password("password123"),
            is_email_verified=True,
            role=User.TYPE_ADMIN
        )
        self.client.force_authenticate(user=admin_user)


        # Call the delete endpoint
        delete_response = self.client.delete(reverse('patient_record', kwargs={'id': created_record_id}))

        # Assert that the request was successful
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        get_response = self.client.get(reverse('patient_record', kwargs={'id': created_record_id}))
        self.assertEqual(get_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(get_response.data["message"], "There is no record with this ID.")




# class ThrepayTestsViewTests(APITestCase):

#     def setUp(self):
#         self.user = User.objects.create_user(username="testuser", password="testpassword")
#         self.pationt = Pationt.objects.create(user=self.user)
#         self.client = APIClient()
#         self.client.force_authenticate(user=self.user)

#     def test_get_therapy_tests_success(self):
#         TherapyTests.objects.create(pationt=self.pationt, MBTItest="INTJ")
#         response = self.client.get("/TherapyTests/tests/")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn("TherapTests", response.data)

#     def test_get_therapy_tests_no_data(self):
#         response = self.client.get("/TherapyTests/tests/")
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# class GlasserTestViewTests(APITestCase):


#     def setUp(self):
#         self.user = User.objects.create(
#             email="testuser@example.com",
#             password=make_password("oldpassword123"),
#             is_email_verified=True,
#             role=User.TYPE_USER,
#             date_of_birth=date(1990, 1, 1),
#             firstname="Test",
#             lastname="Name"
#         )
#         self.client = APIClient()
#         self.client.force_authenticate(user=self.user)
#         self.pationt = Pationt.objects.create(user=self.user)
#         self.data  = {
#                     "data": json.dumps({
#                         "1": {"category": "love", "res": 2},
#                         "2": {"category": "survive", "res": 5},
#                         "3": {"category": "freedom", "res": 4},
#                         "4": {"category": "power", "res": 2},
#                         "5": {"category": "fun", "res": 1},
#                         "6": {"category": "love", "res": 4},
#                         "7": {"category": "survive", "res": 3},
#                         "8": {"category": "freedom", "res": 5},
#                         "9": {"category": "power", "res": 3},
#                         "10": {"category": "fun", "res": 2},
#                         "11": {"category": "love", "res": 1},
#                         "12": {"category": "survive", "res": 5},
#                         "13": {"category": "freedom", "res": 3},
#                         "14": {"category": "power", "res": 2},
#                         "15": {"category": "fun", "res": 5},
#                         "16": {"category": "love", "res": 4},
#                         "17": {"category": "survive", "res": 3},
#                         "18": {"category": "freedom", "res": 5},
#                         "19": {"category": "power", "res": 4},
#                         "20": {"category": "fun", "res": 3},
#                         "21": {"category": "love", "res": 3},
#                         "22": {"category": "survive", "res": 4},
#                         "23": {"category": "freedom", "res": 3},
#                         "24": {"category": "power", "res": 2},
#                         "25": {"category": "fun", "res": 1}
#                     })
#                 }


#     def test_create_glasser_test_success(self):
#         response = self.client.post("https://eniacgroup.ir/TherapyTests/glasser/", self.data,format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         logger.warning(response)
#         self.assertIn("result", response.data)

#     def test_retrieve_glasser_test_success(self):
#         # First, create the GlasserTest with a POST request
#         post_response = self.client.post("https://eniacgroup.ir/TherapyTests/glasser/", self.data, format='json')
#         self.assertEqual(post_response.status_code, status.HTTP_200_OK)

#         # Perform a GET request to retrieve the GlasserTest
#         response = self.client.get("https://eniacgroup.ir/TherapyTests/glasser/")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Deserialize the GlasserTest object manually to verify its structure
        # logger.warning(response)
        # glasser_data = response.data.get("glasser")
        # self.assertIsInstance(glasser_data, dict)
        # self.assertIn("love", glasser_data)
        # self.assertIn("survive", glasser_data)
        # self.assertIn("freedom", glasser_data)
        # self.assertIn("power", glasser_data)
        # self.assertIn("fun", glasser_data)

        # # Validate specific values (adjust based on your implementation logic)
        # self.assertEqual(glasser_data["love"], 2.75)  # Adjust as per your averaging logic
        # self.assertEqual(glasser_data["survive"], 4.0)  # Adjust as per your averaging logic
        # self.assertEqual(glasser_data["freedom"], 4.25)  # Adjust as per your averaging logic
        # self.assertEqual(glasser_data["power"], 2.75)  # Adjust as per your averaging logic
        # self.assertEqual(glasser_data["fun"], 3.25)  # Adjust as per your averaging logic



# class PHQ9testViewTests(APITestCase):

#     def setUp(self):
#         self.user = User.objects.create(
#             email="testuser@example.com",
#             password=make_password("oldpassword123"),
#             is_email_verified=True,
#             role=User.TYPE_USER,
#             date_of_birth=date(1990, 1, 1),
#             firstname="Test",
#             lastname="Name"
#         )
#         self.client = APIClient()
#         self.client.force_authenticate(user=self.user)
#         self.pationt = Pationt.objects.create(user=self.user)

#     def test_create_phq9_test_success(self):
#         data = {"1": 3, "2": 2, "3": 1, "4": 0, "5": 3, "6": 2, "7": 1, "8": 0, "9": 3}
#         response = self.client.post("https://eniacgroup.ir/TherapyTests/phq9/", data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn("result", response.data)

#     def test_retrieve_phq9_test_success(self):
#         TherapyTests.objects.create(pationt=self.pationt, phq9=15)
#         response = self.client.get("https://eniacgroup.ir/TherapyTests/phq9/")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn("type", response.data)


class GetMBTItestViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            email="testuser@example.com",
            password=make_password("oldpassword123"),
            is_email_verified=True,
            role=User.TYPE_USER,
            date_of_birth=date(1990, 1, 1),
            firstname="Test",
            lastname="Name"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.pationt = Pationt.objects.create(user=self.user)

    def test_create_mbti_test_success(self):
        data = {1: 'a', 2: 'b', 3: 'b', 4: 'a', 5: 'b', 6: 'b', 7: 'a',
                8: 'b', 9: 'a', 10: 'b', 11: 'a', 12: 'b', 13: 'b', 14: 'b',
                15: 'a', 16: 'b', 17: 'b', 18: 'a', 19: 'b', 20: 'a',
                21: 'b', 22: 'b', 23: 'a', 24: 'b', 25: 'b', 26: 'b', 27: 'a',
                28: 'b', 29: 'a', 30: 'b', 31: 'a', 32: 'b', 33: 'b',
                34: 'a', 35: 'b', 36: 'b', 37: 'b', 38: 'b', 39: 'b', 40: 'b',
                41: 'b', 42: 'b', 43: 'b', 44: 'b', 45: 'b', 46: 'b',
                47: 'b', 48: 'b', 49: 'b', 50: 'b', 51: 'b', 52: 'b', 53: 'a',
                54: 'b', 55: 'a', 56: 'b', 57: 'a', 58: 'b', 59: 'b',
                60: 'b', 61: 'a', 62: 'b', 63: 'b', 64: 'a', 65: 'b', 66: 'b',
                67: 'a', 68: 'b', 69: 'a', 70: 'a'}
        response = self.client.post(reverse('MBTI'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("result", response.data)

    def test_retrieve_mbti_test_success(self):
        TherapyTests.objects.create(pationt=self.pationt, MBTItest="INFP")
        response = self.client.get(reverse('MBTI'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("type", response.data)
