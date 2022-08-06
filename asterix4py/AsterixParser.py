from xml.dom import minidom

try:
    import importlib.resources as pkg_resources
except ImportError:  # try backwards compatibility python < 3.7
    import importlib_resources as pkg_resources

from .common import AST_XML_FILES
from . import config
from . import icao6bitchars
 
 
dataItemsCache = {}
uapItemsCache = {}


class AsterixParser:
    """Decode bytearray of asterix data"""

    def __init__(self, bytesdata):
        self.bytes = bytesdata
        self.datasize = len(bytesdata)
        self.p = 0
        self.recordnr = 0

        self.decoded_result = {}

        while self.p < self.datasize:
            if self.datasize - self.p <= 3:
                break

            startbyte = self.p
            cat = int.from_bytes(self.bytes[startbyte:startbyte +1], byteorder='big', signed=False)
            length = int.from_bytes(self.bytes[startbyte + 1:startbyte + 3], byteorder='big', signed=False)
            self.p += 3

            if cat not in AST_XML_FILES:
                # ignore unknown categories
                self.p += length
                continue

            self.loadAsterixDefinition(cat)

            last_byte = startbyte + length 
            # Check that there's enough data to decode a message.
            while self.p < last_byte and (last_byte - self.p - 3) > 3:
                self.recordnr += 1
                self.decoded = {'cat': cat}
                if cat in dataItemsCache and cat in uapItemsCache:
                    try:
                        self.decode(dataItemsCache.get(cat), uapItemsCache.get(cat))
                    except Exception as e:
                        self.decoded_result[self.recordnr] = self.decoded
                        self.p = last_byte
                        break
                else:
                    print(f"Error: unable to find asterix cat{cat:03d} in data items cache")
                    self.p = startbyte + length
                self.decoded_result[self.recordnr] = self.decoded

    """get decoded results in JSON format"""

    def get_result(self):
        return self.decoded_result

    def loadAsterixDefinition(self, cat):
        try:
            if cat not in dataItemsCache:
                # add asterix category decoding info to cache (10 times faster!)
                xml = pkg_resources.read_text(config, AST_XML_FILES[cat])
                xmlcat = minidom.parseString(xml)
                if xmlcat:
                    category = xmlcat.getElementsByTagName('Category')[0]
                    dataItemsCache[cat] = category.getElementsByTagName('DataItem')
                    uap = category.getElementsByTagName('UAP')[0]
                    uapItemsCache[cat] = uap.getElementsByTagName('UAPItem')
        except:
            print('cat %d not supported' % cat)
            return

    def decode(self, dataitems, uapitems):
        # ------------------ FSPEC -------------------------------
        fspec_octets = 0
        fspec_octets_len = 0
        while True:
            _b = self.bytes[self.p]
            self.p += 1
            fspec_octets = (fspec_octets << 8) + _b
            fspec_octets_len += 1
            if _b & 1 == 0:
                break
        # ------------------ FSPEC bits to uapitem id --------------------------
        itemids = []  # dataitems
        # mask is 0b1000000000...
        mask = 1 << (8 * fspec_octets_len - 1)

        for i in range(0, 8 * fspec_octets_len):
            if fspec_octets & mask > 0:
                itemid = uapitems[i].firstChild.nodeValue
                if itemid != '-':
                    itemids.append(itemid)

            mask >>= 1

        # ------------------ decode each dataitem --------------------------
        for itemid in itemids:
            for dataitem in dataitems:
                if dataitem.getAttribute('id') == itemid:
                    dataitemformat = dataitem.getElementsByTagName('DataItemFormat')[0]
                    for cn in dataitemformat.childNodes:
                        r = None
                        if cn.nodeName == 'Fixed':
                            r = self.decode_fixed(cn)
                        elif cn.nodeName == 'Repetitive':
                            r = self.decode_repetitive(cn)
                        elif cn.nodeName == 'Variable':
                            r = self.decode_variable(cn)
                        elif cn.nodeName == 'Compound':
                            r = self.decode_compound(cn)
                        elif cn.nodeName == 'Explicit':
                            r = self.decode_explicit(cn)

                        if r:
                            self.decoded.update({itemid: r})

    def decode_fixed(self, datafield):
        results = {}
        length = int(datafield.getAttribute('length'))
        bitslist = datafield.getElementsByTagName('Bits')

        _bytes = self.bytes[self.p: self.p + length]
        self.p += length

        data = int.from_bytes(_bytes, byteorder='big', signed=False)

        for bits in bitslist:
            bit_name = bits.getElementsByTagName('BitsShortName')[0].firstChild.nodeValue

            bit = bits.getAttribute('bit')
            if bit != '':
                bit = int(bit)                
                results[bit_name] = ((data >> (bit - 1)) & 1)

            else:
                from_ = int(bits.getAttribute('from'))
                to_ = int(bits.getAttribute('to'))

                if from_ < to_:  # swap values - fixes errors in xml files
                    from_, to_ = to_, from_

                mask = (1 << (from_ - to_ + 1)) - 1
                fieldBits = ((data >> (to_ - 1)) & mask)  # field value in integer bits

                encode = bits.getAttribute('encode')
                if encode:
                    if encode == 'signed':
                        if fieldBits & (1 << (from_ - to_)):  # signed val
                            fieldBits = - (1 << (from_ - to_ + 1)) + fieldBits
                        results[bit_name] = fieldBits
                    elif encode == 'ascii':
                        results[bit_name] = self.bits_to_ascii(fieldBits)
                    elif encode == 'octal':
                        # we assume this is always a mode A code (4 digits octal)
                        results[bit_name] = f"{fieldBits:04o}"
                    elif encode == '6bitschar':
                        results[bit_name] = self.bits_to_6bitchars(fieldBits)
                    elif encode == 'hex':
                        results[bit_name] = f"{fieldBits:X}"
                    elif encode == 'unsigned':
                        results[bit_name] = fieldBits
                    else:
                        # unknown encoder
                        print(f"Warning: unknown encoding: {encode}")
                        results[bit_name] = fieldBits
                else:
                    results[bit_name] = fieldBits

                # lets pretend this is only used for numeric values
                BitsUnit = bits.getElementsByTagName("BitsUnit")
                if BitsUnit:
                    scale = BitsUnit[0].getAttribute('scale')
                    if not scale:
                        scale = 1
                    results[bit_name] = results[bit_name] * float(scale)

        return results

    def decode_variable(self, datafield):
        results = {}

        for fixed in datafield.getElementsByTagName('Fixed'):
            r = self.decode_fixed(fixed)
            results.update(r)
            assert 'FX' in r
            if r['FX'] == 0:
                break

        return results

    def decode_repetitive(self, datafield):
        rep = self.bytes[self.p]
        self.p += 1

        results = {}  # each repetitive item is numbered
        fixed = datafield.getElementsByTagName('Fixed')[0]
        for i in range(rep):
            r = self.decode_fixed(fixed)
            results[i + 1] = r

        return results

    def decode_compound(self, datafield):
        # first variable field is indicators of all the subfields
        # all subfield indicators
        # --------------------------get indicators-------------
        indicator_octets = 0
        indicator_octetslen = 0
        while True:
            _b = self.bytes[self.p]
            self.p += 1
            indicator_octets = (indicator_octets << 8) + _b
            indicator_octetslen += 1

            if _b & 1 == 0:  # FX is zero
                break

        indicators = []
        mask = 1 << (8 * indicator_octetslen - 1)
        indicator = 1
        for i in range(0, 8 * indicator_octetslen):
            if i % 8 == 7:  # i is FX
                continue

            if indicator_octets & (mask >> i) > 0:
                indicators.append(indicator)

            indicator += 1

        subfield_names = {}
        # --------------------------get subfields names-------------
        for cn in datafield.childNodes:
            if cn.nodeName == 'Variable':
                bitslist = cn.getElementsByTagName('Bits')
                indicators_p = 1
                index = 1
                for bits in bitslist:
                    bit_name = bits.getElementsByTagName('BitsShortName')[0].firstChild.nodeValue
                    if bit_name == 'spare' or bit_name == 'FX':
                        indicators_p += 1
                        continue
                    if indicators_p in indicators:
                        subfield_names[index] = bit_name
                    index +=1
                    indicators_p += 1
                break
            
        # --------------------decode data------------------------
        results = {}
        index = 0
        for cn in datafield.childNodes:
            if cn.nodeName not in ['Fixed', 'Repetitive', 'Variable', 'Compound']:
                continue
            if index not in subfield_names:
                index += 1
                continue
            if subfield_names[index] not in results:
                results[subfield_names[index]] = {}
            if cn.nodeName == 'Fixed':
                r = self.decode_fixed(cn)
            elif cn.nodeName == 'Repetitive':
                r = self.decode_repetitive(cn)
            elif cn.nodeName == 'Variable':
                r = self.decode_variable(cn)
            elif cn.nodeName == 'Compound':
                r = self.decode_compound(cn)

            results[subfield_names[index]].update(r)
            index += 1

        return results
    
    def decode_explicit(self, datafield):
        length = self.bytes[self.p]
        bit_name = datafield.getElementsByTagName('Bits')[0].getElementsByTagName('BitsShortName')[0].firstChild.nodeValue
        results = {}  # Special and reserved fields in CAT21 aren't decoded so just return hex string
        results[bit_name] = self.bytes[self.p+1:self.p + length].hex()
        self.p += length
        
        return results
        
    """convert binary value to 8 bit ascii text string"""

    def bits_to_ascii(self, bitvalue):
        return bitvalue.to_bytes((bitvalue.bit_length() + 7) // 8, 'big').decode()

    """convert to ICAO 6 bit character sequence (callsign, mode S aircraft identification)"""

    def bits_to_6bitchars(self, bitvalue):
        cs = ''
        for i in range(1, 9):
            p = bitvalue & 0b111111
            bitvalue = bitvalue >> 6
            cs = icao6bitchars.ICAO6BITCHARS[p] + cs
        return cs
