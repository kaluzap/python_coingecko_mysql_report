

def str_change_percentage(initial, final):
    
    if initial == 0.0:
        return '--.--'
    else:
        value = (final - initial)/initial
    return f'{(100.0*value):.2f}%'
