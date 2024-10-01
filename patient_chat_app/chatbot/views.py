from django.shortcuts import render, redirect
from .models import Patient, Chat
from .services import process_query, extract_date_from_message, check_for_medical_conditions, update_patient_entities
from django.utils import timezone
from django.http import JsonResponse

def is_ajax(request):
    """Check if the request is an AJAX request."""
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'

def save_to_database(user_message, bot_response, patient):
    """Saves user messages and bot responses to models.py -> database"""
    Chat.objects.create(patient=patient, sender='patient', message=user_message, entities = update_patient_entities(patient, user_message))
    Chat.objects.create(patient=patient, sender='bot', message=bot_response)

def chat_view(request):
    # Get or create a dummy patient
    patient, created = Patient.objects.get_or_create(
        first_name="John",
        last_name="Doe",
        defaults={
            'date_of_birth': '1990-01-01',
            'phone_number': '1234567890',
            'email': 'johndoe@example.com',
            'medical_condition': 'Hypertension',
            'medication_regimen': 'Lisinopril twice a day',
            'last_appointment': timezone.now(),
            'next_appointment': timezone.now(),
            'doctor_name': 'Dr. Smith',
        }
    )

    # if 'new_chat_history' not in request.session:
    #     request.session['new_chat_history'] = []

    request.session['new_chat_history'] = []

    new_chat_history = request.session['new_chat_history']

    if request.method == "POST" and is_ajax(request):
        user_message = request.POST.get('message')

        # Check if the query is about appointment or medical changes
        query_flags = check_for_medical_conditions(user_message)

        if query_flags['appointment_related']:
            new_date = extract_date_from_message(user_message)
            if new_date:
                old_date = patient.next_appointment
                patient.next_appointment = new_date
                patient.save()
                bot_response = f"Appointment rescheduled from {old_date.strftime('%A, %B %d, %Y')} to {new_date.strftime('%A, %B %d, %Y')}."
                save_to_database(user_message, bot_response, patient)
            else:
                bot_response = "I couldn't find a valid date in your request. Please specify a new appointment date."
                save_to_database(user_message, bot_response, patient)
        elif query_flags['medical_related']:
            bot_response = f"You are on {patient.medication_regimen} for {patient.medical_condition}. Your doctor has been notified."
            save_to_database(user_message, bot_response, patient)
        else:
            # Process the query through the service
            bot_response = process_query(user_message, patient)
            save_to_database(user_message, bot_response, patient)

        # Save user and bot messages in chat history
        new_chat_history.append({'sender': 'patient', 'message': user_message, 'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S')})
        new_chat_history.append({'sender': 'bot', 'message': bot_response, 'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S')})

        # Save the updated session chat history
        request.session['new_chat_history'] = new_chat_history

        # Return the latest chat messages as JSON
        return JsonResponse({
            'user_message': user_message,
            'bot_response': bot_response,
            'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    return render(request, 'chat.html', {'chat_history': new_chat_history})
