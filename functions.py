def snap_position(pos:float, unit:float, ofset=0.0, up=False):
    return (pos-ofset)//unit*unit+ofset+unit*up