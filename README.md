# Machine-learning
Hệ thống dự báo cháy qua MQTT
# 🔥 IoT Fire & Gas Leak Early Warning System

Dự án ứng dụng Machine Learning kết hợp IoT để nhận diện và cảnh báo sớm sự cố rò rỉ khí gas và hỏa hoạn trong môi trường thực tế.

## 🛠 Phần cứng sử dụng
* Vi điều khiển: ESP32
* Cảm biến: DHT11 (Nhiệt/Ẩm), MQ-2 (Khí Gas), Flame Sensor (Cảm biến lửa).
* Nguồn: Nguồn pin độc lập qua module hạ áp L298N.

## 🧠 Mô hình Machine Learning
* **Thuật toán:** Random Forest Classifier.
* **Đầu vào (Features):** Nhiệt độ, Độ ẩm, Khí Gas thô, Ánh sáng lửa.
* **Đầu ra (Labels):** * `0`: BÌNH THƯỜNG
  * `1`: CẢNH BÁO RÒ RỈ GAS (Gas > 2000)
  * `2`: NGUY HIỂM: HỎA HOẠN
* **Độ chính xác mô hình:** >98%

## 🚀 Luồng hoạt động
1. ESP32 đọc cảm biến và gửi dữ liệu thô qua giao thức MQTT (Server `broker.emqx.io`).
2. Script Python lắng nghe MQTT, tiền xử lý và đưa vào mô hình `.pkl` để dự đoán trạng thái theo thời gian thực.
3. Nếu phát hiện sự cố, hệ thống sẽ đẩy thông báo khẩn cấp và hú còi qua Telegram API (có cơ chế cooldown 10s chống spam).

## 📁 Hướng dẫn chạy code
1. Nạp code C++ vào mạch ESP32.
2. Cài đặt các thư viện Python: `pip install paho-mqtt scikit-learn pandas numpy requests joblib`
3. Chạy file `main.py` để hệ thống bắt đầu giám sát.
