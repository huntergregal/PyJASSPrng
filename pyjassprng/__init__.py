import ctypes as C
import struct

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

    def GetRandomReal(self, min_val: float, max_val: float) -> float:
        #Exact bitwise match of JASS GetRandomReal.

        #The f32 helper functions are needed (as opposed to say, using numpy)
        #because the JASS natives differ from IEEE754 in these ways:
        #    * subnormals treated as 0 on input and output
        #    * no rounding -- truncates after alginment
        #    *no NaN/Inf handling

        #s/o GPT 5 for explaining these operations. Was not quite sure what they
        #were doing with the floats. Now it tracks. These are architecture
        #agnostic variants of float 32 sub/add/mult w/ some... quirks.


        def u32(x): return C.c_uint32(x).value
        def s32(x): return C.c_int32(x).value
        def float_to_u32(f): return struct.unpack('<I', struct.pack('<f', f))[0]
        def u32_to_float(u): return struct.unpack('<f', struct.pack('<I', u & 0xffffffff))[0]

        def _clz32_c(x: int) -> int:
            x = u32(x)
            if x == 0: return 32
            i = 31
            while (x >> i) == 0:
                i -= 1
            return 31 - i  # number of leading zeros in 32-bit lane
        
        def _signed_sig_x2(u: int) -> int:
            # ((mant|0x800000)*2 ^ (int)u>>31) - ((int)u>>31)  in 32-bit lanes
            u  = u32(u)
            m2 = u32((u & 0x7fffff) | 0x800000)
            m2 = u32(m2 * 2)
            s  = s32(u) >> 31                  # 0 or -1
            v  = u32(m2 ^ u32(s))             # xor in u32
            return s32(s32(v) - s)            # signed subtract
        
        def f32_add(a_bits: int, b_bits: int) -> int:
            a = u32(a_bits); b = u32(b_bits)
        
            exp_a = a & 0x7f800000
            if exp_a == 0:
                return b
            exp_b = b & 0x7f800000
            if exp_b == 0:
                return a
        
            sig_a = _signed_sig_x2(a)
            sig_b = _signed_sig_x2(b)
        
            diff = u32(exp_b - exp_a)
            if s32(diff) < 1:
                if s32(diff) < -0x0B7FFFFF:
                    return a
                sh = ((u32(exp_a - exp_b) >> 23) & 0x1f)
                sig_b = s32(sig_b >> sh)       # arithmetic shift
                exp_big = exp_a
            else:
                if s32(diff) > 0x0B7FFFFF:
                    return b
                sh = ((diff >> 23) & 0x1f)
                sig_a = s32(sig_a >> sh)
                exp_big = exp_b
        
            sum_signed = s32(s32(sig_a) + s32(sig_b))
            if sum_signed == 0:
                return 0x00000000
        
            sign_bit = 0x80000000 if sum_signed < 0 else 0
            mag = u32(-sum_signed if sum_signed < 0 else sum_signed)
        
            clz = _clz32_c(mag)
            # Branchy renorm, exactly like the decompile: shift so leading 1 ends at bit 23,
            # exponent delta is (7 - clz) << 23
            shift_amt = -clz + 8
            if shift_amt < 0:
                mag = u32((mag << u32(-shift_amt)) & 0xffffffff)
            else:
                # use arithmetic-looking shift on a positive value to mirror C’s >> on unsigned promoted to int
                mag = u32(s32(mag) >> (shift_amt & 0x1f))
        
            out = u32((((-clz + 7) * 0x800000) + exp_big) |
                       (mag & 0x7fffff) |
                       sign_bit)
            return out
        
        def f32_sub(op1_bits: int, op2_bits: int) -> int:
            return f32_add(op1_bits, u32(op2_bits) ^ 0x80000000)

        def f32_mult(a_bits: int, b_bits: int) -> int:
            a = a_bits & 0xffffffff
            b = b_bits & 0xffffffff
        
            sign = (a ^ b) & 0x80000000
            Ea = a & 0x7f800000
            Eb = b & 0x7f800000
            Ma = a & 0x007fffff
            Mb = b & 0x007fffff
        
            # WC3 semantics: treat subnormals/zeros as 0 (result 0)
            if Ea == 0 or Eb == 0:
                print("=== f32_mult debug (zero/subnormal) ===")
                return 0x00000000
        
            # 24-bit significands with hidden 1
            Ma1 = (1 << 23) | Ma
            Mb1 = (1 << 23) | Mb
        
            # 24x24 -> 48-bit product
            P = (Ma1 * Mb1) & 0xffffffffffffffff  # keep 64b for clarity
        
            # topbit is the 48-bit product's bit 47 (>= 2.0 requires a renorm step)
            topbit = (P >> 47) & 1
        
            # Truncation (no rounding): shift 23 or 24 depending on topbit
            mant = (P >> (23 + topbit)) & 0x007fffff
        
            # Exponent combine: Ea + Eb - bias
            # (0xC0800000 is -0x3F800000 modulo 2^32)
            E = (Ea + Eb + 0xC0800000) & 0xffffffff
        
            # If topbit==1, renormalize by bumping exponent by 1 ulp of exponent field
            if topbit:
                E = (E + 0x00800000) & 0xffffffff
        
            # Underflow to zero if exponent would be subnormal (WC3 collapses subnormals)
            if ((E - 0x00800000) & 0xffffffff) >> 31:  # unsigned test E < 0x00800000
                out = 0x00000000
            else:
                out = (sign | (E & 0x7f800000) | mant) & 0xffffffff
        
            return out

        def s32_to_f32(param_2: int) -> int:
            param_2 &= 0xffffffff
            if param_2 == 0:
                return 0x00000000
            sign = param_2 & 0x80000000
            if s32(param_2) < 0:
                param_2 = (-param_2) & 0xffffffff
            iVar1 = _clz32_c(param_2)
            shift_amt = iVar1 - 8
            if shift_amt < 0:
                uVar4 = s32(param_2) >> ((-shift_amt) & 0x1f)
            else:
                uVar4 = (param_2 << (shift_amt & 0x1f)) & 0xffffffff
            return (((0x9e - iVar1) * 0x800000) | (uVar4 & 0x7fffff) | sign) & 0xffffffff

        # Sanity Check for R2SW debug
        def f32_from_bits(u: int) -> float:
                return struct.unpack('<f', struct.pack('<I', u & 0xffffffff))[0]
        def f32_to_bits(x: float) -> int:
            return struct.unpack('<I', struct.pack('<f', x))[0] & 0xffffffff

        def r2sw_trunc_f32_bits(val_bits: int, width: int, precision: int) -> str:
            """Emulate JASS R2SW: truncate to 'precision' decimals (no rounding), pad zeros."""
            x = f32_from_bits(val_bits)
            neg = x < 0.0
            ax = -x if neg else x
        
            # integer part (truncate toward zero)
            i_part = int(ax)
            frac_bits = f32_sub(f32_to_bits(ax), f32_to_bits(float(i_part)))  # ax - i_part (f32)
            s = "-" + str(i_part) if neg and (i_part != 0 or f32_from_bits(frac_bits) != 0.0) else str(i_part)
        
            # fractional digits by repeated *10 (all in f32) with truncation each step
            if precision > 0:
                s += "."
                ten_bits = 0x41200000  # 10.0f
                for _ in range(precision):
                    frac_bits = f32_mult(frac_bits, ten_bits)           # frac *= 10
                    digit = int(f32_from_bits(frac_bits))               # trunc toward 0
                    s += str(digit)
                    # frac -= digit
                    digit_bits = f32_to_bits(float(digit))
                    frac_bits = f32_sub(frac_bits, digit_bits)
        
            # left-pad to width if needed
            if width > 0 and len(s) < width:
                s = " " * (width - len(s)) + s
            return s

        # ------------------------
        # 1) clamp = min - max
        # ------------------------
        u_min_val = float_to_u32(min_val)
        u_max_val = float_to_u32(max_val)
        width_bits = f32_sub(u_min_val, u_max_val)

        threshold = u32_to_float(0x3456bf95)
        if abs(u32_to_float(width_bits)) < threshold:
            return u32_to_float(u_min_val)
   
        # ------------------------
        # 2) width = |max - min|, stored via the same sub_float32 calls
        #    (note: final add always uses ORIGINAL min pointer)
        # ------------------------
        if min_val <= max_val:
            width_bits = f32_sub(u_max_val, u_min_val)  # max - min (positive)
        else:
            width_bits = f32_sub(u_min_val, u_max_val)  # min - max (positive)
    
        # ------------------------
        # 3) u in [0,1): use LOW 23 bits of rnd
        # ------------------------
        rnd = self.Step() & 0xffffffff
        one_to_two_bits = ((rnd & 0x7fffff) | 0x3f800000) & 0xffffffff
        g_rand_add_bits = s32_to_f32(0xffffffff)             # -1.0f => 0xbf800000
        u_bits = f32_add(one_to_two_bits, g_rand_add_bits)   # (1.xxx) + (-1.0) => [0,1)


        # ------------------------
        # 4) result = min + width * u   (all via custom ops)
        # ------------------------
        scaled_bits = f32_mult(width_bits, u_bits)
        out_bits = f32_add(u_min_val, scaled_bits)  # add to ORIGINAL min pointer

        return u32_to_float(out_bits)


