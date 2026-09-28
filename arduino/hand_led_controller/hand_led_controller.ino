const int ledPins[] = {2, 3, 4, 5, 6};

String command = "";

void setup() {
  Serial.begin(9600);

  for (int i = 0; i < 5; i++) {
    pinMode(ledPins[i], OUTPUT);
    digitalWrite(ledPins[i], LOW);
  }
}

void loop() {

  if (Serial.available() > 0) {

    command = Serial.readStringUntil('\n');
    command.trim();

    if (command.length() >= 5) {

      for (int i = 0; i < 5; i++) {

        if (command[i] == '1') {
          digitalWrite(ledPins[i], HIGH);
        }

        else if (command[i] == '0') {
          digitalWrite(ledPins[i], LOW);
        }
      }
    }
  }
}