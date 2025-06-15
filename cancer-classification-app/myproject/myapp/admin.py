from django.contrib import admin
from .models import Doctor, Patient, PatientImage, ExaminationTechnician

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty')
    search_fields = ('user__username', 'specialty')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'chart_id', 'doctor', 'latest_prediction')
    search_fields = ('name', 'chart_id')
    list_filter = ('doctor',)

@admin.register(PatientImage)
class PatientImageAdmin(admin.ModelAdmin):
    list_display = ('patient', 'uploaded_at', 'prediction')
    list_filter = ('uploaded_at',)
    search_fields = ('patient__name',)

@admin.register(ExaminationTechnician)
class TechnicianAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty')
    search_fields = ('user__username', 'specialty')

