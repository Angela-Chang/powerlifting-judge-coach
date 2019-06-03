#torque reference: (not code just ideas)
#http://ffden-2.phys.uaf.edu/211_fall2013.web.dir/Johnson_Ryan/physics-of-the-squat.html
#http://ffden-2.phys.uaf.edu/211_fall2013.web.dir/Johnson_Ryan/torque-in-the-deadlift.html
from math import*
#finds torque about a certain joint
def findTorque(jointPoints, joint, barbell, load=1):
    #returns relative torque unless weight is given
    #barbell: index for joint holding the bar
    #joint: origin for moment arm
    lenMomentArm = abs(jointPoints[joint].x - jointPoints[barbell].x)
    
    dy = abs(jointPoints[joint].y - jointPoints[barbell].y)
    theta = atan(dy/lenMomentArm)
    torque = load*lenMomentArm*sin(theta)
    return torque
    