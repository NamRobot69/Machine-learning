#include "DHT.h"

// ==========================================
// ĐỊNH NGHĨA CHÂN KẾT NỐI (PINOUT)
// ==========================================
#define DHTPIN 32        // Chân DATA của DHT11 nối với D4
#define DHTTYPE DHT11   // Khai báo loại cảm biến là DHT11

#define MQ_PIN 34       // Chân A0 của MQ nối với D34 (Analog)
#define FLAME_PIN 35    // Chân A0 của Cảm biến lửa nối với D35 (Analog)

// Khởi tạo đối tượng cảm biến DHT
DHT dht(DHTPIN, DHTTYPE);

// Biến lưu trạng thái nhãn hiện tại, mặc định khi bật máy là 0 (Bình thường)
int currentLabel = 0;

void setup() {
  Serial.begin(115200);
  dht.begin();
  
  // In dòng tiêu đề (Header) của file CSV
  Serial.println("Temperature,Humidity,Gas_Analog,Flame_Analog,Label");
}

void loop() {
  // ==========================================
  // BƯỚC 1: Gõ LỆNH TỪ BÀN PHÍM ĐỂ ĐỔI NHÃN
  // ==========================================
  // Kiểm tra xem bạn có gõ gì vào Serial Monitor không
  if (Serial.available() > 0) {
    char incomingChar = Serial.read();
    
    // Nếu gõ '0', '1', hoặc '2' thì cập nhật nhãn tương ứng
    if (incomingChar == '0') {
      currentLabel = 0;
    } 
    else if (incomingChar == '1') {
      currentLabel = 1;
    } 
    else if (incomingChar == '2') {
      currentLabel = 2;
    }
    // Code tự động bỏ qua phím Enter hoặc các ký tự rác khác để không làm hỏng data
  }

  // ==========================================
  // BƯỚC 2: ĐỌC DỮ LIỆU TỪ CÁC CẢM BIẾN
  // ==========================================
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  int gasValue = analogRead(MQ_PIN);
  int flameValue = analogRead(FLAME_PIN); 

  if (isnan(h) || isnan(t)) {
    Serial.println("Lỗi: Không đọc được dữ liệu từ DHT11!");
    delay(1000);
    return;
  }

  // ==========================================
  // BƯỚC 3: IN RA SERIAL MONITOR CHUẨN ĐỊNH DẠNG CSV
  // ==========================================
  Serial.print(t);
  Serial.print(",");
  Serial.print(h);
  Serial.print(",");
  Serial.print(gasValue);
  Serial.print(",");
  Serial.print(flameValue);
  Serial.print(",");
  Serial.println(currentLabel); // In nhãn động đã được cập nhật

  delay(500); 
}
