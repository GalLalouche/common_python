from RichFile import RichFile


class ConsoleFile(RichFile):
  def __init__(self):
    self.f = None
  def _writelns(self, what, mode):
    if mode == 'w':
      self.clear()
    for line in what:
      print(line)
    return self
  def clear(self):
    pass
  def lines(self):
    return []
  def commit(self):
    pass

