import bpy

def IF(statement,true,false):
    """ Returns true if statement is true Returns false if statement is false:
        statement - conditional statement
        true - value to return if statement is True
        false - value to return if statement is False
    """
    if statement == True:
        return true
    else:
        return false

def OR(*vars):
    """ Returns True if ONE parameter is true
    """
    for var in vars:
        if var:
            return True
    return False

def AND(*vars):
    """ Returns True if ALL parameters are true
    """
    for var in vars:
        if not var:
            return False
    return True

def INCH(value):
    """ Converts value to meters: expecing value in inches
    """
    return value * .0254

def MILLIMETER(value):
    """ Converts value to meters: expecting value in millimeter
    """
    return value * .001

def LIMIT(val,val_min,val_max):
    """ Returns par1 if value is between min and max else
        the minimum or maximum value value will be returned
    """
    if val>val_max:
        return val_max
    elif val<val_min:
        return val_min
    else:
        return val
    
def PERCENTAGE(value,min,max):
    """ Returns Percentage amount based on the min and max values
    """
    return (value - min)/(max - min)    