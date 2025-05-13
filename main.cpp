#include <WiFi.h> 
#include <PubSubClient.h>
#include <OneWire.h>
#include <DallasTemperature.h>

#define WIFI_SSID "<YOUR WIFI NAME>"
#define WIFI_PASSWORD "<YOUR WIFI PASS>"
#define MQTT_SERVER "<HOST MACHINE IP>"
#define MQTT_PORT 1883
#define DALLAS_ONEWIRE_PIN 17

WiFiClient espClient;
PubSubClient client(espClient);
OneWire onewire(DALLAS_PIN);
DallasTemperature dallasSensor(&onewire);

//Give new sensors a float value and string with a name
//Sensor1
float dallasTemp;
String sensor_name1 = "DS18B20_1";

void connectWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected.");
}

void reconnectMQTT() {
  while (!client.connected()) {
    Serial.print("Connectiong to MQTT...");
    if (client.connect("ESP32_DHT11")) {
      Serial.println("OK");
    } else {
      Serial.print("Error (rc=");
      Serial.print(client.state());
      Serial.println("). Retrying...");
      delay(3000);
    }
  }
}

void setup() {
  Serial.begin(9600);
  dallasSensor.begin();
  delay(1000);

  connectWiFi();
  client.setServer(MQTT_SERVER, MQTT_PORT);
}

void loop() {
  if (!client.connected()) {
    reconnectMQTT();
  }
  client.loop();
  dallasSensor.requestTemperatures();
  
  // Add sensors to this list, increment the index with each new sensor
  dallasTemp = dallasSensor.getTempCByIndex(0);

  if (!isnan(dallasTemp) && !isnan(dallasTemp)) {
    String payload = String(sensor_name1) + ": " + String(dallasTemp);
    client.publish("esp32/ds/temperature", payload.c_str());
    Serial.println("Sent: " + payload);
  } else {
    Serial.println("Error: Could not read temp");
  }

  delay(100);
}
