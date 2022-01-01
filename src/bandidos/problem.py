from uuid import uuid4
from inspect import isclass
import plotly.graph_objects as go

from bandidos import BanditArm

class BanditProblem:
  def __init__(self, steps: int):
    assert isinstance(steps, int), f"BanditProblem steps argument must be an integer not {type(steps)}"
    assert steps > 0, "BanditProblem steps must be positive integer"

    self._uuid = uuid4()
    self._arms = []
    self._steps = steps

    # Setup data structures needed to store data associated with the current step
    self._current_step = None
    self._current_rewards = {}
    self._current_pdfs = {}

    # Data structures needed to store the data over the entire lifetime of this problem (keep track of information on each step)
    self._historical_rewards = []
    self._historical_pdfs = []

  @property
  def arms(self):
    '''
    The number of arms associated with this problem as an integer. Easily confused with `self._arms` which is the internal storage of `BanditArm()` instances.
    '''
    return len(self._arms)

  @property
  def uuid(self):
    '''
    A uuid generated at initialization the problem used primarily for record keeping and disk storage.
    '''
    return self._uuid

  def add_arm(self, cls, *args):
    assert self._current_step is None, "BanditProblem can accept additional arms after the problem has *started* by either 'step()' or 'sample(arm)` functionality."

    assert isclass(cls), f"First argument of add_arm must be class not {type(cls)}"
    assert issubclass(cls, BanditArm), f"First argument of add_arm must be a descendent of BanditArm not {type(cls)}"

    # Construct the arm with steps and any other args passed in
    arm = cls(self._steps, *args)
    self._arms.append(arm)

    return arm
  
  def sample(self, arm):
    '''
    This method will return the sample of a specified arm in a given time step. If multiple calls are made to this method which specify the same arm, such as multiple `sample(0)` calls. It will cache the first sample *during this time step* and subsequent calls will all return the same value. This allows us to use the same `p = Problem()` instance while evaluating multiple algorithms (which might sample the same arm during a given time step). 

    Further it potentially, also allows for easier comparison between different algorithms. The idea is that, when evaluating, if the algorithms are compared in the exact same setting results are more comparable  
    '''
    assert isinstance(arm, int), "Arm must be integer indicating the index of the arm to be sampled"
    assert arm >= 0, "Arm must be non-negative integer indicating the index of the arm to be sampled"
    assert arm < self.arms, "Arm must be non-negative integer indicating the index of the arm to be sampled"

    # If this is our first step, initialize the count
    if self._current_step is None:
      self._current_step = 0

    # See if we have already sampled this arm for this step
    if arm in self._current_rewards:
      return self._current_rewards[arm]

    return self._do_sample(arm)
  
  def step(self):
    '''
    This method is used to start a new step of the problem. It can be called after a sequence of `sample(arm)` calls or can be called without ever using the sample method.

    If called before any `sample(arm)` it will advance the step count. It will also get a single sample from each arm for historical records.

    If called after a sequence of `sample(arm)` calls, it will advance the step count and will collect a single sample from arms which were not sampled by the `sample(arm)` calls for historical records. 
    '''

    # Initialize the count if it has not been
    if self._current_step is None:
      self._current_step = 0
    
    # Collect sample un-sampled arms
    for arm_index in range(self.arms):
      if arm_index not in self._current_rewards:
        self._do_sample(arm_index)
    
    # Convert the rewards to a tuple
    rewards = tuple([self._current_rewards[i] for i in range(self.arms)])

    # Store the rewards and pdfs
    self._historical_rewards.append(rewards)
    self._historical_pdfs.append(self._current_pdfs)

    # Reset data structures for current step
    self._current_pdfs = {}
    self._current_rewards = {}

    # Bump the step count
    self._current_step += 1

  def _do_sample(self, arm):
    a = self._arms[arm]

    s = a.sample(self._current_step)

    # Make sure we have a float
    try:
      s = float(s)
    except ValueError:
      raise ValueError(f'When sampled from BanditProblem instance, arm at index {arm} returned type that cannot be converted to a floating point number: {type(s)}')

    self._current_rewards[arm] = s

    # Collect the pdf from which this sample was taken
    if a.has_pdf:
      pdf = a.pdf(self._current_step)

      assert isinstance(pdf, tuple), "PDF function returned non tuple return type. Make sure that all methods 'pdf' of BanditArm return a x,y tuple"
      assert len(pdf) == 2, "PDF function returned tuple of invalid size. Make sure that all methods 'pdf' of BanditArm return a x,y tuple"

      self._current_pdfs[arm] = pdf

    return s
  
  def _get_pdf_trace(self, step):
    '''
    This method constructs a plotly Violin trace from the probability density information provided by each arm.
    '''
    if self._current_step is None:
      raise AssertionError('The _get_pdf_trace() method can only be used after the problem has been started. To start a problem, call "sample(arm)" or "step()" at least once')
    
    if self._current_step <= step:
      raise AssertionError('The _get_pdf_trace() can only be used with steps which have been completed. To complete a step call the step() method.')
    
    traces = []

    # Create a Violin trace for each pdf in the specified time step
    for arm in self._historical_pdfs[step]:
      v = go.Violin(
        x = self._historical_pdfs[step][arm][0],
        y = self._historical_pdfs[step][arm][1],
        name = f'Arm: {arm}',
        box_visible = True
      )

      traces.append(v)

    return traces
