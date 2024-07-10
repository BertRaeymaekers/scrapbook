import sys
import copy

class Pedigree(object):
  """
  Pedigree
  """
  
  def __init__(self):
    self.__normalized = True
    self.data = dict()
    self.keys = list()
    self.mentioned = list()
    
  def __sort(self, one, two):
    if (one > two):
      return (two, one)
    else:
      return (one, two)
      
  def importFile(self, filename, instruction=False):
    fh = open(filename, 'r')
    for line in fh:
      self.addline(line.rstrip(), instruction)
    fh.close()
    
  def addline(self, line, instruction=False):
    if len(line) == 0:
      return
    if line[0] == "#":
      return
    if line[0] == "@":
      if instruction:
        instruction(line)
      return
    line.replace("\\t", " ")
    parts = line.split(' ', 4)
    while len(parts) < 3:
      parts.append('')

    if parts[2] == '?':
      parts[2] = ''
    if parts[1] == '?':
      parts[1] = ''

    self.add(parts[0].rstrip(), parts[1].rstrip(), parts[2].rstrip())
      
  def add(self, id, father, mother):
    if id == '':
      raise KeyError("Empty id")
    self.__normalized = False
    self.data[id] = (father, mother)
    if father != '':
      if father not in self.keys:
        if father not in self.mentioned:
          self.mentioned.append(father)
    if mother != '':
      if mother not in self.keys:
        if mother not in self.mentioned:
          self.mentioned.append(mother)
    self.keys.append(id)
    
  def get(self, id):
    '''
    Throws a KeyError if id is not in the pedigree
    '''
    return copy.copy(self.data[id])
    
  def getMentioned(self):
    return copy.copy(mentioned)
    
  def getFather(self, id):
    (father, mother) = self.get(id)
    return father
    
  def getMother(self, id):
    (father, mother) = self.get(id)
    return mother
        
  def getIds(self):
    return self.keys
    
  def dump(self):
    result = ""
    for id in self.getIds():
      result += "%s %s %s\\n" % (id, self.data[id][0], self.data[id][1])
    return result
    
  def __append(self, newqueue, holdqueue, id):
    newqueue.append(id)
    # Check if the holdqueue is resolved by this one so we can empty it (!ERR RECURSIVE!)
    if id in holdqueue:
      for child in holdqueue[id]:
        if holdqueue[id][child] == '':
          # If nothing holds it based on the other parent: GO & APPEND
          self.__append(newqueue, holdqueue, child)
        else:
          # The other parent is still blocking it: Resolving the blocking on the other parent
          otherparent = holdqueue[id][child]
          if otherparent in holdqueue:
            if child in holdqueue[otherparent]:
              holdqueue[otherparent][child] = ''
      # Everything solved for this parent
      del holdqueue[id]
    
  def normalize(self):
    '''
    Make sure parents are before childeren
    '''
    if self.__normalized:
      return
    newqueue = self.mentioned
    holdqueue = dict()
    for id in newqueue:
      self.data[id] = ('','')
    for id in self.keys:
      (father, mother) = self.data[id]
      fatherok = False
      motherok = False
      
      # Father already known?
      if father != "":
        if father in newqueue:
          # Father is already int the newqueue
          fatherok = True
        elif father not in self.data:
          # Father isn't in the pedigree
          fatherok = True
      else:
        # No father
        fatherok = True
        
      # Mother already known?
      if mother != "":
        if mother in newqueue:
          # Mother is already int the newqueue
          motherok = True
        elif mother not in self.data:
          # Mother isn't in the pedigree
          motherok = True
      else:
        # No mother
        motherok = True
        
      # Add the missing to the holdqueue
      if not(fatherok):
        if father in holdqueue:
          if motherok:
            holdqueue[father][id] = ''
          else:
            holdqueue[father][id] = mother
        else:
          if motherok:
            holdqueue[father] = {id: ''}
          else:
            holdqueue[father] = {id: mother}
      if not(motherok):
        if mother in holdqueue:
          if fatherok:
            holdqueue[mother][id] = ''
          else:
            holdqueue[mother][id] =  father
        else:
          if fatherok:
            holdqueue[mother] = {id: ''}
          else:
            holdqueue[mother] = {id: father}

      # All OK: append to the newqueue
      if (fatherok & motherok):
        self.__append(newqueue, holdqueue, id)
      
    # The holdqueue should be empty
    self.keys = newqueue
    self.mentioned = list()
    self.__normalized = True


class FilteredPedigree(Pedigree):

  def __init__(self):
    super(FilteredPedigree, self).__init__()
    self.filter = list()
    
  def initPedigree(pedigree):
    self.data = pedigree.data
    self.keys = pedigree.keys
    self.mentioned = self.mentioned
    self.filter = list()
    
  def __show(self, key):
    if key in self.keys:
      self.filter.append(key)
      return True
    else:
      return False
      
  def parseinstruction(self, line):
    if line[:9] == '@VISIBLE ':
      keys = line[9:].split(' ')
      for key in keys:
        if key in self.keys:
          self.filter.append(key)
      return True
    return False
    
  def addline(self, line, instruction=False):
    super(FilteredPedigree, self).addline(line, instruction=self.parseinstruction)
    if len(line) == 0:
      return
    if line[0] == '@':
      if type(instruction).__name__ == 'function':
        return instruction(line)
      elif type(instruction).__name__ == 'instancemethod':
        return instruction(line)
    
  def show(self, keys):
    rc = list()
    if type(keys).__name__=='list':
      for key in keys:
        if self.__show(key):
          rc.append(key)
    else:
      if self.__show(keys):
        rc.append(keys)
    
  def getAllIds(self):
    return self.keys
        
  def getIds(self):
    return self.filter

  def setIds(self, ids):
    self.filter = ids


class PedigreeFilter(object):
  
  def __init__(self, infn):
    self.infn = infn
    
  def applyFilter(self, pedigree):
    ids = pedigree.getAllIds()
    filter = list()
    for id in ids:
      if self.infn(id):
        filter.append(id)
    pedigree.setIds(filter)
    
  def superimposeFilter(self, pedigree):
    ids = pedigree.getIds()
    filter = list()
    for id in ids:
      if self.infn(id):
        filter.append(id)
    pedigree.setIds(filter)


def testCheck(id):
  if len(id) > 2:
    return True
  return False


def testPedigree():
  p = FilteredPedigree()
  p.add('AB', 'A', 'B')
  p.add('AAB', 'A', 'AB')
  p.add('AABC', 'AAB', 'C')
  p.add('AABAABC', 'AAB', 'AABC')
  p.normalize()
  f = PedigreeFilter(testCheck)
  f.applyFilter(p)
  return p

  
if __name__ == '__main__':
  p = testPedigree()
  if len(sys.argv) > 1:
    p = FilteredPedigree()
    p.importFile(sys.argv[1])
  print("ALL ID")
  print(p.getAllIds())
  print('')
  print("ID")
  print(p.getIds())
  print('')
  print("DUMP")
  print(p.dump())
  print('')
  print("MENTIONED")
  print(p.mentioned)
  print('')
  p.normalize()
  print("DUMP AFTER NORMALIZATION")
  print(p.dump())
  print('')
  print("FATHER OF AAB & A")
  print(p.getFather('AAB'))
  print(p.getFather('A'))
  print('')

