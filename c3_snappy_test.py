import snappy
import sys
import json

# one = 19190200293332222
# text = one.to_bytes((one.bit_length()+7)//8, sys.byteorder)
# comp = snappy.compress(text)
# print(comp)
# uncomp = snappy.uncompress(comp)
# print(int.from_bytes(uncomp, sys.byteorder))

# compressor = snappy.StreamCompressor()
# test="1,2"
# comp = snappy.compress(test)
# print(sys.getsizeof(comp))
# print(comp)
# uncomp = snappy.uncompress(comp)
# print(sys.getsizeof((uncomp)))
# # print(list(uncomp))
# print(str(uncomp))


test='1,2,3,4,5,6'
test=test.encode('utf-8')
comp = snappy.compress(test)
print(comp)
uncomp = snappy.uncompress(comp)
print(uncomp.decode('utf-8'))
# print(str(uncomp))
# print(len(comp))


