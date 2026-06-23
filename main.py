from machine import Pin, PWM
import time


# ΚΙΝΗΤΗΡΕΣ
IN1 = Pin(0, Pin.OUT); IN2 = Pin(1, Pin.OUT)
IN3 = Pin(2, Pin.OUT); IN4 = Pin(3, Pin.OUT)

enable1 = PWM(Pin(4)); enable2 = PWM(Pin(5))
enable1.freq(1000); enable2.freq(1000)

# ΑΙΣΘΗΤΗΡΕΣ
left_ir   = Pin(10, Pin.IN)
center_ir = Pin(11, Pin.IN)
right_ir  = Pin(12, Pin.IN)

# ΡΥΘΜΙΣΕΙΣ
BASE_SPEED = 50000  # Βασική ταχύτητα

KP = 3000   
KI = 0      
KD = 2000   

# ΚΙΝΗΤΗΡΕΣ
def motors(left_speed, left_fwd, right_speed, right_fwd):
    left_speed  = max(0, min(65535, int(left_speed)))
    right_speed = max(0, min(65535, int(right_speed)))
    enable1.duty_u16(left_speed)
    enable2.duty_u16(right_speed)
    
    IN1.value(1 if left_fwd else 0)
    IN2.value(0 if left_fwd else 1)
    IN3.value(1 if right_fwd else 0)
    IN4.value(0 if right_fwd else 1)


def stop():
    enable1.duty_u16(0); enable2.duty_u16(0)
    IN1.low(); IN2.low(); IN3.low(); IN4.low()

# PID
last_error  = 0
integral    = 0
last_turn   = "none"
lost_count  = 0

# ΕΚΚΙΝΗΣΗ
print("Εκκίνηση σε 3 δευτερόλεπτα...")
time.sleep(3)
print("GO!")

while True:
    L = left_ir.value()    # 1=γραμμή
    C = center_ir.value()
    R = right_ir.value()

    # ΥΠΟΛΟΓΙΣΜΟΣ ΣΦΑΛΜΑΤΟΣ
    # -2      = πολύ αριστερά
    # -1      = λίγο αριστερά
    #  0      = κέντρο
    # +1      = λίγο δεξιά
    # +2      = πολύ δεξιά
    if   L==0 and C==1 and R==0:
        error = 0        # ευθεία
    elif L==1 and C==1 and R==0:
        error = -1       # λίγο αριστερά
    elif L==1 and C==0 and R==0:
        error = -2       # πολύ αριστερά
    elif L==0 and C==1 and R==1:
        error = 1        # λίγο δεξιά
    elif L==0 and C==0 and R==1:
        error = 2        # πολύ δεξιά
    elif L==1 and C==1 and R==1:
        error = 0        # διασταύρωση → ευθεία
    else:
        lost_count += 1
        if lost_count > 50:
            stop()
        elif last_turn == "left":
            motors(40000, False, 40000, True)
        elif last_turn == "right":
            motors(40000, True, 40000, False)
        else:
            stop()
        time.sleep_ms(8)
        continue

    lost_count = 0

    # PID ΥΠΟΛΟΓΙΣΜΟΣ
    integral  = integral + error          # I
    derivative = error - last_error       # D
    last_error = error

    correction = int(KP * error + KI * integral + KD * derivative)

    left_speed  = BASE_SPEED + correction
    right_speed = BASE_SPEED - correction

    if error < 0:
        last_turn = "left"
    elif error > 0:
        last_turn = "right"

    motors(left_speed, True, right_speed, True)

    time.sleep_ms(8)