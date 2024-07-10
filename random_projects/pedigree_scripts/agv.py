#!/usr/bin/env python3

from pedigree import *

class AgvMatrix(object):
  """
  Additive Genetic Variance Matrix
  """
  
  def __init__(self):
    self.data = dict()
    self.predef = list()
    
  def doPredef(self):
    for (id1, id2, agv) in self.predef:
      self.setAgv(id1, id2, agv)    

  def process(self, pedigree, id1, id2):
    (father, mother) = pedigree.get(id2)
    if id1 == id2:
      f = self.getAgv(father, mother)/2.0
      if f > 0:
        self.setAgv(id1, id1, 1.0 + f)
      return
    self.setAgv(id1, id2, (self.getAgv(id1, father) + self.getAgv(id1, mother)) / 2.0)
    
  def processPedigree(self, pedigree):
    # Need a normilized pedigree
    pedigree.normalize()
    # First processing the predefs
    self.doPredef()
    self.predef = list()
    # Initializing for the actual work
    father1 = ''
    father2 = ''
    mother1 = ''
    mother2 = ''
    for id2 in pedigree.keys:
      ids = pedigree.keys
      for id1 in ids[:ids.index(id2)+1]:
        # id1 is always older (or equal) then id2
        self.process(pedigree, id1, id2)

  def sort(self, one, two):
    if (one > two):
      return (two, one)
    else:
      return (one, two)
    
  def getAgv(self, one, two):
    # If one is non existing return 0.0
    if one == '':
      return 0.0
    if two == '':
      return 0.0
    # For reals, sort first
    (one, two) = self.sort(one, two)
    if one in self.data:
      onedict = self.data[one]
      if two in onedict:
        return onedict[two]
    if one == two:
      return 1.0
    return 0.0
    
  def setAgv(self, one, two, agv):
    (one, two) = self.sort(one, two)
    old = 0
    if one == two:
      old = 1
    if one in self.data:
      onedict = self.data[one]
      if two in onedict:
        old = onedict[two]
      onedict[two] = agv
    else:
      self.data[one] = {two: agv}
    return old
    
  def setInbreeding(self, one, agv):
    self.setAgv(one, one, agv)
    
  def setKinship(self, one, two, kinship):
    self.setAgv(one, two, kinship*2.0)
  
  def getKinship(self, one, two):
    return self.getAgv(one, two)/2.0
    
  def parseline(self, line):
    if line[:5] == '@AGV ':
      keys = line[5:].split(' ')
      if len(keys) >= 3:
        self.predef.append((keys[0], keys[1], float(keys[2])))
      return True
    return False
    
  def dump(self):
    result = ""
    for one in self.data:
      for two in self.data[one]:
        result += "%s %s %s\n" % (one, two, self.data[one][two])
    return result
    
  def txtMatrix(self, pedigree):
    pedigree.normalize()
    size = 10
    result = "{:>9}|".format('')[(-size):]
    for id2 in pedigree.getIds():
      result += "{:>9}|".format(id2)[(-size):]
    result += "\n"
    for id2 in pedigree.getIds():
      result += "{:->9}+".format('-')[(-size):]
    result += "{:->9}+".format('-')[(-size):]
    result += "\n"
    for id1 in pedigree.getIds():
      result += "{:>9}|".format(id1)[(-size):]
      for id2 in pedigree.getIds():
        result += "{:>9}|".format("{:.2%} ".format(self.getAgv(id1, id2)))
      result += "\n"
    return result
    
  def csv(self, pedigree, comma, separator):
    pedigree.normalize()
    result = "AGV" + separator
    for id2 in pedigree.getIds():
      result += id2 + separator
    result += "\n"
    for id1 in pedigree.getIds():
      result += id1 + separator
      for id2 in pedigree.getIds():
        value = "{:.4}"
        result += "{:.4}".format(self.getAgv(id1, id2)).replace('.', comma) + separator
      result += "\n"
    return result


