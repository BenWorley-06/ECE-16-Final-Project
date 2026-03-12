const int BUTTON_PIN=27;
int prevVal=1;
const int FIRE_BUTTON_PIN=32; 
int prevFireVal = HIGH;
unsigned long fire_time_since_push = 0;
unsigned long time_since_push=0;
void setupButton(){
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(FIRE_BUTTON_PIN, INPUT_PULLUP);
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

int detectFireButton() {
    int fireVal = digitalRead(FIRE_BUTTON_PIN);
    int pressed = 0;

    if(fireVal == LOW && prevFireVal == HIGH) {
        fire_time_since_push = millis();
        digitalWrite(LED_BUILTIN, HIGH);
    }

    if(fireVal == HIGH && prevFireVal == LOW) {
        if(millis() - fire_time_since_push > 50) {
            digitalWrite(LED_BUILTIN, LOW);
            pressed = 1;
        }
    }

    prevFireVal = fireVal;
    return pressed;
}