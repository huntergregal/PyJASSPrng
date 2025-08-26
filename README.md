# PyJASSPrng
Python implementation of Warcraft 3's JASS Random number generator

# Quick Usage

```
from pyjassprng import JASSPrng
seed = 12345
rng = JASSPrng()
rng.SetRandomSeed(seed)
#rng = JASSPrng(seed) # optional init with seed
for i in range(10):
    print(rng.GetRandomInt(0,10000))
```
# Sample Test
```
python3 __init__.py
=== Wc3 JASS Test ===
function test takes nothing returns nothing
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
endfunction
==Wc3 Output==
r1=189832
r2=638801
r3=925099
r4=2.566
r4W=4.405078400
r5=1.568
r5W=1.275389408
r6=-0.997
r6W=0.035798548
=== JASSPrng Python Test ===
=ints=
r1=189832
r2=638801
r3=925099
=floats=
r4=2.566
r4W=4.4050788879
r5=1.568
r5W=1.2753894329
r6=-0.997
r6W=0.0357985497
```

Note: very tiny loss in GetRandomReal output precision. (25-ULP difference)
