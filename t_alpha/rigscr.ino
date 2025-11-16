#include <HX711.h>

#define LOADCELL_DOUT_PIN  4
#define LOADCELL_SCK_PIN   5

HX711 scale;

const int relayPin = 24;  
#define calibration_factor 215.03


void setup() {
  Serial.begin(9600);
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
   scale.set_scale(calibration_factor); 
  scale.tare(); 
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, HIGH);  
}

void loop() {
  // Check for incoming serial data
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');

    if (command == "ON") {
      digitalWrite(relayPin,LOW);  
      delay(2000);
      digitalWrite(relayPin, HIGH); 

    } else if (command == "OFF") {
      digitalWrite(relayPin, HIGH); 
    } 
  }

  Serial.print(scale.get_units(), 1); 
Serial.println();
  delay(100);

}
