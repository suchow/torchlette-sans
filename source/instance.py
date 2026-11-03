"""Write a static instance of a variable font.

    python instance.py VARIABLE.ttf WGHT OUT.ttf

Torchlette Sans starts from Mulish at wght 324, a little lighter than Mulish Light.
"""
import sys
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

src, wght, dst = sys.argv[1], float(sys.argv[2]), sys.argv[3]
font = instantiateVariableFont(TTFont(src), {'wght': wght})
font['head'].modified = font['head'].created   # no build-time timestamp
font.recalcTimestamp = False
font.save(dst)
print('wrote', dst)
