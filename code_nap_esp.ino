#include <WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"

// --- KHAI BÁO CHÂN CẮM SENSOR ---
#define DHTPIN 32          // Chân nối DATA của DHT11
#define DHTTYPE DHT11     // Loại cảm biến
#define MQ_PIN 34         // Chân Analog nối Gas 
#define FLAME_PIN 35      // Chân Analog nối Lửa 

// --- CẤU HÌNH MẠNG ---
const char* ssid = "12T";
const char* password = "12345678";
const char* mqtt_server = "broker.emqx.io";

WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHTPIN, DHTTYPE);

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Dang ket noi WiFi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nDa ket noi WiFi!");
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Dang ket noi MQTT Broker... ");
    // Tạo ID ngẫu nhiên để không bị trùng lặp kết nối
    String clientId = "ESP32_Client_Hizu_";
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str())) {
      Serial.println("Thanh cong!");
    } else {
      Serial.print("That bai, ma loi=");
      Serial.print(client.state());
      Serial.println(" Thu lai sau 5 giay");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  setup_wifi();
  client.setServer(mqtt_server, 1883);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Đọc dữ liệu từ cảm biến thực
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  int gasValue = analogRead(MQ_PIN);
  int flameValue = analogRead(FLAME_PIN); 

  // --- CHỐT CHẶN AN TOÀN ĐÃ KHÔI PHỤC ---
  // Nếu cảm biến lỗi hoặc lỏng dây, dừng việc gửi data lên mạng
  if (isnan(h) || isnan(t)) {
    Serial.println("Loi doc Kiem tra lai day cam.");
    delay(1000);
    return; // Lệnh này bắt ESP32 quay lại từ đầu (không chạy phần gửi MQTT bên dưới)
  }

  // Đóng gói 4 thông số thành 1 chuỗi CSV
  String payload = String(t) + "," + String(h) + "," + String(gasValue) + "," + String(flameValue);
  
  // Bắn dữ liệu thô lên mạng MQTT
  client.publish("hizu/sensor/raw_data", payload.c_str());
  
  Serial.print("Da gui MQTT: ");
  Serial.println(payload);

  delay(10000); // Đợi 10 giây rồi lặp lại
}