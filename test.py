import timeit

setup = """
import hashlib
a = bytearray("ABCDE")
b = "ABCD"
"""
fn = [
"""
a[4] = "F"
op = hashlib.md5(a).hexdigest()
""",
"""
b = b + "F"
op = hashlib.md5(b).hexdigest()
""",
"""
b = b + "F"
op = hashlib.md5(b.encode('utf-8')).hexdigest()
"""]

for f in fn:
  print(timeit.timeit(f, setup, number=1000))
