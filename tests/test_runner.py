from bandidos import BanditProblem, BanditArm, BanditRunner
from bandidos.builtins.arms import NormalArm

def temporary():
  p = BanditProblem(30)
  p.add_arm(NormalArm)
  p.add_arm(NormalArm)

  r = BanditRunner(p)

  r._plot()

if __name__ == '__main__':
  temporary()