if __name__ == '__main__':
    print('=== Wc3 JASS Test ===')
    print('''function test takes nothing returns nothing
    call SetRandomSeed(12345)
    call DisplayTimedTextToPlayer(Player(0), 0, 0, 60, "r1=" + I2S(GetRandomInt(0, 1000000)))
    call DisplayTimedTextToPlayer(Player(0), 0, 0, 60, "r2=" + I2S(GetRandomInt(0, 1000000)))
    call DisplayTimedTextToPlayer(Player(0), 0, 0, 60, "r3=" + I2S(GetRandomInt(0, 1000000)))

    call DisplayTimedTextToPlayer(Player(0), 0, 0, 60, "r4=" + R2S(GetRandomReal(2.245, 6.532)))
    call DisplayTimedTextToPlayer(Player(0), 0, 0, 60, "r4W=" + R2SW(GetRandomReal(2.245, 6.532), 8, 9))
    call DisplayTimedTextToPlayer(Player(0), 0, 0, 60, "r5=" + R2S(GetRandomReal(1.1, 2.5)))
    call DisplayTimedTextToPlayer(Player(0), 0, 0, 60, "r5W=" + R2SW(GetRandomReal(1.1, 2.5), 8, 9))
    call DisplayTimedTextToPlayer(Player(0), 0, 0, 60, "r6=" + R2S(GetRandomReal(-2.1, 3.14)))
    call DisplayTimedTextToPlayer(Player(0), 0, 0, 60, "r6W=" + R2SW(GetRandomReal(-2.1, 3.14), 8, 9))
endfunction''')
    print('==Wc3 Output==')
    print('r1=189832')
    print('r2=638801')
    print('r3=925099')
    print('r4=2.566')

    print('r4W=4.405078400')
    print('r5=1.568')
    print('r5W=1.275389408')
    print('r6=-0.997')
    print('r6W=0.035798548')

    print('=== JASSPrng Python Test ===')
    rng = JASSPrng()
    rng.SetRandomSeed(12345)
    print('=ints=')
    for i in range (1, 4):
        print(f'r{i}={rng.GetRandomInt(0, 1000000)}')

    print('=floats=')
    reals = [(2.245, 6.532), (1.1, 2.5), (-2.1, 3.14)]
    for i in range(len(reals)):
        x = rng.GetRandomReal(reals[i][0], reals[i][1])
        print(f'r{i+4}={x:4.3f}')
        x = rng.GetRandomReal(reals[i][0], reals[i][1])
        print(f'r{i+4}W={x:4.10f}') # precision ever so slightly off due to python
