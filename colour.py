import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/Users/kcarikas/AppData/Roaming/Python/Python310/site-packages')

import colour

from colour import Color
red = Color("red")
colors = list(red.range_to(Color("green"),10))
print (colors)
