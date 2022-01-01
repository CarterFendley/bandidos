import numpy as np
from scipy.stats import norm

from bandidos import BanditArm

class NormalArm(BanditArm):
  '''
  This class defines a class of type `BanditArm` which samples from a normal distribution.
  
  The most basic initialization would take the form `n_arm = NormalArm(steps)` where `steps` is a parameter required by the `BanditArm` abstract class and defines the number of expected times `sample()` will be called.

  To specify the mean & standard deviation one can input them as the second two positional arguments `n_arm = NormalArm(steps, mean, sd)`. If no mean & sd are provided, the default will be `mean = 0` & `sd = 1`.

  **Reminder:** If used with a `BanditProblem(steps)` instance (by use of the `add_arm(NormalArm)` method), the `steps` argument will be injected by the bandit problem. Thus, the following would be how to create a bandit problem with one `NormalArm` with `mean` of 15 and `sd` of 0.2.
  
  ```python
  p = BanditProblem(50)
  p.add_arm(NormalArm, 15, 0.2)
  ```
  '''
  def setup(self, steps, *args):
    self._mean = None
    self._sd = None

    # Parse out the optional parameters 
    for i, arg in enumerate(args):
      print(f'{i=}, {arg=}')
      if i == 0:
        try:
          self._mean = float(arg)
        except ValueError:
          raise ValueError('Unable to parse input mean into float')
      elif i == 1:
        try:
          self._sd = float(arg)
        except ValueError:
          raise ValueError('Unable to parse input standard deviation into float')
      else:
        raise IndexError('Too many positional arguments passed to NormalArm setup')

    # If mean & sd was not set from arguments, set now
    if self._mean is None:
      self._mean = 0.0
    if self._sd is None:
      self._sd = 1.0
    
    # As this is a stationary arm, we can calculate the PDF at this time rather than on each step
    self._pdf_x = np.linspace(
      norm.ppf(0.01, loc=self._mean, scale=self._sd), # The x at the 1st precentile
      norm.ppf(0.99, loc=self._mean, scale=self._sd), # The x at the 99th precentile
      100 # Spread 100 points between these two x's 
    )
    self._pdf_y = norm.pdf(
      self._pdf_x, # For each of the 100 points evaluate the PDF
      loc=self._mean,
      scale=self._sd
    )

  # Create read-only properties for mean & sd
  @property
  def mean(self):
    return self._mean
  @property
  def sd(self):
    return self._sd
  
  def pdf(self, step):
    return self._pdf_x, self._pdf_y 

  def sample(self, step):
    # Note: If anyone knows how to test the output of this method, please make a PR. Maybe fixing the seed?
    rvs = norm.rvs(
      size=1,
      loc=self._mean,
      scale=self._sd
    )

    return rvs[0]
