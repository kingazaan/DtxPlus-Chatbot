from django.db import models

# Create your models here.
class Patient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    doctor_name = models.CharField(max_length=100, default="Dr. Smith")
    email = models.CharField(max_length=100, null=True)
    date_of_birth = models.CharField(max_length=100)
    phone_number = models.IntegerField(null=True)
    medical_condition = models.TextField()
    medication_regimen = models.TextField()
    last_appointment = models.DateTimeField()
    next_appointment = models.DateTimeField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Chat(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    sender = models.CharField(max_length=512, default="blank message")    # used after submitting message to chatbot, can increase token size later
    entities = models.JSONField(null=True, blank=True)  # Store entities as JSON

    def __str__(self):
        return f"{self.sender} at {self.timestamp}"