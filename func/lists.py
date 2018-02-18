from itertools import chain


class FunctionalList:
  def __init__(self, xs):
    self.xs = xs

  def iterator(self):
    return FunctionalList(iter(self.xs))


  def _apply(self, what, f):
    return FunctionalList(list(what(f, self.xs)))

  def map(self, f):
    return self._apply(map, f)

  def filter(self, f):
    return self._apply(filter, f)

  def flatmap(self, f):
    return FunctionalList(list(chain.from_iterable(map(f, self.xs))))

  def take(self, n):
    return FunctionalList(self.xs[:n])

  def find(self, f):
    xs = self.filter(f)
    if xs:
      return xs[0]
    else:
      return None

  def mk_string(self, delimiter):
    return delimiter.join(self.map(str))

  def __getitem__(self, item):
    return self.xs[item]

  def __str__(self, *args, **kwargs):
    return str(self.xs)


def of(xs):
  return FunctionalList(xs)
