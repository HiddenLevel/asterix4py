import copy
import asterix4py


b = open('../sample/cat048.ast', 'rb').read()

decoder = asterix4py.AsterixParser(b)
parser_result = decoder.get_result()[1]

encoder = asterix4py.AsterixEncoder(copy.deepcopy(parser_result))
encoder_result = encoder.get_result()

print('dec: ', memoryview(b).tolist())
print('hex: ', [f'{i:02X}' for i in memoryview(b).tolist()])
print('AsterixParser result: ', parser_result)
print('AsterixEncoder result: ', bytes(encoder_result))
print('bytes read result    : ', bytes(memoryview(b).tolist()))
