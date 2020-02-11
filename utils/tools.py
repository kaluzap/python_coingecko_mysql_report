import numpy as np

def str_change_percentage(initial, final):
    
    if initial == 0.0:
        return '--.--'
    else:
        value = (final - initial)/initial
    return f'{(100.0*value):.2f}%'


def float_change_percentage(initial, final):
    
    if initial == 0.0:
        return np.nan
    else:
        value = 100.0*(final - initial)/initial
    return round(value, 2)
