from django.shortcuts import render,redirect
from django.http import JsonResponse
from PIL import Image
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Patient,PatientImage,Doctor
from .forms import PatientForm,DoctorCreationForm,ExaminationTechnicianForm,ExaminationLoginForm,ChartIDSearchForm
from django.shortcuts import get_object_or_404
from .forms import DoctorLoginForm,ExaminationTechnician
from django.contrib.auth import authenticate, login
from django.http import HttpResponseForbidden
import os

import onnxruntime as ort
import numpy as np

idx_to_class = {
    0: "all_benign",
    1: "all_early",
    2: "all_pre",
    3: "all_pro"
}

# ==============================
# ✅ importの順番を修正（先にimport）
# ==============================
import onnxruntime as ort
import numpy as np

# ==============================
# ✅ ONNXモデル読み込み
# ==============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

model_path = os.path.join(BASE_DIR, "model_quantized.onnx")

onnx_session = ort.InferenceSession(model_path)



def preprocess(image):
    image = image.resize((224, 224))
    image = np.array(image).astype(np.float32) / 255.0
    
    # 正規化（あなたの設定に合わせる）
    image = (image - 0.5) / 0.5
    
    # (H, W, C) → (C, H, W)
    image = np.transpose(image, (2, 0, 1))
    
    # バッチ次元追加
    image = np.expand_dims(image, axis=0)
    
    return image

#2
class_to_japanese = {
    "all_benign": "良性",
    "all_early": "初期がん",
    "all_pre": "前がん状態",
    "all_pro": "進行がん"
}

def index(request):
    return render(request,'index.html')

def predict_image_view(request):
    '''
    ・POSTで画像がアップロードされた時、PyTorchモデルを用いて画像を判定
    ・推論結果をJSON形式で返す。
    '''
    
    #画像がアップロードされたときの処理に入る条件
    #POSTメソッドであり、FILES（アップロードファイルの辞書）にimageキーが含まれているかを確認
    if request.method == 'POST' and request.FILES.get('image'):
        
        #送信された画像ファイルを開く
        #.convert('RGB') によって白黒などの画像もカラー（3チャンネル）として扱うように変換
        image = Image.open(request.FILES['image']).convert('RGB')

        #モデルに入力できるように画像を前処理する関数を定義
        #Resize((224, 224)): 画像サイズを固定
        #ToTensor(): NumPy配列をPyTorchテンソルに変換
        #Normalize((0.5,), (0.5,)): 平均0.5、標準偏差0.5で正規化
        

        #画像を前処理してテンソル化し、unsqueeze(0) で1次元追加
        #.to(device) によりCPUかGPUか自動で選択されたデバイスに転送
        input_numpy = preprocess(image)

        #推論時に使う
        outputs = onnx_session.run(None, {"input": input_numpy})
        outputs = outputs[0]
        
        predicted = np.argmax(outputs, axis=1)
        predicted_class = idx_to_class[int(predicted[0])]

        return JsonResponse({'result': predicted_class})

    return render(request, 'upload.html')

#本アプリは、Kaggleにて公開されている Obuli Sai Naren 氏による「Multi Cancer Dataset」を使用しています。
#このデータセットは CC BY-NC-SA 4.0（表示・非営利・継承） ライセンスのもとで提供されています。
#https://www.kaggle.com/datasets/obulisainaren/multi-cancer



def is_admin(user):
    '''
    ・Djangoユーザーが管理者かどうかを判定
    '''
    return user.is_superuser  # 管理者のみ許可

