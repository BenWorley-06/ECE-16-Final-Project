from ECE16Lib.communication import Communication
from ECE16Lib.circular_list import CircularList
from matplotlib import pyplot as plt
import numpy as np
import time as tm

#Constants
plot_update=1.0

active_threshold=4000
lazy_threshold=3650

active_message="I smell a,gold medalist!"
idle_message="Get off your,bottom ape!"

active_readings_required=2
idle_readings_required=50

plot_labels=["Acceleration","Detection"]

def generatePlot(labels):
    plt.ion()
    fig, axs = plt.subplots(3, 3, figsize=(10, 8))
    axs = axs.flatten()
    for i in range(len(labels)):
        axs[i].set_title(labels[i])
    return fig, axs

def updatePlot(axs, data,labels):
    for i in range(len(data)):
        axs[i].clear()
        axs[i].plot(data[i])
        axs[i].set_title(labels[i])
    plt.pause(0.001)

def computeMagnitude(axes):
  return np.sqrt(np.square(axes[0])+np.square(axes[1])+np.square(axes[2]))

class IdleDetector:
    def __init__ (self,comms,num_samples):
        self.comms=comms
        
        """self.fig,self.axs=generatePlot([plot_labels])"""

        self.is_active=None
        self.active_count=0
        self.idle_count=0

        self.detection_buffer = CircularList([], num_samples)
        self.amag= CircularList([], num_samples)

        self.data=[self.amag,self.detection_buffer]

        self.plot_timer=0
        self.new_samples=0

    def iterateCount(self):
        new_data = self.amag[-self.new_samples:] 
    
        for movement in new_data:
            if movement >= active_threshold:
                self.active_count += 1
                self.idle_count = max(self.idle_count - 1, 0)
            elif self.is_active and movement >= lazy_threshold:
                self.active_count += 1
                self.idle_count = max(self.idle_count - 1, 0)
            else:
                self.idle_count += 1
                self.active_count = max(self.active_count - 1, 0)
                
        self.new_samples = 0

    def check(self):
        self.iterateCount()

        if self.active_count>=active_readings_required:  
            self.active_count=0
            return active_message
        
        elif self.idle_count>=idle_readings_required:
            self.idle_count=0
            return idle_message
        
        return None
    
    def communicate(self):
        message=self.check()
        if message is not(None):
            #print(message)
            if message==active_message:
               if self.is_active != True:
                  self.comms.send_message("Status: "+message)
                  self.is_active=True
            elif message==idle_message:
               if self.is_active != False:
                  self.comms.send_message("Status: "+message)
                  self.is_active=False

    def add(self,ax,ay,az):
        mag = computeMagnitude([ax,ay,az])
        self.amag.add(mag)
        self.new_samples+=1

    def process(self):

        #self.detection_buffer.add(1 if self.is_active else 0)   #   Square wave representation of active state

        self.communicate()
