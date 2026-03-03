from ECE16Lib.circular_lists import CircularList
import ECE16Lib.DSP as filt
import numpy as np

"""
A class to enable a simple heart rate monitor
"""
class HRMonitor:
  """
  Encapsulated class attributes (with default values)
  """
  __hr = 0           # the current heart rate
  __time = None      # CircularList containing the time vector
  __ppg = None       # CircularList containing the raw signal
  __filtered = None  # CircularList containing filtered signal
  __num_samples = 0  # The length of data maintained
  __new_samples = 0  # How many new samples exist to process
  __fs = 0           # Sampling rate in Hz
  __thresh = 0.6     # Threshold from Tutorial 2

  """
  Initialize the class instance
  """
  def __init__(self, num_samples, fs, times=[], data=[],webcam=False):
    self.__hr = 0
    self.__num_samples = num_samples
    self.__fs = fs
    self.__time = CircularList(times, num_samples)
    self.__ppg = CircularList(data, num_samples)
    self.__filtered = CircularList([], num_samples)
    self.__b, self.__a = filt.create_filter(4, [0.7, 3.5], "bandpass", self.__fs)
    self.__webcam=webcam

  """
  Add new samples to the data buffer
  Handles both integers and vectors!
  """
  def add(self, t, x):
    if isinstance(t, np.ndarray):
      t = t.tolist()
    if isinstance(x, np.ndarray):
      x = x.tolist()


    if isinstance(x, int):
      self.__new_samples += 1
    else:
      self.__new_samples += len(x)

    self.__time.add(t)
    self.__ppg.add(x)

  """
  Compute the average heart rate over the peaks
  """
  def compute_heart_rate(self, peaks):
    if len(peaks) < 2:
      return 0
    t = np.array(self.__time)
    time_diff = np.diff(t[peaks])
    if len(time_diff) == 0 or np.mean(time_diff) == 0:
      print('bad time diff')
      return 0
    return 60 / np.mean(time_diff)

  """
  Process the new data to update step count
  """
  def process(self):
    # Grab only the new samples into a NumPy array
    x = np.array(self.__ppg[ -min(self.__new_samples+400,self.__num_samples-200): ])

    # Filter the signal (feel free to customize!)
    x = filt.detrend(x, 25)
    x = filt.moving_average(x, 5)
    x = filt.gradient(x)
    if self.__webcam:
      x = np.tanh(x * 1.5)
    x= filt.filter(self.__b, self.__a, x) # Band pass to filter signals out that dont make sense for heart beat (Should be between 40 to 200 BPM)
    x = filt.normalize(x)
    

    # Store the filtered data
    self.__filtered.add(x.tolist())

    # Find the peaks in the filtered data
    threshold = np.mean(x) + np.std(x) # Adaptive threshold
    _, peaks = filt.count_peaks(self.__filtered, threshold, 1)

    # Update the step count and reset the new sample count
    self.__hr = self.compute_heart_rate(peaks)
    self.__new_samples = 0

    # Return the heart rate, peak locations, and filtered data
    return self.__hr, peaks, np.array(self.__filtered)

  """
  Clear the data buffers and step count
  """
  def reset(self):
    self.__hr = 0
    self.__time.clear()
    self.__ppg.clear()
    self.__filtered.clear()