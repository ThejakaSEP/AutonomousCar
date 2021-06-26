import RPi.GPIO as GPIO
from time import sleep


m1 = 16
m2 = 18
# m3 = 22

m1a = 31
m2a = 29
    


def car_setup():
    
    GPIO.setmode(GPIO.BOARD)

    # m3a = 19
    
    GPIO.setup(m1,GPIO.OUT)
    GPIO.setup(m2,GPIO.OUT)
    GPIO.output(m1,GPIO.LOW)
    GPIO.output(m2,GPIO.LOW)
    
    GPIO.setup(m1a,GPIO.OUT)
    GPIO.setup(m2a,GPIO.OUT)
    GPIO.output(m1a,GPIO.LOW)
    GPIO.output(m2a,GPIO.LOW)
    print("Setting up")
    sleep(0.5)

def car_forward(sleeptime):
    
    print("Forward")
    
    GPIO.output(m1,GPIO.HIGH)
    GPIO.output(m2,GPIO.LOW)
    
    GPIO.output(m1a,GPIO.HIGH)
    GPIO.output(m2a,GPIO.LOW)
    
    sleep(sleeptime)

def car_backward(sleeptime):
    
    print("Backward")
    
    GPIO.output(m1,GPIO.LOW)
    GPIO.output(m2,GPIO.HIGH)
    
    GPIO.output(m1a,GPIO.LOW)
    GPIO.output(m2a,GPIO.HIGH)
    
    sleep(sleeptime)


def car_pivotleft(sleeptime):
    
    print("Pivot Left")
    
    GPIO.output(m1,GPIO.LOW)
    GPIO.output(m2,GPIO.HIGH)
    
    GPIO.output(m1a,GPIO.HIGH)
    GPIO.output(m2a,GPIO.LOW)
    
    sleep(sleeptime)

def car_pivotright(sleeptime):
    
    print("Pivot Right")
    
    GPIO.output(m1,GPIO.HIGH)
    GPIO.output(m2,GPIO.LOW)
    
    GPIO.output(m1a,GPIO.LOW)
    GPIO.output(m2a,GPIO.HIGH)
    
    sleep(sleeptime)

def car_stop(sleeptime):

    print("Car stopped")
    
    GPIO.output(m1,GPIO.LOW)
    GPIO.output(m2,GPIO.LOW)
    
    GPIO.output(m1a,GPIO.LOW)
    GPIO.output(m2a,GPIO.LOW)
    
    sleep(sleeptime)
    
    
def car_reset():
    
    print('Reset')
    
    GPIO.cleanup()

#car_setup()
#car_forward(0.1)
#car_backward(sleeptime)
#car_pivotleft(0.1)
#car_stop()
#car_reset()