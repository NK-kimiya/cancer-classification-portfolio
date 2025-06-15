from django.urls import path
from .views import predict_image_view,create_patient,patient_list,patient_detail,predict_for_patient,create_doctor,doctor_login_view,doctor_dashboard,index,doctor_list,create_examination,examination_list,examination_login_view,examination_dashboard,search_patient_by_chart_id


urlpatterns = [
    path('', index, name='index'),
    path('predict/', predict_image_view, name='predict_image'),
    path('create/', create_patient, name='create_patient'),
    path('list/', patient_list, name='patient_list'),
    path('patients/<int:pk>/', patient_detail, name='patient_detail'),
    # 画像アップロードで予測する処理（POST専用）
    path('patient/<int:pk>/predict/', predict_for_patient, name='predict_for_patient'),
    path('create_doctor/', create_doctor, name='create_doctor'),
    path('doctor/login/', doctor_login_view, name='doctor_login'),
    path('examination/login/', examination_login_view, name='examination_login'),
    path('doctor/dashboard/', doctor_dashboard, name='doctor_dashboard'),
    path('examination/dashboard/', examination_dashboard, name='examination_dashboard'),
    path('doctors/', doctor_list, name='doctor_list'),
    path('examinations/', examination_list, name='examination_list'),
    path('create_examination/', create_examination, name='create_examination'),
    path('search-patient/', search_patient_by_chart_id, name='search_patient'),
]