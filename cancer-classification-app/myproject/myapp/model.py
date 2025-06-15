import torch
import torch.nn as nn
import os

# CNN構造（学習時と同じ）
class CNNModel(nn.Module):
    def __init__(self, num_classes=4):
        super(CNNModel, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.conv3 = nn.Conv2d(32, 64, 3, padding=1)
        self.fc1 = nn.Linear(64 * 28 * 28, 256)
        self.fc2 = nn.Linear(256, num_classes)

    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.pool(torch.relu(self.conv2(x)))
        x = self.pool(torch.relu(self.conv3(x)))
        x = x.view(-1, 64 * 28 * 28)
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# デバイスの設定
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# モデルのインスタンス化
model = CNNModel(num_classes=4)

# ✅ 修正点：モデルファイルのパスを正しく指定
model_path = os.path.join(os.path.dirname(__file__), "cnn_cancer_model.pth")

# モデルの読み込み
model.load_state_dict(torch.load(model_path, map_location=device))
model.to(device)
model.eval()

# クラスID → 名前
idx_to_class = {
    0: "all_benign",
    1: "all_early",
    2: "all_pre",
    3: "all_pro"
}

