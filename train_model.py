# -*- coding: utf-8 -*-
"""
Created on Sun May 31 01:16:41 2026

@author: PC
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

# ==========================================
# 1. ĐỌC VÀ LÀM SẠCH DỮ LIỆU
# ==========================================
print("Đang tải dữ liệu từ file data.csv...")
try:
    df = pd.read_csv('data.csv')
except FileNotFoundError:
    print("LỖI: Không tìm thấy file 'data.csv'. Vui lòng kiểm tra lại thư mục!")
    exit()

# Xóa các dòng bị lỗi (nếu có giá trị rỗng)
df = df.dropna()

# ==========================================
# 2. PHÂN TÁCH ĐẶC TRƯNG VÀ NHÃN
# ==========================================
# Lấy 4 cột đầu tiên làm Đặc trưng (Features)
X = df[['Temperature', 'Humidity', 'Gas_Analog', 'Flame_Analog']]
# Lấy cột cuối cùng làm Nhãn (Labels)
y = df['Label']

# Chia tập dữ liệu: 80% để Huấn luyện (Train), 20% để Kiểm tra (Test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ==========================================
# 3. CHUẨN HÓA DỮ LIỆU
# ==========================================
# Đưa các giá trị về cùng một thang đo để AI học dễ hơn
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ==========================================
# 4. HUẤN LUYỆN MÔ HÌNH RANDOM FOREST
# ==========================================
print("Đang huấn luyện mô hình Random Forest...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# ==========================================
# 5. ĐÁNH GIÁ MÔ HÌNH
# ==========================================
y_pred = model.predict(X_test_scaled)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n--- KẾT QUẢ ĐÁNH GIÁ ---")
print(f"Độ chính xác (Accuracy): {accuracy * 100:.2f}%\n")
print("Báo cáo chi tiết:")
print(classification_report(y_test, y_pred, target_names=['Bình thường', 'Rò rỉ Gas', 'Hỏa hoạn']))

# ==========================================
# 6. LƯU MÔ HÌNH ĐỂ SỬ DỤNG CHO DEMO REAL-TIME
# ==========================================
joblib.dump(model, 'fire_detection_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
print("\nĐã đóng gói và lưu mô hình thành công (fire_detection_model.pkl và scaler.pkl)!")

# ==========================================
# 7. TRỰC QUAN HÓA BẰNG BIỂU ĐỒ
# ==========================================
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Bình thường', 'Gas', 'Cháy'], 
            yticklabels=['Bình thường', 'Gas', 'Cháy'])
plt.title('Ma trận nhầm lẫn (Confusion Matrix)')
plt.ylabel('Nhãn thực tế (Thực tế là...)')
plt.xlabel('Nhãn dự đoán (AI đoán là...)')
plt.show()