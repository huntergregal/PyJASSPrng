class JASSPrng:
    '''
    Warcraft 3 JASS Pseudorandom number generator
    Mimics the JASS native functions: SetRandomSeed, GetRandomInt
    '''

    # Extracted from game.dll v1.26.0.6401
    CONSTANTS_BYTES = b'\x8e\x14\x27\x99\xfd\xaa\xc7\x08\xd5\xe6\x3e\x1f\xf6' \
        b'\xbb\x55\xda\x75\xa0\x4a\x6a\xe8\xbd\x97\xff\xde\x9b\xbc\x9f\x81' \
        b'\x8a\xa1\x46\x6e\x0b\xe3\x63\x76\x7a\x6c\x5d\x88\xd3\x69\xca\xc3' \
        b'\x47\xb9\x25\x83\xab\xa2\x3f\xa6\x41\x7c\xba\xe5\xac\x95\x01\x7e' \
        b'\xcf\x09\xc1\xd9\x62\x70\x71\x8d\xdb\x05\x02\x24\x87\xef\x54\xc6' \
        b'\xd4\x37\x30\xd0\x1b\xcb\x7b\xb8\xe4\xd8\xec\x49\xce\xad\xdc\x13' \
        b'\xa9\x94\xc4\x8f\x39\xae\x0d\x18\x52\xdd\x0e\x78\xfa\xf5\x85\x58' \
        b'\xd2\xaf\x6d\xa4\xb2\x53\x3b\x51\xa5\x50\xbe\xfc\x2d\xf4\x11\x48' \
        b'\x98\x16\xf1\x86\xdf\x3d\x66\x5e\x44\x2e\x2f\x36\x07\x6b\x17\x8b' \
        b'\x29\x4c\xb6\xe2\x89\x5f\xe7\xcd\xa7\x21\xe1\x4d\xc9\x65\xed\xfe' \
        b'\xee\x9c\x23\x33\x7d\xb7\x04\x9e\x9a\x2a\x40\xb3\x10\x5b\xf3\x82' \
        b'\x77\x1c\x92\x20\x4e\x1e\x57\x22\x72\x06\x8c\x67\x2c\x73\xfb\x59' \
        b'\xc2\x0a\xbf\x79\x5c\xf9\x0c\x28\x1a\x12\x68\x74\x34\x19\x42\xb1' \
        b'\xc0\x84\xf8\x38\xf0\x15\x9d\x60\xf2\x3a\x6f\xb4\x90\xeb\x91\x1d' \
        b'\x7f\x35\x61\x5a\x32\x03\x56\xa3\xc5\x2b\x93\x80\x0f\x4b\x43\xf7' \
        b'\xa8\xe0\x3c\x96\xd1\x64\x26\xd7\x45\xcc\x4f\xc8\xb0\xe9\xb5\x00' \
        b'\xd6\x31\xea\x68\x75\x6e\x74\x65\x72\x20\x67\x72\x65\x67\x61\x6c'

    def __init__(self, seed = None) -> None:
        self.seed_bits = 0
        self.current = 0
        if seed is not None:
            self.SetRandomSeed(seed)

    def SetRandomSeed(self, seed: int) -> None:
        self._set_seed(seed)
        _ = self.Step()

    def _set_seed(self, seed: int) -> None:
        # seed_bitfield format
        # shifts and sets 6bit fields at bit offsets: 2, 10, 18, 26 */
        #   [31..26]  6b:  ((seed / 47) * 17 + seed)  & 0x3F
        #   [25..24]  2b:  0 (gaps)
        #   [23..18]  6b:  seed % 53
        #   [17..16]  2b:  0
        #   [15..10]  6b:  seed % 59
        #   [9..8]    2b:  0
        #   [7..2]    6b:  seed % 61
        #   [1..0]    2b:  0
        #
        self.seed_bits = (seed % 0x3d) << 2
        self.seed_bits |= (seed % 0x3b) << 10
        self.seed_bits |= (seed % 0x35) << 18
        self.seed_bits |= ((seed // 0x2f) * 0x11 + seed) << 26
        self.current = seed

    @staticmethod
    def _rotl32(x: int, n: int) -> int:
        x &= 0xFFFFFFFF
        return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF

    def _const_at(self, idx: int) -> int:
        return int.from_bytes(self.CONSTANTS_BYTES[idx:idx+4], 'little', signed=False)

    def Step(self) -> int:
        s = self.seed_bits & 0xFFFFFFFF

        b3 = (s >> 24) & 0xFF
        b2 = (s >> 16) & 0xFF
        b1 = (s >> 8)  & 0xFF
        b0 = s & 0xFF

        i0 = b3 - 4
        if i0 < 0:
            i0 = b3 + 0xB8

        i1 = b2 - 0x0C
        if i1 < 0:
            i1 = b2 + 200

        i2 = b1 - 0x18
        if i2 < 0:
            i2 = b1 + 0xD4

        i3 = b0 - 0x1C
        if i3 < 0:
            i3 = b0 + 0xD8

        c2 = self._const_at(i2)
        mix = (
            self._rotl32(self._const_at(i2), 3) ^
            self._rotl32(self._const_at(i1), 2) ^
            (self._const_at(i3)) ^                  # (no rotation)
            self._rotl32(self._const_at(i0), 1)
        ) & 0xFFFFFFFF

        new_val = (self.current + mix) & 0xFFFFFFFF

        # Advance seed bytes
        self.seed_bits = (((i0 & 0xFF) << 24) |
                          ((i1 & 0xFF) << 16) |
                          ((i2 & 0xFF) << 8)  |
                          (i3 & 0xFF)) & 0xFFFFFFFF

        self.current = new_val
        return new_val

    def GetRandomInt(self, min_val: int, max_val: int) -> int:
        if min_val == max_val:
            return min_val
    
        # range = |max - min|
        if max_val < min_val:
            rng = min_val - max_val
        else:
            rng = max_val - min_val
    
        rnd = self.Step()
        t = (rnd * (rng + 1)) >> 32
    
        return min_val + t

if __name__ == '__main__':
    print('=== Wc3 JASS Test ===')
    print('function test takes nothing returns nothing')
    print('    call SetRandomSeed(12345)')
    print('    call DisplayTimedTextToPlayer(Player(0), 0, 0, 60, "r1=" + I2S(GetRandomInt(0, 1000000)))')
    print('    call DisplayTimedTextToPlayer(Player(0), 0, 0, 60, "r2=" + I2S(GetRandomInt(0, 1000000)))')
    print('    call DisplayTimedTextToPlayer(Player(0), 0, 0, 60, "r3=" + I2S(GetRandomInt(0, 1000000)))')
    print('endfunction')
    print('==Wc3 Output==')
    print('r1=189832')
    print('r2=638801')
    print('r3=925099')

    print('=== JASSPrng Python Test ===')
    rng = JASSPrng()
    rng.SetRandomSeed(12345)
    for i in range (1, 4):
        print(f'r{i}={rng.GetRandomInt(0, 1000000)}')
