from inspect import signature

class BanditArm:
  def __init__(self, steps: int, *args):
    assert self.__class__ != BanditArm, "BanditArm abstract class should not be initalized directly"
    assert isinstance(steps, int), "Argument for steps must be an integer"
    assert steps > 0, "Argument for steps must be positive integer"

    # Keep local copy of the steps for future use
    self._steps = steps

    # Check the existence sample method
    if not hasattr(self, "sample") or not callable(self.sample):
      raise AttributeError("Impmentations of abstract class BanditArm must have callable method / attribute with signature 'sample(self, step)'")
    
    # Check signature of sample method
    sample_sig = signature(self.sample)
    if not len(sample_sig.parameters) == 1 or 'step' not in sample_sig.parameters:
      raise AssertionError("Impmentations of abstract class BanditArm must have callable method / attribute with signature 'sample(self, step)'")

    # Call setup if it exists
    if hasattr(self, "setup") and callable(self.setup):
      setup_sig = signature(self.setup)
      if not len(setup_sig.parameters) == 2 or 'steps' not in setup_sig.parameters:
        raise AssertionError("Optional setup method for instance of BanditProblem must have signature 'setup(self, steps, *args)'")
      self.setup(self._steps, *args)
  
  # Expose read only vars
  @property
  def steps(self):
    return self._steps
  
  # Expose a self.has_pdf for ease of 
  @property
  def has_pdf(self):
    '''
    Evaluates to `True` if there is a callable attribute named "pdf" which has signature self.pdf(step). This attribute could be a method, lambda function, etc...
    ''' 

    # Check existence and callability
    if not hasattr(self, "pdf") or not callable(self.pdf):
      return False

    # Check signature of callable
    sig = signature(self.pdf)
    if not len(sig.parameters) == 1 or 'step' not in sig.parameters:
      return False

    # All checks passed
    return True
  
  @property
  def has_step(self):
    '''
    Evaluates to `True` if there is a callable attribute named 'step' which has signature `self.step(step)`. This attribute could be a method, lambda function, etc...

    Step routines are called by the `BanditProblem()` instance each time a new time step is started. These methods can be used to modify variables internal to the `BanditArm()` instance, for example to adjust the mean of a non-stationary arm. 
    '''

    # Check existence and callability
    if not hasattr(self, "step") or not callable(self.step):
      return False

    # Check signature of callable
    sig = signature(self.step)
    if not len(sig.parameters) == 1 or 'step' not in sig.parameters:
      return False

    # All checks passed
    return True
  
  def _get_pdf(self):
    '''
    Wrapper around calls to self.pdf() to assure that they return correct data types
    '''
    assert self.has_pdf, "Can not get the pdf of arm without callable attribute 'self.pdf()'"