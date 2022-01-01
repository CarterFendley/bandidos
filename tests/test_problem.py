import pytest
import random
import numpy as np
from scipy.stats import norm
import plotly.graph_objects as go

from bandidos import BanditProblem, BanditArm
from bandidos.builtins.arms import NormalArm

class MockArm(BanditArm):
  def setup(self, steps, *args):
    # Record args as it is useful to check injection in tests
    self.args = args

  def sample(self, step):
    return 4

class TestTypeChecking:
  def test_on_bad_steps(self):
    with pytest.raises(AssertionError):
      BanditProblem(3.0)
    
    with pytest.raises(AssertionError):
      BanditProblem(0)
    
    with pytest.raises(AssertionError):
      BanditProblem(-1)

  def test_add_non_class_arm(self):
    p = BanditProblem(3)
    with pytest.raises(AssertionError):
      p.add_arm(None)

  def test_add_bad_class_arm(self):
    class BadClass:
      pass

    p = BanditProblem(3)
    with pytest.raises(AssertionError):
      p.add_arm(BadClass)

  def test_add_instance_arm(self):
    p = BanditProblem(3)
    with pytest.raises(AssertionError):
      p.add_arm(MockArm(3))
  
  def test_sample_bad_arm(self):
    p = BanditProblem(3)
    p.add_arm(MockArm)

    with pytest.raises(AssertionError):
      p.sample(None)

    with pytest.raises(AssertionError):
      p.sample(-1)

    with pytest.raises(AssertionError):
      p.sample(1)

class TestBasic:
  def test_basic_sample(self):
    p = BanditProblem(3)
    a = p.add_arm(MockArm)

    assert isinstance(a, MockArm)

    assert p.sample(0) == 4
  
  def test_caching_sample(self):
    # Fix the seed so we get deterministic behavior 
    random.seed(10)
    # This is the first number that will be generated by random.random()
    first_random = 0.5714025946899135
    second_random = 0.4288890546751146

    class RandomArm(BanditArm):
      def sample(self, step):
        return random.random()
    
    p = BanditProblem(10)
    a = p.add_arm(RandomArm)

    
    assert p.sample(0) == first_random

    # Make sure it is the same on subsequent calls
    assert p.sample(0) == first_random

    # Make sure after steps, we recieve the next value
    p.step()
    assert p.sample(0) == second_random


class TestArmContract:
  def test_step_injection(self):
    for steps in range(1, 50):
      p = BanditProblem(steps)
      
      a = p.add_arm(MockArm)
      assert a.steps == steps
  
  def test_arg_injection(self):
    for fake_arg1 in range(1, 50):
      p = BanditProblem(100)

      a = p.add_arm(MockArm, fake_arg1)
      assert len(a.args) == 1
      assert a.args[0] == fake_arg1
    
    # Test with a number of args
    for num_args in range(1, 10):
      # Create a list of arguments 0, ..., num_args to check uniqueness
      args = [i for i in range(num_args)]

      # *args syntax unpacks the args list into the positional args of the method call 
      a = p.add_arm(MockArm, *args)

      # Sanity check on the size
      assert len(a.args) == num_args

      # Check elements, tuple() is required bc python converts *args into a tuple form
      assert a.args == tuple(args)

  def test_bad_sample(self):
    # Idea is to make sure we output errors immediately if instances of BanditArm misbehave
    class BadSample(BanditArm):
      def sample(self, step):
        return 'Wrong type'
    
    p = BanditProblem(40)
    p.add_arm(BadSample)

    with pytest.raises(ValueError):
      p.sample(0)
  
  def test_bad_pdf(self):
    class BadPDF(MockArm):
      def pdf(self, step):
        return 'Not a tuple'
    
    p = BanditProblem(40)
    p.add_arm(BadPDF)

    with pytest.raises(AssertionError):
      p.sample(0)

    class BadPDF2(MockArm):
      def pdf(self, step):
        return 'Too', 'many', 'args'
    
    p = BanditProblem(40)
    p.add_arm(BadPDF2)

    with pytest.raises(AssertionError):
      p.sample(0)

class TestViolin:
  def test_bad_step(self):
    p = BanditProblem(10)

    with pytest.raises(AssertionError):
      p._get_pdf_trace(0)

    p.step()
    with pytest.raises(AssertionError):
      p._get_pdf_trace(1)
  
  def test_normal_violin(self):
    p = BanditProblem(10)
    p.add_arm(NormalArm)
    p.step()

    traces = p._get_pdf_trace(0)
    assert len(traces) == 1
    
    violin = traces[0]
    assert isinstance(violin, go.Violin)
    
    # Check that the pdf matches a normal distribution
    pdf_vals = norm.pdf(violin['x'])
    assert np.allclose(violin['y'], pdf_vals)