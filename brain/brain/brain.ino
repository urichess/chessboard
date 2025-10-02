#include <Arduino.h>

#define UART_TX_PIN 43  // U0TXD
#define UART_RX_PIN 44  // U0RXD
#define BAUD_RATE   115200

void setup() {
  // USB CDC Serial
  Serial.begin(BAUD_RATE);
  while (!Serial);  // wait for USB CDC to be ready (native USB boards)

  Serial.println("ESP32 USB ↔ UART0 bridge starting...");

  // Hardware UART0
  Serial1.begin(BAUD_RATE, SERIAL_8N1, UART_RX_PIN, UART_TX_PIN);
}

void loop() {
  // Forward USB -> UART
  while (Serial.available()) {
    char c = Serial.read();
    Serial1.write(c);
  }

  // Forward UART -> USB
  while (Serial1.available()) {
    char c = Serial1.read();
    Serial.write(c);
  }

  //Serial.println("nothing");
}
