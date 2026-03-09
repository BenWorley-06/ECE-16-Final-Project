const int LED_PIN=17;

const int frequency = 2; // hz
int period;

int duration = 1000; // ms

unsigned long time_of_transition_LED=0;
unsigned long start_time = 0;

bool lit = false;

bool run = true;


void setupLED(){
  pinMode(LED_PIN, OUTPUT);
  period = 1000/frequency;
}

void deactivateLED(){
  lit=false;
  digitalWrite(LED_PIN, LOW);
}

void blinkLED(){
  int current_time=millis();
  if (current_time-time_of_transition_LED>=period){
    time_of_transition_LED=millis();
    if (lit){
      lit=false;
      digitalWrite(LED_PIN, LOW);
    }else{
      lit=true;
      digitalWrite(LED_PIN, HIGH);
    }
  }
}

void processLED(bool requested){
  int current_time = millis();
  if (requested){
      start_time=current_time;
      run=true;
  }
  if (run){
    blinkLED();
    if (current_time-start_time>=duration){
      run = false;
      deactivateLED();
    }
  }
}