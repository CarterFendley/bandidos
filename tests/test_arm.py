import pytest

from bandidos import BanditArm

class BasicArm(BanditArm):
  def sample(self, step):
    return 3

class TestInit:
  def test_bad_steps(self):
    with pytest.raises(AssertionError):
      BasicArm(3.0)

    with pytest.raises(AssertionError):
      BasicArm(0)

    with pytest.raises(AssertionError):
      BasicArm(-1)
  
  def test_fail_direct_instantiate(self):
    with pytest.raises(AssertionError):
      BanditArm(3)

  def test_fail_call_sample(self):
    class BadArm(BanditArm):
      sample = None
    with pytest.raises(AttributeError):
      BadArm(3)

  def test_fail_args_sample(self):
    class BadArm(BanditArm):
      def sample(self, step, more, args):
        pass
    with pytest.raises(AssertionError):
      BadArm(3)


  def test_pass_on_minimal(self):
    class GoodArm(BanditArm):
      def sample(self, step):
        pass

    GoodArm(3)

  def test_pass_on_setup(self):
    class GoodArm(BanditArm):
      setup_called = False
      def sample(self, step):
        pass

      def setup(self, steps, *args):
        self.setup_called = True

    g = GoodArm(3)
    assert g.setup_called

class TestProperties:
  def test_pdf_method(self):
    class PdfArm(BasicArm):
      def pdf(self, step):
        pass

    a = PdfArm(3)
    assert a.has_pdf
  
  def test_pdf_lambda(self):
    class LambdaPdf(BasicArm):
      # Simple python inline function which takes in 'step' and always returns 1 
      def setup(self, steps, *args):
        self.pdf = lambda step: 1

    a = LambdaPdf(3)
    assert a.has_pdf

  def test_step_method(self):
    class StepArm(BasicArm):
      def step(self, step):
        pass

    a = StepArm(3)
    assert a.has_step
  
  def test_step_lambda(self):
    class StepLambda(BasicArm):
      def setup(self, steps, *args):
        self.step = lambda step: 1
    
    a = StepLambda(3)
    assert a.has_step
  
  def test_no_optionals(self):
    a = BasicArm(3)
    assert not a.has_pdf
    assert not a.has_step