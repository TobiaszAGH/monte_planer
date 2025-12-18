def snap_position(pos:float, unit:float, ofset=0.0, up=False):
    return (pos-ofset)//unit*unit+ofset+unit*up



def display_hour(mins):
    hs = int(mins//12+8)
    mins = int(mins%12)*5
    return f'{hs}:{mins:02d}' 

def shorten_name(name):
    words = name.split()
    return ' '.join([word[0:3] + '.' for word in words])
