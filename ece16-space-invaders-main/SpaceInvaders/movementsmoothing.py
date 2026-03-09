import numpy as np
def smoothMovement(ship):
    dir_sum = np.sum(np.array(ship.socketDirections))
    print(dir_sum)
    if dir_sum>0:
        return ship.speed
    elif dir_sum<0:
        return -ship.speed
    elif dir_sum==0:
        return 0