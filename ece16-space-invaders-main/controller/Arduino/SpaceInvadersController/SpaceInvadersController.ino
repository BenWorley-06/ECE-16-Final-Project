/*
 * Global variables
 */
// Acceleration values recorded from the readAccelSensor() function
int ax = 0; int ay = 0; int az = 0;
int ppg = 0;        // PPG from readPhotoSensor() (in Photodetector tab)
int sampleTime = 0; // Time of last sample (in Sampling tab)
bool sending;
String currentLives = "3";
/*
 * Initialize the various components of the wearable
 */
void setup() {
  Serial.begin(115200);
  setupAccelSensor();
  setupCommunication();
  setupDisplay();
  setupPhotoSensor();
  setupButton();
  sending = false;

  writeDisplay("Ready...", 1, true);
  writeDisplay("Set...", 2, false);
  writeDisplay("Play!", 3, false);
}

/*
 * The main processing loop
 */
void loop() {
  // Parse command coming from Python (either "stop" or "start")
  bool bullet_detected = false;
  String command = receiveMessage();
  if(command == "stop") {
    sending = false;
    writeDisplay("Controller: Off", 0, true);
  }
  else if(command == "start") {
    sending = true;
    writeDisplay("Controller: On", 0, true);
  }
  else if (command == "bullet"){
    bullet_detected=true;
  }
  else if(command.startsWith("lives:")) {
    currentLives = command.substring(6);
    String msg = "Lives: " + currentLives;
    writeDisplay(msg.c_str(), 2, false);
  }

  else if(command.startsWith("score:")) {
    String scoreVal = command.substring(6);
    String scoreMsg = "Score: " + scoreVal;
    writeDisplay(scoreMsg.c_str(), 1, true);
    String livesMsg = "Lives: " + currentLives;
    writeDisplay(livesMsg.c_str(), 2, false);
  }

  // Send the orientation of the board
  if(sending && sampleSensors()) {
    sendMessage(String(ax) + "," + String(detectButton()) + "," + String(detectFireButton()));
  }

  processLED(bullet_detected);
}
