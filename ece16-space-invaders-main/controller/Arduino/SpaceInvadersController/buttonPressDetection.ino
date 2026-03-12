const int BUTTON_PIN=27;
int prevVal=1;

unsigned long time_since_push=0;
void setupButton(){
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED_BUILTIN, OUTPUT);
}
//  Push Button Logic
int detectButton() {
    int buttonVal = digitalRead(BUTTON_PIN);
    int pressed = 0;

    if (buttonVal == LOW && prevVal == HIGH) {
        time_since_push = millis();
        digitalWrite(LED_BUILTIN, HIGH);
    }
    if (buttonVal == HIGH && prevVal == LOW) {
        if (millis() - time_since_push > 50) {  
            digitalWrite(LED_BUILTIN, LOW);
            pressed = 1;
        }
    }
    prevVal = buttonVal;
    return pressed;
}