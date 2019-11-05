from gpiozero import MotionSensor

pir = MotionSensor(27)

i=0
while True:
    pir.wait_for_motion()
    print("{} You moved".format(i))
    #pir.wait_for_no_motion()
    i += 1
