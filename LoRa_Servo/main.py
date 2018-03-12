from machine import PWM
import utime

pwm = PWM(0, frequency=50)  # use PWM timer 0, with a frequency of 5KHz
# create pwm channel on pin P12 with a duty cycle of 50%
pwm_c = pwm.channel(0, pin='P12', duty_cycle=0.5)
current_angle = 0

def set_angle(new_angle = 0, current_angle = 0):
    degrees = new_angle - current_angle
    if (abs(degrees) >= 360):
        degrees = new_angle + current_angle
    print(degrees)
    if (degrees >= 0):
        print("Forward")
        pwm_c.duty_cycle(0.074) #Clockwise Rotation
        degrees = abs(degrees)
        time_angle = int((float(degrees)/360)*3860)
        utime.sleep_ms(time_angle)
        pwm_c.duty_cycle(0.0) 
    else:
        print("Reverse")
        pwm_c.duty_cycle(0.078) #Anti-Clockwise Rotation
        degrees = abs(degrees)
        time_angle = int((float(degrees)/360)*2540)
        utime.sleep_ms(time_angle)
        pwm_c.duty_cycle(0.0) 
    return(new_angle)

current_angle= set_angle(180,current_angle)
tme.sleep_ms(2000)
current_angle= set_angle(65,current_angle)
tme.sleep_ms(2000)
current_angle= set_angle(70,current_angle)
tme.sleep_ms(2000)
current_angle= set_angle(270,current_angle)
tme.sleep_ms(2000)
current_angle= set_angle(0,current_angle)