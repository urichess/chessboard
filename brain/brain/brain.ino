#include <Arduino.h>
#include <NimBLEDevice.h>
#include <queue>

std::queue<uint8_t> txQueue;

#define UART_TX_PIN 43
#define UART_RX_PIN 44
#define BAUD_RATE   115200
#define BUFFER_SIZE 1024

// Nordic UART Service UUIDs
#define SERVICE_UUID        "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
#define CHARACTERISTIC_RX   "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
#define CHARACTERISTIC_TX   "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

NimBLEServer* pServer = nullptr;
NimBLECharacteristic* pTxCharacteristic = nullptr;
bool deviceConnected = false;
bool notificationReady = true;

// ---- Callbacks ----
class ServerCallbacks : public NimBLEServerCallbacks {
  void onConnect(NimBLEServer* pServer, NimBLEConnInfo& connInfo) {
    deviceConnected = true;
    Serial.println("BLE Device connected");
  }
  void onDisconnect(NimBLEServer* pServer, NimBLEConnInfo& connInfo, int reason) {
    deviceConnected = false;
    NimBLEDevice::startAdvertising();
    Serial.println("BLE Device disconnected");
  }
};

class RXCallbacks : public NimBLECharacteristicCallbacks {
  void onWrite(NimBLECharacteristic* pCharacteristic, NimBLEConnInfo& connInfo) {
    std::string value = pCharacteristic->getValue();
    for (char c : value) {
      Serial.write(c);
      Serial1.write(c);
    }
  }
};

class TXCallbacks : public NimBLECharacteristicCallbacks {
    void onStatus(NimBLECharacteristic* pCharacteristic, int code) override {
        if (code == 0 || code == BLE_HS_EDONE) {
            notificationReady = true;
        } else {
            Serial.print("Failed with code: ");
            Serial.println(code);
        }
    }
};

// ---- Setup ----
void setup() {
  Serial.begin(BAUD_RATE);
  while (!Serial);
  Serial.println("\n[ESP32-S3] BLE ↔ UART ↔ USB Bridge starting...");

  Serial1.begin(BAUD_RATE, SERIAL_8N1, UART_RX_PIN, UART_TX_PIN);

  // Initialize BLE
  NimBLEDevice::init("ESP32S3_BLE_Bridge");

  Serial.println(NimBLEDevice::getAddress().toString().c_str());

  pServer = NimBLEDevice::createServer();
  pServer->setCallbacks(new ServerCallbacks());

  NimBLEService* pService = pServer->createService(SERVICE_UUID);

  pTxCharacteristic = pService->createCharacteristic(
      CHARACTERISTIC_TX,
      NIMBLE_PROPERTY::INDICATE
  );

  NimBLECharacteristic* pRxCharacteristic = pService->createCharacteristic(
      CHARACTERISTIC_RX,
      NIMBLE_PROPERTY::WRITE | NIMBLE_PROPERTY::WRITE_NR
  );
  pRxCharacteristic->setCallbacks(new RXCallbacks());
  pTxCharacteristic->setCallbacks(new TXCallbacks());

  pService->start();

  NimBLEAdvertising* pAdvertising = NimBLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponseData(NimBLEDevice::getAdvertising()->getAdvertisementData());
  pAdvertising->setMinInterval(0x20);
  pAdvertising->setMaxInterval(0x40);
  NimBLEDevice::startAdvertising();

  NimBLEDevice::setSecurityAuth(false, false, true); // bonding, MITM, secure connections
  
  Serial.println("[BLE] Advertising as 'ESP32S3_BLE_Bridge'");
  Serial.println("Bridge active: USB ↔ UART ↔ BLE\n");
}

// ---- Main Loop ----
void loop() {
  // USB → UART + BLE
  while (Serial.available()) {
    uint8_t c = Serial.read();
    Serial1.write(c);
    if (deviceConnected)
      txQueue.push(c);
  }

  // UART → USB + BLE
  while (Serial1.available()) {
    uint8_t c = Serial1.read();
    Serial.write(c);
    if (deviceConnected)
      txQueue.push(c);
  }

      // Send one byte at a time via BLE if ready
    if (deviceConnected && !txQueue.empty() && notificationReady) {
      static uint8_t buffer[BUFFER_SIZE];
      int len = 0;

      const uint16_t characteristic_max_size = pTxCharacteristic->getValue().max_size();
      const int MAXIMUM_SIZE = characteristic_max_size < BUFFER_SIZE? (int)characteristic_max_size:(int)BUFFER_SIZE;

      while (!txQueue.empty() && len < MAXIMUM_SIZE) {
          buffer[len++] = txQueue.front();
          txQueue.pop();
      }


      pTxCharacteristic->setValue(buffer, len);     
      notificationReady = false;  // wait for onStatus
      pTxCharacteristic->indicate();
    }


}
