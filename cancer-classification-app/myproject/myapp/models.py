from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialty = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username}（専門：{self.specialty}）"
    
class Patient(models.Model):
    name = models.CharField(max_length=100)
    chart_id = models.CharField(max_length=50)
    latest_prediction = models.CharField(max_length=100, blank=True, null=True) 
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name='patients') 

    def __str__(self):
        return f"{self.name}（ID: {self.chart_id}）"

class PatientImage(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('image') 
    uploaded_at = models.DateTimeField(auto_now_add=True)
    prediction = models.CharField(max_length=100, blank=True)  # ← これを追加済みか確認

class ExaminationTechnician(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialty = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username}（専門：{self.specialty}）"   