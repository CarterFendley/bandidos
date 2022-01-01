import pytest
import numpy as np
from scipy.stats import norm

from bandidos.builtins.arms import NormalArm

class TestNormalArm:
  def test_basic_init(self):
    na = NormalArm(3)

    # Make sure mean=0 & sd=1 when no arguments provided
    assert na.mean == 0
    assert na.sd == 1
  
  def test_input_mean_sd(self):
    mean_arm = NormalArm(3, 10)
    assert mean_arm.mean == 10
    assert mean_arm.sd == 1

    both_arm = NormalArm(3, 15.0, 0.2)
    assert both_arm.mean == 15
    assert both_arm.sd == 0.2
  
  def test_invalid_input(self):
    with pytest.raises(ValueError):
      NormalArm(3, 'Wrong type')
    with pytest.raises(ValueError):
      NormalArm(3, 10, 'Wrong type')
  
  def test_pdf(self):
    a = NormalArm(3)

    x, y = a.pdf(1) # Use a random step as it should not matter

    # Check that y corresponds to the pdf values for each x in a normal distribution with mean=0 & sd=1
    pdf_vals = norm.pdf(x)
    assert np.allclose(y, pdf_vals)
  
  def test_sample_return_type(self):
    a = NormalArm(3)

    for i in range(10):
      s = a.sample(1)
      assert isinstance(s, float)