import plotly.graph_objects as go

from bandidos import BanditProblem

class BanditRunner:
  '''
  A runner should be supplied with a single problem and one or more algorithms. To get a good idea of algorithms performance there is a need to run alogs. against *multiple* initializations of the same problem. Problems can be initalized in a non-deterministic manner such as, choosing the mean for a normal distribution from *another* distribution. Without sampling multiple possible initializations, there is the potential for a the results to not represent the general performance of a algorithm if that algorithm is sensitive to the initial conditions.

  TODO: Will need to create .copy() methods for problems and arms. Maybe not ~copy~ exactly but something that holds the same input params and reinitialize 
  '''
  def __init__(self, problem):
    assert isinstance(problem, BanditProblem), "Expected instance of BanditProblem in first positional argument"
    
    self._problem = problem
  
  def _plot(self):
    # TODO: Temporary step call
    self._problem.step()

    fig = go.Figure()

    pdf_traces = self._problem._get_pdf_trace(0)

    for trace in pdf_traces:
      fig.add_trace(trace)
    
    print('yo')

    fig.show(renderer='browser')
    fig.write_image("figure.png", engine="kaleido")