import snappy
import sys

one = 19190200293332222
text = one.to_bytes((one.bit_length()+7)//8, sys.byteorder)
comp = snappy.compress(text)
print(comp)
uncomp = snappy.uncompress(comp)
print(int.from_bytes(uncomp, sys.byteorder))
