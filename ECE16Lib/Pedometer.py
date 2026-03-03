from ECE16Lib.circular_lists import CircularList
import ECE16Lib.DSP as filt
import numpy as np
import time as tm

threshold__high_min=100
threshold__low_min=20

"""
A class to enable a simple step counter
"""
class Pedometer:
  """
  Encapsulated class attributes (with default values)
  """
  __steps = 0        # the current step count
  __l1 = None        # CircularList containing L1-norm
  __filtered = None  # CircularList containing filtered signal
  __num_samples = 0  # The length of data maintained
  __new_samples = 0  # How many new samples exist to process
  __fs = 0           # Sampling rate in Hz
  __b = None         # Low-pass coefficients
  __a = None         # Low-pass coefficients
  __thresh_low = 40   # Threshold from Tutorial 2
  __thresh_high = 100 # Threshold from Tutorial 2
  __lastStepTime=0
  __minStepInterval=0.025 # 25 ms
  __maxStepInterval=2 # 2 seconds

  __jumpDetectionOn = False
  __jumps=0
  __jumpThreshold_high=900
  __jumpThreshold_low=300

  """
  Initialize the class instance
  """
  def __init__(self, num_samples, fs, data=None, jumpDetectionOn=False):
    self.__steps = 0
    self.__num_samples = num_samples
    self.__fs = fs
    self.__l1 = CircularList(data, num_samples)
    self.__filtered = CircularList([], num_samples)
    self.__b, self.__a = filt.create_filter(4, 5, "lowpass", fs)
    self.__jumpDetectionOn = jumpDetectionOn

  """
  Add new samples to the data buffer
  Handles both integers and vectors!
  """
  def add(self, ax, ay, az):
    l1 = filt.l1_norm(ax, ay, az)
    if isinstance(ax, int):
      num_add = 1
    else:
      num_add = len(ax)
      l1 = l1.tolist()

    self.__l1.add(l1)
    self.__new_samples += num_add

  """
  Process the new data to update step count
  """
  def process(self):
    # Grab only the new samples into a NumPy array
    x = np.array(self.__l1[ -self.__new_samples: ])

    # Filter the signal (detrend, LP, MA, etc…)                     
    ma = filt.moving_average(x, 50)                   
    dt = filt.detrend(ma)   
    x= filt.filter(self.__b, self.__a, dt)

    mean = np.mean(x)
    std = np.std(x)

    high_adaptive = mean + 2*std
    low_adaptive  = mean + 0.5*std
    self.__thresh_low=max(low_adaptive,threshold__low_min)
    self.__thresh_high=max(high_adaptive,threshold__high_min)


    # Store the filtered data
    self.__filtered.add(x.tolist())

    # Count the number of peaks in the filtered data
    count, peaks = filt.count_peaks(x,self.__thresh_low,self.__thresh_high)
    if self.__jumpDetectionOn:
      jumpCount,jumpPeaks = filt.count_peaks(x,self.__jumpThreshold_low,self.__jumpThreshold_high)

      if jumpCount>0:
        count=max(0,count-jumpCount)
        self.__jumps+=jumpCount

    # Update the step count and reset the new sample count
    current_time = tm.time()
    if self.__minStepInterval < current_time-self.__lastStepTime:
        self.__lastStepTime=current_time
        self.__steps += count
    
    self.__new_samples = 0

    # Return the step count, peak locations, and filtered data
    return self.__steps, peaks, np.array(self.__filtered), self.__jumps

  """
  Clear the data buffers and step count
  """
  def reset(self):
    self.__steps = 0
    self.__l1.clear()
    self.__filtered = CircularList([], self.__num_samples)