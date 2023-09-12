#include <SPI.h>
#include <MFRC522.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

#define SS_PIN D2   // SDA connected to D2
#define RST_PIN D1  // Reset pin connected to D1

MFRC522 mfrc522(SS_PIN, RST_PIN);
WiFiClient client;
const char* ssid = "Quantum";
const char* password = "johnnykey";
const char* serverAddress = "http://192.168.108.91:5000/register"; // Update with your PC's IP address

void setup() {
  Serial.begin(115200);
  SPI.begin();
  mfrc522.PCD_Init();
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
}

void loop() {
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
    delay(50);
    return;
  }
  
  String cardId = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    cardId += String(mfrc522.uid.uidByte[i], HEX);
  }
  cardId.toUpperCase();
  
  Serial.println("Detected Card ID: " + cardId);
  
  // Send data to Flask server using HTTP POST request
  sendPostRequest(cardId);
  
  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();
}

void sendPostRequest(String cardId) {
  HTTPClient http;
  
  http.begin(client,serverAddress);
  http.addHeader("Content-Type", "application/x-www-form-urlencoded");
  
  String postData = "card_id=" + cardId;
  int httpResponseCode = http.POST(postData);
  
  if (httpResponseCode > 0) {
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
  } else {
    Serial.println("HTTP Request failed");
  }
  
  http.end();
}

