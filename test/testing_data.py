
TEST_CAT048 = {
    "140": {
      "ToD": 27354.6015625
    },
    "161": {
      "spare": 0,
      "TRN": 3563
    },
    "170": {
      "CNF": 0,
      "RAD": 2,
      "DOU": 0,
      "MAH": 0,
      "CDM": 0,
      "FX": 0,
      "TRE": 0,
      "GHO": 0,
      "SUP": 0,
      "TCC": 0,
      "spare": 0
    },
    "200": {
      "GSP": 0.12066650390625,
      "HDG": 124.002685546875
    },
    "220": {
      "AA": 3958284
    },
    "230": {
      "COM": 1,
      "STAT": 0,
      "SI": 0,
      "spare": 0,
      "MSSC": 1,
      "ARC": 1,
      "AIC": 1,
      "B1A": 1,
      "B1B": 5
    },
    "240": {
      "AI": "DLH65A  "
    },
    "250": {
      1: {
        "MBDATA": 54175137758183420,
        "BDS1": 4,
        "BDS2": 0
      }
    },
    "cat": 48,
    "010": {
      "SAC": 25,
      "SIC": 201
    },
    "020": {
      "TYP": 5,
      "SIM": 0,
      "RDP": 0,
      "SPI": 0,
      "RAB": 0,
      "FX": 0
    },
    "040": {
      "RHO": 197.68359375,
      "THETA": 340.13671875
    },
    "070": {
      "V": 0,
      "G": 0,
      "L": 0,
      "spare": 0,
      "MODE3A": "1000"
    },
    "090": {
      "V": 0,
      "G": 0,
      "FL": 330
    }
}


TEST_CAT034 = {
    "120": {
      "HGT": 1214,
      "LAT": 46.50589942932129,
      "LON": 15.5546236038208
    },
    "cat": 34,
    "010": {
      "SAC": 147,
      "SIC": 102
    },
    "000": {
      "MT": 1
    },
    "030": {
      "ToD": 46012.0859375
    },
    "041": {
      "ARS": 6.0078125
    },
    "050": {
      "COM": {
        "NOGO": 0,
        "RDPC": 0,
        "RDPR": 0,
        "OVLRDP": 0,
        "OVLXMT": 0,
        "MSC": 0,
        "TSV": 0,
        "spare": 0
      },
      "PSR": {
        "ANT": 0,
        "CHAB": 1,
        "OVL": 0,
        "MSC": 0,
        "spare": 0
      },
      "MDS": {
        "ANT": 0,
        "CHAB": 1,
        "OVLSUR": 0,
        "MSC": 0,
        "SCF": 0,
        "DLF": 0,
        "OVLSCF": 0,
        "OVLDLF": 0,
        "spare": 0
      }
    }
}

TEST_CAT001 = {
  "141": {
    "TToD": 439.5625
  },
  "cat": 1,
  "010": {
    "SAC": 45,
    "SIC": 168
  },
  "020": {
    "TYP": 0,
    "SIM": 0,
    "SSRPSR": 3,
    "ANT": 0,
    "SPI": 0,
    "RAB": 0,
    "FX": 0
  },
  "040": {
    "RHO": 19.984375,
    "THETA": 52.66845703125
  },
  "070": {
    "V": 0,
    "G": 0,
    "L": 0,
    "spare": 0,
    "MODE3A": "6024"
  },
  "090": {
    "V": 0,
    "G": 0,
    "HGT": 380
  }
}

TEST_CAT048_B = b'0\x000\xfd\xf7\x02\x19\xc95mM\xa0\xc5\xaf\xf1\xe0\x02\x00\x05(<f\x0c\x10\xc26\xd4\x18 \x01\xc0x\x001\xbb\xff\xfc@\r\xeb\x07\xb9X.A\x00 \xf5'

TEST_CAT034_B = b'"\x00\x1a\xed\x10\x93f\x01Y\xde\x0b\x03\x01\x94\x00  \x00\x04\xbe!\x12$\x0b\x0f\xa2'

TEST_CAT001_B = b'\x01\x00\x11\xfa-\xa80\t\xfe%t\x0c\x14\x05\xf0\xdb\xc8'