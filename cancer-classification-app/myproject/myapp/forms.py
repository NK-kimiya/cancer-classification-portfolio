from django import forms
from .models import Patient
from django.contrib.auth.models import User
from .models import Doctor,ExaminationTechnician

'''
Patientモデルに対応したフォームを作成するためのクラス
'''
class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'chart_id', 'doctor']  # doctor を追加
        
        labels = {
            'name': '患者名',        # 'name' フィールドのラベルを '患者名' に変更
            'chart_id': 'カルテ番号', # 'chart_id' フィールドのラベルを 'カルテ番号' に変更
            'doctor': '担当医',      # 'doctor' フィールドのラベルを '主治医' に変更
        }

'''
ユーザー登録時に User と Doctor の2つのモデルを同時に作成するためのフォーム
'''  
class DoctorCreationForm(forms.ModelForm):
    #User モデルに関係する3つの情報を手動でフォームに追加
    username = forms.CharField(label='医師名', max_length=150) # ここでラベルを設定
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput) # ここでラベルを設定
    email = forms.EmailField(label='メールアドレス') # ここでラベルを設定

    class Meta:#Doctor モデルに対応するフォームフィールドを指定
        model = Doctor
        fields = ['specialty']#モデル内で保存されるのは specialty（専門分野）だけ
        

    #ModelForm の標準の save() メソッドを上書き
    # User インスタンスの作成
    #フォームを送信したときに、User と Doctor の両方を作成するための処理
    def save(self, commit=True):
        #入力されたフォームデータから User インスタンスを作成
        #create_user() は自動でパスワードをハッシュ化
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email'],
        )
        #Doctor モデルのインスタンスを、DBに保存せずに一度取得
        doctor = super().save(commit=False)
        #Doctor モデルの外部キー user に、上で作成した User を割り当て
        doctor.user = user
        #commit=True の場合のみ、データベースに Doctor インスタンスを保存
        if commit:
            doctor.save()
        #最後に Doctor インスタンスを返す
        return doctor

#医師アカウント専用のログインフォームを提供するためのクラス
class DoctorLoginForm(forms.Form):
    username = forms.CharField(max_length=150,label='ユーザー名')
    password = forms.CharField(widget=forms.PasswordInput,label='パスワード')
    
'''
ユーザー登録時に User と ExaminationTechnicianの2つのモデルを同時に作成するためのフォーム
'''  
class ExaminationTechnicianForm(forms.ModelForm):
    #User モデルに関係する3つの情報を手動でフォームに追加
    username = forms.CharField(label='医師名', max_length=150) # ここでラベルを設定
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput) # ここでラベルを設定
    email = forms.EmailField(label='メールアドレス') # ここでラベルを設定

    class Meta:#ExaminationTechnician モデルに対応するフォームフィールドを指定
        model = ExaminationTechnician
        fields = ['specialty']#モデル内で保存されるのは specialty（専門分野）だけ
        

    #ModelForm の標準の save() メソッドを上書き
    # User インスタンスの作成
    #フォームを送信したときに、User と Doctor の両方を作成するための処理
    def save(self, commit=True):
        #入力されたフォームデータから User インスタンスを作成
        #create_user() は自動でパスワードをハッシュ化
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email'],
        )
        #ExaminationTechnician モデルのインスタンスを、DBに保存せずに一度取得
        examinationTechnician = super().save(commit=False)
        #Doctor モデルの外部キー user に、上で作成した User を割り当て
        examinationTechnician.user = user
        #commit=True の場合のみ、データベースに Doctor インスタンスを保存
        if commit:
            examinationTechnician.save()
        #最後に Doctor インスタンスを返す
        return examinationTechnician
    
#検査技師アカウント専用のログインフォームを提供するためのクラス
class ExaminationLoginForm(forms.Form):
    username = forms.CharField(max_length=150,label='ユーザー名')
    password = forms.CharField(widget=forms.PasswordInput,label='パスワード')

#患者をカルテで検索するフォーム
class ChartIDSearchForm(forms.Form):
    chart_id = forms.CharField(label="カルテID", max_length=50)