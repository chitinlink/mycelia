class A:
  def __init__(self, foo):
    print(f"{self.__class__.__name__}")
    self.foo = foo

class B(A):
  def __init__(self, foo, bar):
    super().__init__(foo)
    self.bar = bar

test = B("aaaa", "bbbbbar")
