
int PINS[] = {A0, A1, A2, A3, A4, A5};
int PIN_COUNT = int(sizeof(PINS)/sizeof(PINS[0])); 

void setup() {
  // put your setup code here, to run once:
  Serial.begin(230400);
}

void loop() {
  // put your main code here, to run repeatedly:
  for (int i = 0; i < PIN_COUNT; i++) {
    Serial.print(PINS[i]);
    Serial.print(", ");
  }
  Serial.println();
  delay(1000);
}
