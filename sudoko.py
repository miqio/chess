from copy import copy, deepcopy

class SolverConflictException(Exception):
  pass
  
class FoundNoPairException(Exception):
  pass
  
class Solver:
  
  def __init__(self, fields=None):
    self._redolist=[]
    self._matrix=[]
    self._locations=[]
    self.isRunning=True
    if fields: self.matrify(fields)
  
  def matrify( self,fields ):
    self._matrix = [[int(x) if x.isdigit() else list((1,2,3,4,5,6,7,8,9)) for x in array] for array in fields]
  
  def run(self):
    print "Starting from:"
    fineprint(self._matrix)
    step=0
    while True:
      self._step()
      step+=1
      if self.foundSolution():
        print "Found solution at step %i:" % step
        fineprint(self._matrix)
        return
      else:
        self.proposeValue()
        
  def proposeValue(self):
    self._redolist.append( deepcopy(self._matrix) )
    if not self._startSetHasElements(2) and not self._startSetHasElements(3):
      raise FoundNoPairException("Did not find any solution set with less than four elements!")
  
  def _startSetHasElements(self, length=2):
    for i in range(0,9):
      for j in range(0,9):
        el = self._matrix[i][j]
        if type(el)==list and len(el)==length:
          self._locations.append((i,j))
          el=self._redolist[-1][i][j]
          self._matrix[i][j] = el.pop()
          self.isRunning=True
          return True
    return False
  
  def _step(self):
    k=0
    while self.isRunning:
      try:
        self._iterate()
        k+=1
      except SolverConflictException:
        i,j=self._locations[-1]
        solset = self._redolist[-1][i][j]
        if len(solset)==1:
          self._matrix = self._redolist.pop()
          self._locations.pop()
        else:
          self._matrix = deepcopy( self._redolist[-1] )
        self._matrix[i][j] = solset.pop()
    return

  def _iterate(self):
    self.isRunning=False
    return [[ self.candidates(i,j) for j in range(0,9)] for i in range(0,9) ]
    
  def candidates(self,i,j):
    m = self._matrix[i][j]
    n=copy(m)
    if type(m)==int: return m
    for cand in n:
      if not self.isCandidate(cand,i,j):
        m.remove(cand)
        self.isRunning=True
    if len(m)>1:
      return m
    elif not m:
      raise SolverConflictException("Found conflict for row %i and col %i" % (i+1,j+1))  
    else:
      self._matrix[i][j]=m[0]
      return m[0]
      
  def isCandidate(self,x,i,j):
    m=self._matrix
    return self.isNewInVec(m[i],x) and self.isNewInVec(self.getCol(j),x) and self.isNewInVec(self.getBlock(i,j),x)

  def isNewInVec(self,u,x):
    v=set()
    for el in u:
      if type(el)==int: v.add(el)
    l0=len(v)
    v.add(x)
    l1=len(v)
    if l0!=l1:
      return True
    else:
      return False

  def getBlock(self,i,j):
    i0,k0=divmod(i,3)
    j0,l0=divmod(j,3)
    block=list()
    for k in range(i0*3,i0*3+3):
      for l in range(j0*3,j0*3+3):
        block.append(self._matrix[k][l])
    return block

  def getCol(self,i):
    return [self._matrix[rind][i] for rind in range(0,9)]
    
  def foundSolution(self):
    for v in self._matrix:
      for el in v:
        if type(el)==list: return False
    return True
    
  def checkSolution(self):
    if not self.foundSolution():
      return False
    for i in range(0,9):
      if len(set(self._matrix[i]))!=9: return False
      if len(set(self.getCol(i)))!=9: return False
    for i in range(0,3):
      for j in range(0,3):
        if len(set(self.getBlock(3*i,3*j)))!=9: return False
    return True
    
def fineprint(m):
  fineprint=''
  for v in m:
    for el in v:
      if type(el)==int:
        fineprint+=' %i'% el
      else:
        fineprint+='  '
    fineprint+='\n'
  print fineprint

