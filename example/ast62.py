import asterix4py

b = open('../sample/cat062.ast', 'rb').read()
print('dec: ', memoryview(b).tolist())
print('hex: ', [f'{i:02X}' for i in memoryview(b).tolist()])

decoder = asterix4py.AsterixParser(b)
print('decode: ', decoder.get_result())
