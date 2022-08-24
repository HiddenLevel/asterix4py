from typing import Any, Dict
from xml.dom import minidom

from asterix4py.icao6bitchars import ICAO6BITCHARS

try:
    import importlib.resources as pkg_resources
except ImportError:  # try backwards compatibility python < 3.7
    import importlib_resources as pkg_resources

from . import config
from .common import AST_XML_FILES

dataItemsCache = {}
uapItemsCache = {}

BYTE_LENGTH = 8


class AsterixEncoder():
    """Encode single ASTERIX msg to bytearray"""

    def __init__(self, asterix_msg: Dict[str, Any]):
        assert isinstance(asterix_msg, dict)
        self.asterix_msg = asterix_msg

        cat = int(self.asterix_msg['cat'])
        if cat not in AST_XML_FILES:
            return None

        self.loadAsterixDefinition(cat)

        self.encoded_result = bytearray()
        self.encoded_result += bytes([cat])
        self.encoded_result += bytes([0, 0])

        del asterix_msg['cat']

        self.encoded = bytearray()
        self.asterix = asterix_msg
        self.encode(cat)

        self.encoded_result += self.encoded

        length = len(self.encoded_result)

        self.encoded_result[1:3] = (length).to_bytes(2, 'big')

    def get_result(self):
        return self.encoded_result

    def loadAsterixDefinition(self, cat):
        try:
            if cat not in dataItemsCache:
                # add asterix category decoding info to cache (10 times
                # faster!)
                xml = pkg_resources.read_text(config, AST_XML_FILES[cat])
                xmlcat = minidom.parseString(xml)
                if xmlcat:
                    category = xmlcat.getElementsByTagName('Category')[0]
                    dataItemsCache[cat] = category.getElementsByTagName(
                        'DataItem')
                    uap = category.getElementsByTagName('UAP')[0]
                    uapItemsCache[cat] = uap.getElementsByTagName('UAPItem')
        except BaseException:
            print('cat %d not supported' % cat)
            return

    def encode(self, cat):
        # encoded length, tmp to 0

        FSPEC_bits = 0
        FSPEC_bits_len = 0

        for uapitem in reversed(uapItemsCache[cat]):
            # FX field
            if FSPEC_bits_len % BYTE_LENGTH == 0:
                if FSPEC_bits != 0:
                    FSPEC_bits += (1 << FSPEC_bits_len)
                else:  # if all the previous field is zero, discard it
                    FSPEC_bits_len = 0
                FSPEC_bits_len += 1
                continue

            # other uapitem field
            id = uapitem.firstChild.nodeValue
            if id in self.asterix:
                if not self.asterix[id]:
                    del self.asterix[id]
                    continue
                FSPEC_bits += (1 << FSPEC_bits_len)

            FSPEC_bits_len += 1

        self.encoded += (FSPEC_bits).to_bytes(FSPEC_bits_len //
                                              BYTE_LENGTH, byteorder='big')

        for uapitem in uapItemsCache[cat]:
            id = uapitem.firstChild.nodeValue
            if id not in self.asterix:
                continue

            for dataitem in dataItemsCache[cat]:
                itemid = dataitem.getAttribute('id')
                if itemid == id:
                    dataitemformat = dataitem.getElementsByTagName(
                        'DataItemFormat')[0]
                    for cn in dataitemformat.childNodes:
                        r = None
                        if cn.nodeName == 'Fixed':
                            n, r = self.encode_fixed(self.asterix[itemid], cn)
                        elif cn.nodeName == 'Repetitive':
                            n, r = self.encode_repetitive(
                                self.asterix[itemid], cn)
                        elif cn.nodeName == 'Variable':
                            n, r = self.encode_variable(
                                self.asterix[itemid], cn)
                        elif cn.nodeName == 'Compound':
                            n, r = self.encode_compound(
                                self.asterix[itemid], cn)
                        if r:
                            self.encoded += r

    def encode_fixed(self, data_asterix, datafield):
        length = int(datafield.getAttribute('length'))
        bitslist = datafield.getElementsByTagName('Bits')

        encoded_bytes = 0
        encoded_num = 0  # the num of encoded asterix sub filed
        for bits in bitslist:
            bit_name = bits.getElementsByTagName('BitsShortName')[
                0].firstChild.nodeValue
            if bit_name in data_asterix:
                # skip spare,FX and zero subfield
                if bit_name in ['FX', 'spare'] or data_asterix[bit_name] == 0:
                    del data_asterix[bit_name]
                    continue

                encoded_num += 1
                bit = bits.getAttribute('bit')
                if bit != '':
                    _shift = int(bit) - 1
                    encoded_bytes |= (1 << _shift)
                else:
                    _from = int(bits.getAttribute('from'))
                    _to = int(bits.getAttribute('to'))

                    if _from < _to:  # swap values
                        _from, _to = _to, _from
                    v = data_asterix[bit_name]

                    encode = bits.getAttribute('encode')

                    BitsUnit = bits.getElementsByTagName("BitsUnit")

                    if BitsUnit:
                        scale = BitsUnit[0].getAttribute('scale')
                        v = int(v / float(scale))
                    if encode == 'octal':
                        v = int(v, BYTE_LENGTH)
                    elif encode == '6bitschar':
                        v = self._6bitchars_to_bits(v)
                    elif encode == 'ascii':
                        v = int.from_bytes(v.encode(), 'big')
                    elif encode == 'unsigned':
                        mask = (1 << (_from - _to + 1)) - 1
                        v &= mask

                    v <<= (_to - 1)
                    encoded_bytes |= v

                del data_asterix[bit_name]
        return encoded_num, (encoded_bytes).to_bytes(length, 'big')

    def _6bitchars_to_bits(self, cs):
        bitvalue = 0
        for c in cs:
            bitvalue = (bitvalue << 6) + ICAO6BITCHARS.index(c)
        return bitvalue

    def encode_variable(self, data_asterix, datafield):
        result = bytearray()
        encoded_num = 0

        for fixed in datafield.getElementsByTagName('Fixed'):
            n, r = self.encode_fixed(data_asterix, fixed)
            encoded_num += n
            result += r

            if data_asterix:
                result[-1] |= 1  # set FX=1
            else:
                break
        return encoded_num, result

    def encode_repetitive(self, data_asterix, datafield):
        if not isinstance(data_asterix, list):
            data_asterix = list(data_asterix.values())
        result = bytearray()

        length = len(data_asterix)
        result += bytes([length])  # one byte length
        encoded_num = 0

        # repetive has only one subfiled, Fixed
        fixed = datafield.getElementsByTagName('Fixed')[0]
        for subdata in data_asterix:
            n, r = self.encode_fixed(subdata, fixed)
            encoded_num += n
            result += r
        return encoded_num, result

    def encode_compound(self, data_asterix, datafield):
        result = bytearray()
        encoded_num = 0

        subfield_names = {}
        indicator_bits = []
        # --------------------------get subfields names-------------
        for cn in datafield.childNodes:
            if cn.nodeName == 'Variable':
                bitslist = cn.getElementsByTagName('Bits')
                index = 1
                p = 0
                for bits in bitslist:
                    bit_name = bits.getElementsByTagName(
                        'BitsShortName')[0].firstChild.nodeValue
                    p += 1
                    if bit_name == 'spare' or bit_name == 'FX':
                        continue
                    if bit_name in data_asterix:
                        subfield_names[index] = bit_name
                        indicator_bits.append(p)
                    index += 1
                break
        index = -1
        indexs = []
        for cn in datafield.childNodes:

            if cn.nodeName not in [
                    'Fixed', 'Repetitive', 'Variable', 'Compound']:
                continue

            index += 1  # current node index

            if index == 0:  # skip first node, it's indicator
                continue
            if index % BYTE_LENGTH == 0:  # Fx field
                index += 1

            if index not in subfield_names:
                continue

            if cn.nodeName == 'Fixed':
                n, r = self.encode_fixed(
                    data_asterix[subfield_names[index]], cn)
            elif cn.nodeName == 'Repetitive':
                n, r = self.encode_repetitive(
                    data_asterix[subfield_names[index]], cn)
            elif cn.nodeName == 'Variable':
                n, r = self.encode_variable(
                    data_asterix[subfield_names[index]], cn)
            elif cn.nodeName == 'Compound':
                n, r = self.encode_compound(
                    data_asterix[subfield_names[index]], cn)

            encoded_num += n
            result += r
            indexs.append(index)

        indicator = 0
        maxindex = indexs[-1]
        # how many indicator bytes
        indicator_bytes = (maxindex + 7) // BYTE_LENGTH

        # set indicator bits
        for index in indicator_bits:
            _shift = indicator_bytes * BYTE_LENGTH - index
            indicator |= (1 << _shift)

        # set Fx bits
        for i in range(1, indicator_bytes):  # lasst Fx is zero
            _shift = i * BYTE_LENGTH
            indicator |= (1 << _shift)

        result = (indicator).to_bytes(indicator_bytes, 'big') + result
        return encoded_num, result
