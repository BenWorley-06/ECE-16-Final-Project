import numpy as np

H_RANGE = 50
V_RANGE = 300
CENTER_THRESHOLD = 8

def bullet_detection(ship,bullets):
    total_force = 0.0
    for b in bullets:
        dx = ship.rect.centerx - b.rect.centerx
        dy = ship.rect.centery - b.rect.centery

        if dy <= 0:     #Bullet is behind player
            continue

        if abs(dx) > H_RANGE or dy > V_RANGE:   #Bullet out of range
            continue

        h_weight = 1 - (abs(dx) / H_RANGE)
        v_weight = 1 - (dy / V_RANGE)

        if abs(dx) < CENTER_THRESHOLD:  #Bullet in center
            direction = ship.last_dir
        else:
            direction = np.sign(dx)
            ship.last_dir = direction

        total_force += direction * h_weight * v_weight
    return total_force

def move_assist(ship, bullets):
    total_force = bullet_detection(ship,bullets)

    move = total_force * ship.speed
    move = max(-ship.speed, min(ship.speed, move))

    if abs(move) < 0.2: #Ignore micro movements
        return 0

    return move