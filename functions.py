from PyQt5.QtGui import QColor


def snap_position(pos:float, unit:float, ofset=0.0, up=False):
    return (pos-ofset)//unit*unit+ofset+unit*up

def display_hour(mins):
    hs = int(mins//12+8)
    mins = int(mins%12)*5
    return f'{hs}:{mins:02d}' 

def shorten_name(name):
    words = name.split()
    return ' '.join([word[0:3] + '.' for word in words])

def luminance(color: QColor):
    def to_linear(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r = to_linear(color.red())
    g = to_linear(color.green())
    b = to_linear(color.blue())

    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(c1: QColor, c2: QColor):
    L1 = luminance(c1)
    L2 = luminance(c2)
    return (max(L1, L2) + 0.05) / (min(L1, L2) + 0.05)