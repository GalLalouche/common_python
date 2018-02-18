import os
import os.path as op
import tempfile
import shutil


class RichFile:
  """Mostly a fluent API wrapper for the regular python file API"""
  """Since I'm too lazy to use proper open anyway"""

  def __init__(self, path):
    self.f = path

  def _writelns(self, what, mode):
    with open(self.f, mode) as f:
      for line in what:
        f.write(line + "\n")
    return self

  def appendln(self, what):
    return self.appendlns([what])

  def appendlns(self, what):
    return self._writelns(what, 'a')

  def writeln(self, what):
    return self.writelns([what])

  def writelns(self, what):
    return self._writelns(what, 'w')


  def clear(self):
    open(self.f, 'w').close()
    return self

  def lines(self):
    """Unlike readLines(), this trims that goddamn \n"""
    return list(open(self.f, 'r').read().splitlines())

  def basename(self):
    return op.basename(self.f)

  def exists(self):
    return op.isfile(self.f)

  def abspath(self):
    return op.abspath(self.f)

  def find_line_number(self, pred):
    for i, line in enumerate(self.lines()):
      if pred(line):
        return i
    return -1

  def copy_to(self, dst):
    return RichFile(shutil.copy(self.f, dst))

  def remove(self, lines):
    approved_lines = []
    for (i, line) in enumerate(self.lines()):
      if i not in lines:
        approved_lines.append(line)

    self.clear()
    for line in approved_lines:
      self.appendln(line)

  def insert(self, lines):
    class Temp:
      def in_line(_, line_no):
        fixed_lines = []
        for (i, original_line) in enumerate(self.lines()):
          if i == line_no:
            for input_line in lines:
              fixed_lines.append(input_line)
          fixed_lines.append(original_line)

        self.clear()
        for original_line in fixed_lines:
          self.appendln(original_line)

    return Temp()

  def backup(that):
    """Creates a backup copy of the original file. example use:
       with f.back() as b:
         # do some stuff with b
         b.commit()
    """
    class Backup(RichFile):
      def __init__(self):
        self.original = that.f

      def __enter__(self):
        self.f = tempfile.NamedTemporaryFile(delete=False).name
        for line in that.lines():
          self.appendln(line)
        return self

      def __exit__(self, exc_type, exc_val, exc_tb):
        os.remove(self.f)

      def commit(self):
        that.clear()
        for line in self.lines():
          that.appendln(line)
        return self

    return Backup()

  def memory(that):
    """Creates an in-memory representation of the file"""
    class Memory(RichFile):
      def _writelns(self, what, mode):
        if mode is 'w':
          self.memLines = what
        elif mode is 'a':
          self.memLines += what
        else:
          raise "Invalid mode " + mode

      def lines(self):
        return self.memLines

      def __init__(self):
        self.f = that.f
        self.memLines = that.lines()
      def commit(self):
        that.writelns(self.memLines)
      def indent(that, opener=None, closer=None):
        """"Creates a new managed file, with optional openers and closers that will
        indent all written text. supports multiple, recursive indentations"""

        class Managed(Memory):
          def __init__(self, opener=opener, closer=closer, _level=1):
            self.f = that.f
            self._level = _level
            self._opener = opener
            self._closer = closer
            self.memLines = that.memLines

          def _writelns(self, what, mode):
            return Memory._writelns(self, map(lambda l: ("  " * self._level) + l, what), mode)

          def __enter__(self):
            if self._opener:
              self._level -= 1
              self.appendln(self._opener)
              self._level += 1
            return self

          def __exit__(self, exc_type, exc_val, exc_tb):
            if self._closer:
              self._level -= 1
              self.appendln(self._closer)
              self._level += 1

          # For recursive indentations
          def indent(self, _opener=None, _closer=None):
            return Managed(_opener, _closer, self._level + 1)
        return Managed()  # now, to inline this...

    return Memory()


if __name__ == '__main__':
  file = RichFile("/tmp/pyfile")
  file.clear()
  file \
    .appendln("foo") \
    .appendln("bar") \
    .appendln("spam") \
    .appendln("eggs")

  m = file.memory()
  m.appendln("foobar")
  print(file.lines())
