"""
@author: Ramsin Khoshabeh
"""

from ECE16Lib.Communication import Communication
from time import sleep,time
import socket, pygame

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

  def run(self):
    # 1. make sure data sending is stopped by ending streaming
    self.comms.send_message("stop")
    self.comms.clear()
    PAUSE_COOLDOWN = 0.5
    prev_time_button = 0
    prev_pause_state = 0
    pause_sent = False 
    # 2. start streaming orientation data
    input("Ready to start? Hit enter to begin.\n")
    self.comms.send_message("start")

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
        orientation = int(m1)
        pauseButton = int(m2)
        fireButton = int(m3)
        # if message == 0:
        #   command = "FLAT"
        # if message == 1:
        #   command = "UP"
        if orientation == 3:
          command = "LEFT"
        elif orientation == 4:
          command = "RIGHT"
        if command is not None:
          mySocket.send(command.encode("UTF-8"))
        if fireButton == 1:
          mySocket.send("FIRE".encode("UTF-8"))
        if pauseButton == 1 and prev_pause_state == 0 and (current_time - prev_time_button) > PAUSE_COOLDOWN:
          mySocket.send("PAUSE".encode("UTF-8"))
          pause_sent = True 
        if pauseButton == 0:
          pause_sent = False
        prev_pause_state = pauseButton

if __name__== "__main__":
  serial_name = "/dev/cu.usbserial-110"
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
