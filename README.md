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
