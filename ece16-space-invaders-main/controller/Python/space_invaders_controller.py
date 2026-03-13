"""
@author: Ramsin Khoshabeh
"""

from ECE16Lib.Communication import Communication
from time import sleep,time
import socket, pygame
#Threshold values for ship speed 
TILT_DEAD_ZONE = 100
TILT_MAX = 350
SPEED_MIN = 2         
SPEED_MAX = 15  


# Setup the Socket connection to the Space Invaders game
host = "127.0.0.1"
port = 65432
mySocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mySocket.connect((host, port))
mySocket.setblocking(False)

# Socket connection from game to controller
game_host = "127.0.0.1"
game_port = 65433

gameSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
gameSocket.bind((game_host, game_port))
gameSocket.setblocking(False)

BABY_BUTTON_INTERVAL = 0.5

class PygameController:
  comms = None

  def __init__(self, serial_name, baud_rate):
    self.comms = Communication(serial_name, baud_rate)
  #Instead of getting binary orientation, read ax to get speed.
  def get_speed_from_tilt(self, ax):
    if abs(ax) < TILT_DEAD_ZONE:
        return 0, None

    clamped = max(-TILT_MAX, min(TILT_MAX, ax))
    magnitude = abs(clamped)
    speed = int(SPEED_MIN + (magnitude - TILT_DEAD_ZONE) /
                (TILT_MAX - TILT_DEAD_ZONE) * (SPEED_MAX - SPEED_MIN))
    speed = max(SPEED_MIN, min(SPEED_MAX, speed))

    direction = "LEFT" if clamped < 0 else "RIGHT"
    return speed, direction
  
  def run(self):
    # 1. make sure data sending is stopped by ending streaming
    self.comms.send_message("stop")
    self.comms.clear()
    PAUSE_COOLDOWN = 0.5
    prev_time_button = 0
    prev_time_fire_button = 0
    prev_pause_state = 0
    pause_sent = False 
    # 2. start streaming orientation data
    input("Ready to start? Hit enter to begin.\n")
    self.comms.send_message("start")
    #Calibrate for ax values
    print("Calibrating, hold the board flat...")
    ax_offset = 0
    samples = []
    while len(samples) < 20:
        message = self.comms.receive_message()
        if message != None:
            try:
                (m1, m2, m3) = message.split(',')
                samples.append(int(m1))
            except ValueError:
                continue
    ax_offset = sum(samples) // len(samples)
    print(f"Calibration done. Offset: {ax_offset}")
    # 3. Forever collect orientation and send to PyGame until user exits
    print("Use <CTRL+C> to exit the program.\n")
    while True:
      try:
        msg, _ = gameSocket.recvfrom(1024)
        msg = msg.decode("utf-8")
        if msg == "BULLET":
            self.comms.send_message("BULLET")
        elif msg.startswith("score:"):
          self.comms.send_message(msg)
        elif msg.startswith("lives:"):
          self.comms.send_message(msg)
      except BlockingIOError:
          pass

      message = self.comms.receive_message()
      current_time=time()
      if(message != None):
        command = None
        try:
          (m1, m2, m3) = message.split(',')
        except ValueError:        # if corrupted data, skip the sample
          continue
        ax = int(m1) - ax_offset
        pauseButton = int(m2)
        fireButton = int(m3)
        # if message == 0:
        #   command = "FLAT"
        # if message == 1:
        #   command = "UP"
        #Send computed speed and direction to main
        speed, direction = self.get_speed_from_tilt(ax)
        print(f"ax: {ax}, speed: {speed}, direction: {direction}")
        if direction is not None:
          mySocket.send(f"{direction}:{speed}".encode("UTF-8"))
        if fireButton == 1:
          mySocket.send("FIRE".encode("UTF-8"))
          prev_time_fire_button=current_time
        if pauseButton == 1 and prev_pause_state == 0 and (current_time - prev_time_button) > PAUSE_COOLDOWN:
          mySocket.send("PAUSE".encode("UTF-8"))
          pause_sent = True 
          prev_time_button=current_time
        if pauseButton == 0:
          pause_sent = False
        prev_pause_state = pauseButton
        if (current_time-prev_time_button) < BABY_BUTTON_INTERVAL and (current_time-prev_time_fire_button) < BABY_BUTTON_INTERVAL:
          mySocket.send("BABY".encode("UTF-8"))
          prev_time_button=0
          prev_time_fire_button=0


if __name__== "__main__":
  serial_name = "/dev/cu.MyOLED"
  baud_rate = 115200
  controller = PygameController(serial_name, baud_rate)

  try:
    controller.run()
  except(Exception, KeyboardInterrupt) as e:
    print(e)
  finally:
    print("Exiting the program.")
    controller.comms.send_message("stop")
    controller.comms.close()
    mySocket.send("QUIT".encode("UTF-8"))
    mySocket.close()

  input("[Press ENTER to finish.]")
