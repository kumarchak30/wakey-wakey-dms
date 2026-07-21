const int BUZZER_PIN = 8;
const int LED_PIN    = 13;
bool alertActive     = false;  // this was missing

void setup() {
  Serial.begin(9600);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == '1') {
      digitalWrite(LED_PIN, HIGH);
      alertActive = true;
    }
    else if (cmd == '0') {
      digitalWrite(LED_PIN, LOW);
      alertActive = false;
      noTone(BUZZER_PIN);
    }
  }

  // Pulse the buzzer while alert is active
  if (alertActive) {
    tone(BUZZER_PIN, 2500);
    delay(300);
    noTone(BUZZER_PIN);
    delay(200);
  }
}