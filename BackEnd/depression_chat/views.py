from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
# from accounts.models import User
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.response import Response
from .models import Conversation, ConMessage
from .serializers import ConversionSerializer, ConMessageSerializer
from TherapyTests.models import TherapyTests
from counseling.models import Pationt
import os
import requests
from pydub import AudioSegment
from pydub.utils import which
# بارگذاری مدل و پردازنده
import soundfile as sf
AudioSegment.converter = which("ffmpeg")

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import mimetypes
import tempfile
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torch
import librosa
import tempfile
import numpy as np
import os
from django.utils import timezone
from .disorder_detector.stress_detector import (
    check_for_stress_in_text,
    load_stress_detector_model_tokenizer,
)
from .emotion.emotion_detection import (
    load_emotion_detector_model_tokenizer,
    predict_emotion_label,
    predict_emotion_of_texts,
    label_dict,
)
from .message_validator.message_validator import (
    load_validator_model_and_tokenizer,
    predict_validator_labels,
)
from dotenv import load_dotenv

import logging

logger = logging.getLogger(__name__)
load_dotenv()

validator_model, validator_tokenizer = load_validator_model_and_tokenizer()
emotion_model, emotion_tokenizer = load_emotion_detector_model_tokenizer()
disorder_tokenizer, disorder_model = load_stress_detector_model_tokenizer()

def is_wav_file(file_path):
    try:
        audio = AudioSegment.from_file(file_path, format="wav")
        return True
    except Exception:
        return False



# Step 1: Resample Audio to 16kHz
def resample_audio(input_path, output_path, target_sampling_rate=16000):
    """Resample audio file to target sampling rate."""
    try:
        # Load the audio file with its original sampling rate
        audio, original_sampling_rate = librosa.load(input_path, sr=None)

        # Resample if needed
        if original_sampling_rate != target_sampling_rate:
            audio = librosa.resample(audio, orig_sr=original_sampling_rate, target_sr=target_sampling_rate)

        # Save the resampled audio
        sf.write(output_path, audio, target_sampling_rate)
    except Exception as e:
        raise RuntimeError(f"Error during resampling: {str(e)}")

def process_audio_to_text(audio_file):
    """
    پردازش فایل صوتی به متن با استفاده از مدل Wav2Vec2
    """
    try:
        # Ensure audio file is resampled to 16kHz
        resampled_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        resample_audio(audio_file, resampled_file)

        # Load the resampled audio file
        audio_input, sample_rate = sf.read(resampled_file)

        # Process the audio
        input_values = processor(audio_input, sampling_rate=sample_rate, return_tensors="pt", padding=True).input_values

        # Perform inference
        with torch.no_grad():
            logits = model(input_values).logits

        # Get predicted IDs
        predicted_ids = torch.argmax(logits, dim=-1)

        # Decode the predicted IDs to text
        transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]

    except Exception as e:
        raise RuntimeError(f"Error during audio processing: {str(e)}")
    finally:
        # Cleanup the temporary resampled file
        if os.path.exists(resampled_file):
            os.remove(resampled_file)

    return transcription

# Initialize the processor and model
processor = Wav2Vec2Processor.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-persian")
model = Wav2Vec2ForCTC.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-persian")

