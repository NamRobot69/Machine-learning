import joblib
import numpy as np
import sys
import warnings
import paho.mqtt.client as mqtt
import requests

warnings.filterwarnings('ignore')

# ==========================================
# 1. CẤU HÌNH TELEGRAM BOT (BÁO ĐỘNG RUNG CHUÔNG)
# ==========================================
# ⚠️ QUAN TRỌNG: Hãy điền đoạn mã Token và Chat ID thật của bạn vào trong dấu ngoặc kép bên dưới
TELEGRAM_TOKEN = "8842424547:AAHsy6okplZYlXAx8P5PBZL-ug9MjS6J-hA"
TELEGRAM_CHAT_ID = "8805710262"

def canh_bao_telegram(status_text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={status_text}"
    try:
        # Gửi request lên Telegram, timeout 5s để không làm treo hệ thống nếu nghẽn mạng
        requests.get(url, timeout=5)
    except:
        pass 

# ==========================================
# 2. TẢI "BỘ NÃO" AI ĐÃ HUẤN LUYỆN
# ==========================================
try:
    model = joblib.load('fire_detection_model.pkl')
    scaler = joblib.load('scaler.pkl')
    print("✅ Đã tải mô hình AI thành công!")
except:
    print("❌ Lỗi: Không tìm thấy file mô hình! Hãy kiểm tra lại thư mục.")
    sys.exit()

labels_dict = {
    0: "✅ BÌNH THƯỜNG",
    1: "⚠️ CẢNH BÁO: RÒ RỈ GAS!",
    2: "🔥 NGUY HIỂM: PHÁT HIỆN HỎA HOẠN!"
}

# ==========================================
# 3. HÀM XỬ LÝ KHI NHẬN ĐƯỢC DATA TỪ ESP32
# ==========================================
def on_message(client, userdata, msg):
    raw_data = msg.payload.decode('utf-8')
    data = raw_data.split(',')
    
    if len(data) == 4:
        try:
            t, h, gas, flame = float(data[0]), float(data[1]), float(data[2]), float(data[3])
            
            # Đưa vào AI suy luận
            features = np.array([[t, h, gas, flame]])
            features_scaled = scaler.transform(features)
            prediction = model.predict(features_scaled)[0]
            status = labels_dict.get(prediction, "KHÔNG XÁC ĐỊNH")
            
            print(f"🌡 {t}°C | 💧 {h}% | 💨 Gas: {gas:04.0f} | 🔆 Lửa: {flame:04.0f} ===> {status}")
            
            # --- GỬI DATA LÊN APP MQTT DASHBOARD ---
            # Lưu ý: Gửi nguyên số thô để đồng hồ Gauge quay mượt
            client.publish("hizu/project/temp", f"{t}")
            client.publish("hizu/project/hum", f"{h}")
            client.publish("hizu/project/status", status)
            
            # --- HÚ CÒI TELEGRAM NẾU CÓ CHÁY/GAS ---
            if prediction == 1 or prediction == 2:
                loi_nhan = f"🚨 {status}\n🌡 Nhiệt độ: {t}°C | 💧 Độ ẩm: {h}%"
                canh_bao_telegram(loi_nhan)
                
        except ValueError:
            pass # Bỏ qua nhiễu rác nếu có để hệ thống không sập

# ==========================================
# 4. KẾT NỐI SERVER TRUNG CHUYỂN EMQX
# ==========================================
BROKER = "broker.emqx.io"
PORT = 1883

mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message

print("Đang kết nối với Server EMQX...")
try:
    mqtt_client.connect(BROKER, PORT, 60)
    print("✅ Đã lên mạng! Đang chờ dữ liệu từ mạch ESP32...\n")
    
    # Đăng ký lắng nghe kênh dữ liệu thô từ ESP32
    mqtt_client.subscribe("hizu/sensor/raw_data")
    
    # Giữ cho Python chạy mãi mãi để nghe dữ liệu
    mqtt_client.loop_forever()
    
except Exception as e:
    print("❌ Không thể kết nối MQTT. Kiểm tra lại mạng Internet.")
    sys.exit()