@login_required
@user_passes_test(is_admin)
def create_patient(request):
    '''
    ログインかつ管理者のみ、PatientFormから患者情報を新規作成できる
    '''
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('patient_list')
    else:
        form = PatientForm()
    return render(request, 'create_patient.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def patient_list(request):
    '''
    ・全患者データを一覧表示(管理者専用)
    '''
    patients = Patient.objects.all()
    return render(request, 'patient_list.html', {'patients': patients})


@login_required
def patient_detail(request, pk):
    '''
    患者の詳細情報を表示
    '''
    patient = get_object_or_404(Patient, pk=pk)

    # 権限に応じたrole文字列の設定
    if request.user.is_superuser:
        role = 'admin'
    elif hasattr(request.user, 'doctor'):
        role = 'doctor'
    elif hasattr(request.user, 'examinationtechnician'):  # モデル名に合わせて変更
        role = 'examination'
    else:
        role = 'unknown'

    return render(request, 'patient_detail.html', {
        'patient': patient,
        'role': role,
    })



@login_required
def predict_for_patient(request, pk):
    '''
    ・特定の患者に対して画像をアップロードしてがん種を予測、結果をDB保存
    '''
    patient = get_object_or_404(Patient, pk=pk)

    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']

        # Pillowで画像を読み込んで前処理
        image = Image.open(image_file).convert('RGB')
        input_numpy = preprocess(image)
        

        # 予測
       
        
        outputs = onnx_session.run(None, {"input": input_numpy})
        outputs = outputs[0]
        
        
        predicted = np.argmax(outputs, axis=1)
        predicted_class = idx_to_class[int(predicted[0])]
        
        predicted_japanese = class_to_japanese.get(predicted_class, "不明")

        # DB保存（予測結果つき）
        patient_image = PatientImage.objects.create(
            patient=patient,
            image=image_file,
            prediction=predicted_japanese
        )
        
        patient.latest_prediction = predicted_japanese
        patient.save()
        
        # 権限に応じたrole文字列の設定
        if request.user.is_superuser:
            role = 'admin'
        elif hasattr(request.user, 'doctor'):
            role = 'doctor'
        elif hasattr(request.user, 'examinationtechnician'):  # モデル名に合わせて変更
            role = 'examination'
        else:
            role = 'unknown'

        return render(request, 'patient_detail.html', {
            'patient': patient,
            'prediction': predicted_japanese,
            'role':role
        })

    return redirect('patient_detail', pk=pk)


@login_required#ログインを必須にする
@user_passes_test(is_admin)#is_admin 関数で「スーパーユーザー（管理者）」であるかをチェックすることで、管理者しかDoctor作成画面にアクセスできない
def create_doctor(request):
    '''
    ・管理者のみが新しい医師アカウントを作成できる画面と処理
    '''
    #フォームが送信されたとき（＝POSTメソッド）の処理分岐
    if request.method == 'POST':
        #送信されたデータ（request.POST）を使って DoctorCreationForm のインスタンスを作成
        form = DoctorCreationForm(request.POST)
        #入力がバリデーション（例：空欄チェック・文字数など）を通過したか確認
        if form.is_valid():
            form.save()#モデルの保存処理を実行
            return redirect('patient_list')  # 一覧ページがあれば
    else:
        #GETメソッド（つまりフォームの表示）のときは、空のフォームを表示する準備
        form = DoctorCreationForm()
    #create_doctor.html テンプレートにフォームを渡して表示
    return render(request, 'create_doctor.html', {'form': form})

'''
医師アカウント専用のログイン処理
'''
def doctor_login_view(request):
    if request.method == 'POST':#フォームが「送信された」場合（＝POSTメソッドのとき）の処理に入る条件
        form = DoctorLoginForm(request.POST)
        if form.is_valid():
            
            #フォーム内で username として定義されたフィールドの値を取得
            username = form.cleaned_data['username']
            
            #form.cleaned_data['password'] は、フォーム内で password として定義されたフィールドの値を取得
            password = form.cleaned_data['password']
            
            #authenticate()：username と password を使ってユーザーを認証
            user = authenticate(request, username=username, password=password)
            
            #user認証に成功し、userがdoctor属性を持っていた場合
            if user is not None and hasattr(user, 'doctor'):
                #login(request,user)：userをログイン状態にする
                login(request, user)
                return redirect('doctor_dashboard')  # ログイン後のページ名
            else:
                form.add_error(None, "医師アカウントではないか、認証情報が正しくありません。")
    else:
        form = DoctorLoginForm()
    return render(request, 'doctor_login.html', {'form': form})

'''
ログイン済みの医師が、自分の患者一覧を見るためのページ
'''
@login_required
def doctor_dashboard(request):
    #request.userがdoctor属性を持っていない場合
    #Djangoは、OneToOneField, ForeignKey, ManyToManyField などの関連フィールドを定義すると、関連モデルから逆参照できるように自動で属性を追加
    #逆参照の際には、自動で 関連名が「小文字」
    if not hasattr(request.user, 'doctor'):
        return HttpResponseForbidden("このページは医師専用です")

    #request.userのdoctor属性を取得
    doctor = request.user.doctor
    
    # フィルター用パラメータを取得（GETパラメータから）
    prediction_filter = request.GET.get('latest_prediction')
    
    patients = Patient.objects.filter(doctor=doctor)

    if prediction_filter:
        patients = patients.filter(latest_prediction=prediction_filter)
        
    return render(request, 'doctor_dashboard.html', {
        'doctor': doctor,
        'patients': patients,
        'selected_prediction': prediction_filter,
    })

@login_required
@user_passes_test(is_admin)
def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(request, 'doctor_list.html', {'doctors': doctors})

@login_required
@user_passes_test(is_admin)
def examination_list(request):
    examinations = ExaminationTechnician.objects.all()
    return render(request, 'examination_list.html', {'examinations': examinations})


@login_required#ログインを必須にする
@user_passes_test(is_admin)#is_admin 関数で「スーパーユーザー（管理者）」であるかをチェックすることで、管理者しかDoctor作成画面にアクセスできない
def create_examination(request):
    '''
    ・管理者のみが新しい検査技師アカウントを作成できる画面と処理
    '''
    #フォームが送信されたとき（＝POSTメソッド）の処理分岐
    if request.method == 'POST':
        #送信されたデータ（request.POST）を使って DoctorCreationForm のインスタンスを作成
        form = ExaminationTechnicianForm(request.POST)
        #入力がバリデーション（例：空欄チェック・文字数など）を通過したか確認
        if form.is_valid():
            form.save()#モデルの保存処理を実行
            return redirect('patient_list')  # 一覧ページがあれば
    else:
        #GETメソッド（つまりフォームの表示）のときは、空のフォームを表示する準備
        form = ExaminationTechnicianForm()
    #create_doctor.html テンプレートにフォームを渡して表示
    return render(request, 'create_examination.html', {'form': form})


'''
検査技師アカウント専用のログイン処理
'''
def examination_login_view(request):
    if request.method == 'POST':#フォームが「送信された」場合（＝POSTメソッドのとき）の処理に入る条件
        form = ExaminationLoginForm(request.POST)
        if form.is_valid():
            
            #フォーム内で username として定義されたフィールドの値を取得
            username = form.cleaned_data['username']
            
            #form.cleaned_data['password'] は、フォーム内で password として定義されたフィールドの値を取得
            password = form.cleaned_data['password']
            
            #authenticate()：username と password を使ってユーザーを認証
            user = authenticate(request, username=username, password=password)
            
            #user認証に成功し、userがdoctor属性を持っていた場合
            if user is not None and hasattr(user, 'examinationtechnician'):
                #login(request,user)：userをログイン状態にする
                login(request, user)
                return redirect('examination_dashboard')  # ログイン後のページ名
            else:
                form.add_error(None, "検査技師アカウントではないか、認証情報が正しくありません。")
    else:
        form = ExaminationLoginForm()
    return render(request, 'examination_login.html', {'form': form})

@login_required
def examination_dashboard(request):
    #request.userがdoctor属性を持っていない場合
    #Djangoは、OneToOneField, ForeignKey, ManyToManyField などの関連フィールドを定義すると、関連モデルから逆参照できるように自動で属性を追加
    #逆参照の際には、自動で 関連名が「小文字」
    if not hasattr(request.user, 'examinationtechnician'):
        return HttpResponseForbidden("このページは検査技師専用です")
    patient = ''
    #request.userのdoctor属性を取得
    examination = request.user.examinationtechnician
    prediction_filter = request.POST.get('clinical_records')

    if prediction_filter:
        patient = Patient.objects.filter(chart_id=prediction_filter)
    
    #patients = Patient.objects.filter(doctor=doctor)

    return render(request, 'examination_dashboard.html', {
        'examination': examination,
        'patient': patient
    })

def search_patient_by_chart_id(request):
    form = ChartIDSearchForm()
    patient = None

    if request.method == 'POST':
        form = ChartIDSearchForm(request.POST)
        if form.is_valid():
            chart_id = form.cleaned_data['chart_id']
            try:
                patient = Patient.objects.get(chart_id=chart_id)
            except Patient.DoesNotExist:
                patient = None  # テンプレート側で「見つかりませんでした」と表示可能

    return render(request, 'search_patient.html', {
        'form': form,
        'patient': patient
    })