class ProcessWavVoiceView(APIView):
    def post(self, request, *args, **kwargs):
        voice_file = request.FILES.get('voice_file')

        if not voice_file:
            return Response(
                {"message": "No voice file provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ذخیره موقت فایل برای پردازش
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav_file:
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    # ذخیره فایل آپلود شده
                    for chunk in voice_file.chunks():
                        temp_file.write(chunk)
                    temp_file.seek(0)

                    # شناسایی و تبدیل به WAV
                    try:
                        audio = AudioSegment.from_file(temp_file.name)
                        audio.export(temp_wav_file.name, format="wav")  # تبدیل به WAV
                    except Exception as e:
                        return Response(
                            {"message": f"Error converting audio file: {str(e)}"},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                # مسیر فایل WAV
                wav_file_path = temp_wav_file.name

            # پردازش فایل صوتی به متن
            processed_text = process_audio_to_text(wav_file_path)

        except Exception as e:
            return Response(
                {"message": f"Error processing audio file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        finally:
            # حذف فایل موقت WAV
            if os.path.exists(wav_file_path):
                os.remove(wav_file_path)

        return Response(
            {
                "message": "Audio file processed successfully.",
                "processed_text": processed_text
            },
            status=status.HTTP_200_OK
        )

class DepressionChatView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def create_new_conversation(self, request):

        User = get_user_model()
        try:
            user = request.user
            if user.role != User.TYPE_USER:
                return Response(
                    {"message": "This bot is only for patients."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            conversation = Conversation.objects.create(
                owner=user,
                name="",
                created_at=timezone.now(),
            )
            serializer = ConversionSerializer(conversation)

            return Response(
                {
                    "message": "Conversation created successfully!",
                    "conversation": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": f"Unexpected error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # Function to calculate the weighted average of emotion or disorder over the chat history
    def calculate_weighted_average(
        self, chats: list[ConMessage], feature: str, decay_factor: float = 0.9
    ):
        chats = [chat for chat in chats if chat.message != ""]
        weighted_average = dict()

        for label in getattr(chats[0], feature).keys():
            total_weight = 0
            weighted_scores = list()

            for chat in chats:
                # if chat.response == self.first_server_prompt:
                #     continue
                day_diff = (timezone.now() - chat.timestamp).days
                weight = np.exp(-decay_factor * day_diff)
                weighted_scores.append(getattr(chat, feature)[label] * weight)
                total_weight += weight

            # Calculate the weighted average
            weighted_average[label] = (
                sum(weighted_scores) / total_weight if total_weight != 0 else 0
            )
        return weighted_average

    # Function to interact with OpenAI API to get a response based on chat history and patient message
    def ask_openai(self, chat_obj: ConMessage, chat_history, window_size: int = None):
        chat_history_size = len(chat_history)
        if window_size and chat_history_size >0 :
            chat_history = chat_history.order_by("-id")[:window_size]
        messages = list()
        # Prepare the chat history to be sent to OpenAI
        if chat_history_size >0 : 
            for chat in chat_history:
                messages.append({"role": "user", "content": chat.message})
                messages.append({"role": "system", "content": chat.response})

        # If there are more than 3 chats, include emotional and disorder statuses in the prompt
        if chat_history_size > 3:
            average_emotion_prob = self.calculate_weighted_average(
                list(chat_history) + [chat_obj], "emotion"
            )
            average_disorder_prob = self.calculate_weighted_average(
                list(chat_history) + [chat_obj], "disorder"
            )

            prompt = f"""
    The previous messages are the chat history between a patient and a psychologist.
    Suppose you are a professional psychologist. Based on the following information,
    respond to the patient with a short message.(Prevent to say 'Hi' in each message. And only speak in persian)

    Emotional status: {average_emotion_prob}
    Mental disorder status: {average_disorder_prob}
    Patient message: {chat_obj.message}

    Speak more sincerely and informally, and use emojis to create a friendlier tone. Avoid mentioning the user's stress or emotion levels directly, and don't discuss them.
    Just be aware of these levels to respond appropriately.
    """
        else:
            prompt = f"""
    The previous messages are the chat history between a patient and a psychologist.
    Suppose you are a professional psychologist. Based on the following information,
    respond to the patient with a short message.(Prevent to say 'Hi' in each message. And only speak in persian)

    Patient message: {chat_obj.message}
    """
        load_dotenv()
        RAPID_API_KEY = os.getenv("RAPID_API_KEY")
        logger.warning( "******************************* key {}".format( RAPID_API_KEY) ) 
        messages.append({"role": "user", "content": prompt})
        RAPID_API_HOST = (
            "cheapest-gpt-4-turbo-gpt-4-vision-chatgpt-openai-ai-api.p.rapidapi.com"
        )
        RAPID_API_URL = f"https://{RAPID_API_HOST}/v1/chat/completions"

        payload = {
            "messages": messages,
            "model": "gpt-4o",
            "max_tokens": 100,
            "temperature": 0.9,
        }
        logger.warning(f"**************** this is rapid key : {RAPID_API_KEY}")
        headers = {
            "x-rapidapi-key": RAPID_API_KEY,
            "x-rapidapi-host": RAPID_API_HOST , 
            "Content-Type": "application/json",
        }

        response = requests.post(RAPID_API_URL, json=payload, headers=headers)
        logger.warning(f"response status code : {response} ") 
        if response.status_code == 200:
            result = response.json()
            answer = (
                result.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )
            print(f"Response: {answer}")
            return answer
        else:
            print(f"Error: {response.status_code}")
            print(f"Response Text: {response.text}")
    
            return Response(
                {"message": f"there is problem. {response}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def Message(self, request, *args, **kwargs):
        User = get_user_model()
        user = request.user
        if user.role != User.TYPE_USER:
            return Response(
                {"message": "This bot is only for patients."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        conversion_id = kwargs.get("pk")
        conversation = Conversation.objects.filter(id=conversion_id)
        if not conversation.exists():
            return Response(
                {"message": "There is no conversation with this ID."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            patient = Pationt.objects.get(user=user)
        except Pationt.DoesNotExist:
            return Response(
                {"message": "No patient associated with this user."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        therapy_test = TherapyTests.objects.filter(pationt=patient)

        if not therapy_test.exists():
            return Response(
                {
                    "message": "you did not have any Tests yet, first take the phq9 test."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        therapy_test = therapy_test.first()
        if (timezone.now() - therapy_test.phq9_created_at).days >= 7:
            return Response(
                {
                    "message": "you did not have any Tests more than 7 days before, first take the phq9 test."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        conversation = conversation.first()
        user_msg = request.data.get("user_msg")
        if conversation.name == "":
            conversation.name = user_msg

        message = request.data.get("message")
        v_disorder = check_for_stress_in_text(
            message, disorder_model, disorder_tokenizer
        )
        v_emotion = predict_emotion_label(message, emotion_model, emotion_tokenizer)

        chats = ConMessage.objects.filter(conversation = conversation)
        if not chats.exists():
            chats = []

        chat = ConMessage.objects.create(
            user=user,
            conversation=conversation,
            message=message,
            timestamp=timezone.now(),
            emotion=v_emotion,
            disorder=v_disorder,
        )

        for _ in range(5):
            # Get a response from OpenAI based on the chat history and current message
            response = self.ask_openai(chat, chat_history=chats, window_size=20)
            validation = predict_validator_labels(
                response, validator_model, validator_tokenizer
            )
            if not validation:
                break
          
        chat.validation = validation
        chat.response = response
        chat.save()
        return Response({"message": message, "response": response})



    def Retrieve_conversation(self, request, *args, **kwargs):
        user = request.user
        User = get_user_model()
        if user.role != User.TYPE_USER:
            return Response(
                {"message": "This bot is only for patients."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        conversation = None
        conversation_id = kwargs.get("pk")
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response(
                {"message": "Conversation not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        chats = ConMessage.objects.filter(conversation = conversation )
        if not chats.exists():
            return Response(
                {"message": "There is not chats in this Conversation. make a new one"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = ConMessageSerializer(chats, many=True)
        return Response(
            {"conversations": serializer.data},
            status=status.HTTP_200_OK,
        )
    
    def delete(self, request, *args, **kwargs):
        
        User = get_user_model()
        user = request.user
        if user.role != User.TYPE_USER:
            return Response(
                {"message": "This bot is only for patients."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        conversation_id = kwargs.get("pk")
        try:

            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response(
                {"message": "Conversation not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
 
        if conversation.user != user:
            return Response(
                {"message": "You are not authorized to delete this conversation."},
                status=status.HTTP_403_FORBIDDEN,
            )
        ConMessage.objects.filter(conversation=conversation).delete()
        conversation.delete()
        return Response(
            {"message": "Conversation deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )
    
    
    def Retrieve_all_conversations(self, request, *args, **kwargs):
        user = request.user
        User = get_user_model()
        if user.role != User.TYPE_USER:
            return Response(
                {"message": "This bot is only for patients."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        conversations = Conversation.objects.filter(owner=user)
        if not conversations.exists():
            return Response(
                {"message": "There are no conversations for this user. Create a new one."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        serializer = ConversionSerializer(conversations, many=True)
        return Response(
            {"conversations": serializer.data},
            status=status.HTTP_200_OK,
        )
    
