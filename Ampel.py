from time import sleep
from gpiozero import LED
from gpiozero import MotionSensor
from signal import pause

LED_rot_1  = LED(21)
LED_gelb_1 = LED(20)
LED_grün_1 = LED(16)

LED_rot_2  = LED(23)
LED_gelb_2 = LED(24)
LED_grün_2 = LED(25)

LED_rot_3  = LED(22)
LED_gelb_3 =  LED(27)
LED_grün_3 = LED(17)

LED_rot_4  = LED(26)
LED_gelb_4 = LED(19)
LED_grün_4 = LED(13)

# Here you can find the layout of each 'traffic light' on the breadboard
#        
#     LED_grün_1                                         LED_grün_4
#     LED_gelb_1                                         LED_gelb_4 
#     LED_rot_1                                          LED_rot_4
#
#
# 
#     LED_rot_3                                          LED_rot_2
#     LED_gelb_3                                         LED_gelb_2        
#     LED_grün_3                                         LED_grün_2
#
#


while True:
    LED_grün_1.off()
    LED_gelb_1.on()                                     
    LED_rot_1.on()
    LED_rot_2.on()
    LED_grün_2.on()
    LED_gelb_2.off()
    LED_rot_3.on()                                     
    LED_gelb_3.on()                                             
    LED_grün_3.on()                                    
    LED_grün_4.off()
    LED_gelb_4.on()
    LED_rot_4.on()
pir = MotionSensor(18)

def motion_function():
    print("Motion Detected")

def no_motion_function():
    print("Motion stopped")

pir.when_motion = motion_function
pir.when_no_motion = no_motion_function

pause()