class PcagvMatrix(AgvMatrix):
  '''
  TODO: does not yet all it is supposed to do. Should create a different self.pcdata. And it should calculate inbreeding, but not use it for the calculation.
  Purging correcte AGV matrix.
  
  The only real difference is that inbreeding is never used for calculating 
  the PCAGV.
  '''
  
  def __init__(self):
    super(PcagvMatrix, self).__init__()
    self.pcdata = dict()

  def doPredef(self):
    super(PcagvMatrix, self).doPredef()
    for (id1, id2, agv) in self.predef:
      self.setPcagv(id1, id2, agv)    

  def process(self, pedigree, id1, id2):
    super(PcagvMatrix, self).process(pedigree, id1, id2)
    (father, mother) = pedigree.get(id2)
    if id1 == id2:
      f = self.getPcagv(father, mother)/2.0
      if f > 0:
        self.setPcagv(id1, id1, 1.0 + f)
      return
    self.setPcagv(id1, id2, (self.__getPcagv(id1, father) + self.__getPcagv(id1, mother)) / 2.0)

  def setPcagv(self, one, two, agv):
    (one, two) = self.sort(one, two)
    old = 0
    if one == two:
      old = 1
    if one in self.pcdata:
      onedict = self.pcdata[one]
      if two in onedict:
        old = onedict[two]
      onedict[two] = agv
    else:
      self.pcdata[one] = {two: agv}
    return old
    
  def __getPcagv(self, one, two):
    if one == two:
      return 1.0
    return self.getPcagv(one, two)
    
  def getPcagv(self, one, two):
    # If one is non existing return 0.0
    if one == '':
      return 0.0
    if two == '':
      return 0.0
    # For reals, sort first
    (one, two) = self.sort(one, two)
    if one in self.pcdata:
      onedict = self.pcdata[one]
      if two in onedict:
        return onedict[two]
    if one == two:
      return 1.0
    return 0.0    

  def pcTxtMatrix(self, pedigree):
    pedigree.normalize()
    size = 10
    result = "{:>9}|".format('')[(-size):]
    for id2 in pedigree.getIds():
      result += "{:>9}|".format(id2)[(-size):]
    result += "\n"
    for id2 in pedigree.getIds():
      result += "{:->9}+".format('-')[(-size):]
    result += "{:->9}+".format('-')[(-size):]
    result += "\n"
    for id1 in pedigree.getIds():
      result += "{:>9}|".format(id1)[(-size):]
      for id2 in pedigree.getIds():
        result += "{:>9}|".format("{:.2%} ".format(self.getPcagv(id1, id2)))
      result += "\n"
    return result
    
  def pcCsv(self, pedigree, comma, separator):
    pedigree.normalize()
    result = "AGV" + separator
    for id2 in pedigree.getIds():
      result += id2 + separator
    result += "\n"
    for id1 in pedigree.getIds():
      result += id1 + separator
      for id2 in pedigree.getIds():
        value = "{:.4}"
        result += "{:.4}".format(self.getPcagv(id1, id2)).replace('.', comma) + separator
      result += "\n"
    return result
    

if __name__ == '__main__':
  a = PcagvMatrix()
  p = testPedigree()
  if len(sys.argv) > 1:
    p = FilteredPedigree()
    p.importFile(sys.argv[1], instruction=a.parseline)
    if len(p.getIds()) == 0:
      p.show(p.getAllIds())
  a.processPedigree(p)
  #print(a.dump())
  if len(sys.argv) > 1:
    (root, sep, ext) = sys.argv[1].rpartition('.')
    fh = open(root + '.csv', 'w')
    fh.write(a.csv(p,',',';'))
    fh.close()
    fh = open(root + '.p.csv', 'w')
    fh.write(a.pcCsv(p,',',';'))
    fh.close()
  else:
    print(a.txtMatrix(p))
    print(a.csv(p,'.',','))
    print(a.pcTxtMatrix(p))
    print(a.pcCsv(p,'.',','))

