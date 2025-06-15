\

## 📁 フォルダ構成

```
cancer-classification-app/    # Djangoプロジェクト
model-learning/               # モデルの学習用フォルダ
```

---

## 📚 データの学習準備

- Python 3.12.11
- GPU：NVIDIA GeForce RTX 3060 Ti
- OS：Windows 11 Home（バージョン 10.0.22631）
- メモリ：16GB RAM

---

## 🖥 動作確認済み環境

- Python 3.11.3
- OS：Windows 11 Home（バージョン 10.0.22631）
- CPU：Intel Core i7-12700F（12th Gen / 12 コア 20 スレッド）
- メモリ：16GB RAM

---

### 🔗 データセットについて

本アプリは、Kaggle にて公開されている Obuli Sai Naren 氏による  
[Multi Cancer Dataset](https://www.kaggle.com/datasets/obulisainaren/multi-cancer) を使用しています。  
このデータセットは **CC BY-NC-SA 4.0（表示・非営利・継承）** ライセンスで提供されています。

---

### ① Kaggle API トークンを取得

1. [Kaggle](https://www.kaggle.com/) にログイン
2. プロフィールアイコン → `Account`
3. 「**Create New API Token**」をクリック
4. `kaggle.json` ファイルをダウンロード

---

### ② kaggle.json の配置と CLI セットアップ

```bash
pip install kaggle
```

保存先（フォルダがなければ作成）：

```
Windows: C:\\Users\\<ユーザー名>\\.kaggle\\kaggle.json
```

---

### ③ データセットのダウンロード

#### ▷ コマンドでダウンロード（推奨）

```bash
kaggle datasets download -d obulisainaren/multi-cancer
unzip multi-cancer.zip -d multi_cancer_data
```

#### ▷ 手動ダウンロード

1. Kaggle ページ：[こちら](https://www.kaggle.com/datasets/obulisainaren/multi-cancer)
2. Download ボタンで取得
3. ZIP を展開

---

### ④ データセットの移動

```bash
multi_cancer_data/Multi Cancer/Multi Cancer/Acute Lymphoblastic Leukemia/
```

を以下へ移動：

```
model-learning/data/
```

---

## 📦 インストールパッケージ

```txt
torch
torchvision
scikit-learn
seaborn
matplotlib
numpy
```

---

## ⚡ GPU 対応の PyTorch のインストール

### ✅ ステップ 1：CUDA のバージョンを確認

```bash
nvidia-smi
```

例：CUDA Version: 12.2

---

### ✅ ステップ 2：公式サイトでインストールコマンドを取得

👉 https://pytorch.org/get-started/locally/

例：CUDA 12.1 + pip

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

---

### 💡 補足

CPU 用：

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

GPU 確認コード：

```python
import torch
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))
```

---

## ⚙️ Django プロジェクトの動作手順

### ① プロジェクトをクローン

```bash
git clone https://github.com/NK-kimiya/cancer-classification-portfolio.git
cd cancer-classification-portfolio/cancer-classification-app
```

---

### ② 仮想環境を作成・起動

```bash
python -m venv venv
venv\\Scripts\\activate  # Windowsの場合
```

---

### ③ パッケージをインストール

```bash
pip install -r requirements.txt
```

---

### ④ マイグレーション実行

```bash
cd myproject
python manage.py makemigrations
python manage.py migrate
```

---

### ⑤ 管理ユーザーの作成（任意）

```bash
python manage.py createsuperuser
```

---

### ⑥ サーバー起動

```bash
python manage.py runserver
```

アクセス：

```
http://127.0.0.1:8000/
```
