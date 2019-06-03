import pygame
import time
from pykinect2 import PyKinectV2, PyKinectRuntime
from pykinect2.PyKinectV2 import *
from gradients import *
from fT import*
red = (237, 41, 57)
orange = (249, 129, 42)
yellow = (250, 218, 94)
#initializes, finds, and draws the lifter

class Athlete (object):
    def __init__(self, joints, jointPoints, surface, index, reps=0):
        self.jointPoints = jointPoints
        self.joints = joints
        self.surface = surface
        self.index = index
        self.fullROM = False
        
        self.lockOutJoints = set()
        self.lockOutError = 4
        self.pixelError = 20
        
        self.passedOut = False # :p
        self.oldJointPoints = None
        self.reps = reps
        self.torqueLst = []
        self.jointMovement = []
        
    def analyzeForm(self):
        self.jointMovement.append(self.jointPoints)
        
        if isinstance(self, Squatter):
            hipL = 12
            kneeL = 13
            hipR = 16
            kneeR = 17
            barbell = 20 #spine shoulder
            kneeTorque = (findTorque(self.jointPoints, kneeL, barbell) + findTorque(self.jointPoints, kneeR, barbell))/2
            hipTorque = (findTorque(self.jointPoints, hipL, barbell) + findTorque(self.jointPoints, hipR, barbell))/2
            self.torqueLst.append((kneeTorque, hipTorque))
            
            
        elif isinstance(self, Bencher):
            shoulderL = 4
            elbowL = 5
            barbellL = 6 #wristL
            shoulderR = 8
            elbowR = 9
            barbellR = 10 #wristR
            elbowTorque = (findTorque(self.jointPoints, elbowL, barbellL) + findTorque(self.jointPoints, elbowR, barbellR))/2
            shoulderTorque = kneeTorque = (findTorque(self.jointPoints, shoulderL, barbellL) + findTorque(self.jointPoints, shoulderR, barbellR))/2
            self.torqueLst.append((elbowTorque, shoulderTorque))
            
            
        elif isinstance(self, Deadlifter):
            midBack = 1
            
            hipL = 12
            kneeL = 13
            hipR = 16
            kneeR = 17
            barbellL = 6 #wrist
            barbellR = 10
            kneeTorque = (findTorque(self.jointPoints, kneeL, barbellL) + findTorque(self.jointPoints, kneeR, barbellR))/2
            hipTorque = (findTorque(self.jointPoints, hipL, barbellL) + findTorque(self.jointPoints, hipR, barbellR))/2
            backTorque = findTorque(self.jointPoints, midBack, barbellL)

            
            self.torqueLst.append((kneeTorque, hipTorque, backTorque))
        
    def rangeOfMotion(self, joint1L, joint2L, joint1R, joint2R):
        #makes sure joint1 goes to or below joint2
        if not self.fullROM:
            if isinstance(self, Bencher):
                if ((self.jointPoints[joint1L].y - self.jointPoints[joint2L].y)<20 or (self.jointPoints[joint1R].y - self.jointPoints[joint2R].y)<20) and self.isSupine():
                    self.start = time.time()
                    self.fullROM = True
            
            else:
                if self.jointPoints[joint1L].y >= self.jointPoints[joint2L].y or self.jointPoints[joint1R].y >= self.jointPoints[joint2R].y:
                    self.start = time.time()
                    self.fullROM = True
                
    def isSupine(self):
        error = 20
        head = 3
        head = self.jointPoints[head].y 
        butt = 16
        butt = self.jointPoints[butt].y 
        hip1 = 12
        hip1 = self.jointPoints[hip1].y 
        hip2 = 0
        hip2 = self.jointPoints[hip2].y 
        return abs(head-butt) < error or abs(head-hip1)<error or abs(head-hip2)<error
        
            
    def lockOut(self, joint1, joint2, joint3):
        #basically makes sure 2 limbs are in a straight line
        #s: hip, knee, ankle --> femur and shin
        #b: shoulder, elbow, wrist --> humerus and ulna
        #d: (knee, hip, shoulder --> femur and spine) and (hip, knee, ankle --> femur and shin)
        minSlope = 8
    
        limb1 = (self.jointPoints[joint1].y-self.jointPoints[joint2].y)/(self.jointPoints[joint1].x-self.jointPoints[joint2].x)
  
        limb2 = (self.jointPoints[joint2].y-self.jointPoints[joint3].y)/(self.jointPoints[joint2].x-self.jointPoints[joint3].x)

        straightened =( abs(limb1)-abs(limb2) ) < self.lockOutError
        upright = (abs(limb1)>minSlope and abs(limb2)>minSlope)
        linedUp = abs(self.jointPoints[joint1].x-self.jointPoints[joint2].x) < self.pixelError and abs(self.jointPoints[joint2].x-self.jointPoints[joint3].x) < self.pixelError

        return linedUp or (upright and straightened)
    
    
    
    #this is from the bodyGame demo on github, I've changed it a bit
    def drawJointDot(self, color, joint0, jointsOfInterest):
    
        joint0State = self.joints[joint0].TrackingState

        # not tracked
        if (joint0State == PyKinectV2.TrackingState_NotTracked) or (joint0State == PyKinectV2.TrackingState_Inferred):
            return

        # tracked
  
        pos = (int(self.jointPoints[joint0].x), int(self.jointPoints[joint0].y))

        if joint0 in jointsOfInterest:
            
            pygame.draw.circle(self.surface, color, pos, 20)
        else: 
            pygame.draw.circle(self.surface, color, pos, 5)
            
    
    def draw(self,jointsOfInterest):
        #joints = body.joints
        #jointPoints : joints to colourspace
        #loop draws each joint
        x = 0
        color = pygame.color.THECOLORS["violet"]
        for i in range (25):
            self.drawJointDot(color, i, jointsOfInterest)

    @staticmethod
    def findAthlete(bodies, kinect, surface): #finds athlete. returns jointPoints as pixel values
        trackedBodies = []
        bodiesLst = []
        for body in bodies.bodies:
            bodiesLst.append(body)
            if body.is_tracked:
                trackedBodies.append(body)
 
        if len(trackedBodies)>0:
            if len(trackedBodies) == 1:#deadlift
            
                lifterIndex = bodiesLst.index(trackedBodies[0])
                jointPoints = kinect.body_joints_to_color_space(trackedBodies[0].joints)
                lifter = Deadlifter(trackedBodies[0].joints, jointPoints, surface, lifterIndex)
                lockOutJointsLeft = (4,12,13,14)
                lockOutJointsRight = (8,16,17,18)
                lifter.lockOutJoints.add(lockOutJointsLeft)
                lifter.lockOutJoints.add(lockOutJointsRight)
                
                return lifter
            else:
                return None
                pixelError = 80
                for body in trackedBodies: #checks if anyone is lying down (bench)
                    jointPoints = kinect.body_joints_to_color_space(body.joints)

       #               ###head=3 , spineBase =0
                    if abs(jointPoints[3].y - jointPoints[0].y)<= pixelError: #someone is lying down
                        lifterIndex = bodiesLst.index(body)
                        lifter = Bencher(body.joints, jointPoints, surface, lifterIndex)
                   
                        lockOutJointsLeft = (4,5,6) #shoulder, elbow, wrist
                        lockOutJointsRight = (8,9,10) #shoulder, elbow, wrist
                        self.lockOutJoints.add(lockOutJointsLeft)
                        self.lockOutJoints.add(lockOutJointsRight)

       #                   .
                
                directions = {'left': 0, 'right': 0}
                for body in trackedBodies: #assuming squatting
                  
                    lHip = 12 
                  
                    zL = int(body.joints[lHip].Position.z) 
                    
                    rHip = 16
           
                    zR = int(body.joints[rHip].Position.z)
               
                    if zR <= zL: 
                        #right side closer --> facing the max width?
                        directions['left']+=1
                    elif zR > zL:
                        #left side closer -- > facing min width?
                        directions['right']+=1
                    
                    #facing left: find hip with smallest xval
                    #facing right: find person with largest xval
                    
                #exited for loop
                if directions['left'] > directions ['right']:
                    front = surface.get_width()
                    
                elif directions['right'] > directions ['left']:
                    front = 0
         
                    
                lifterIndex = Athlete.findSquatter(kinect, front, trackedBodies, bodiesLst)
                body = bodies.bodies[lifterIndex]
                jointPoints = kinect.body_joints_to_color_space(body.joints)
                lifter = Squatter(body.joints, jointPoints, surface, lifterIndex)
                return lifter 
                
    @staticmethod            
    def findSquatter(kinect, front, trackedBodies, bodiesLst):
        #returns index of squatter
        possibleAthlete = []
        leastDistance = -1000
        head = 3
        for body in trackedBodies:
            jointPoints = kinect.body_joints_to_color_space(body.joints)
            xCoor = jointPoints[head].x
            distance = abs(front - xCoor)
            if distance < leastDistance:
                possibleAthlete = bodiesLst.index(body)
                
        return possibleAthlete

   
   
class Squatter(Athlete):
    
    def draw(self):
        #draws the person
        squatJoints = {12,13,14,16,17,18}#hip left, knee left, ankle left, hip right, knee right, ankle right
        super().draw(squatJoints)
        #draw stress skelly
        #joints of interest: stress over femur and shin
        kneeT = self.torqueLst[-1][0]
        hipT = self.torqueLst[-1][1]
        
        rightHip = self.jointPoints[16].x, self.jointPoints[16].y
        rightKnee = self.jointPoints[17].x, self.jointPoints[17].y
        rightAnkle = self.jointPoints[18].x, self.jointPoints[18].y
        
        
        leftHip = self.jointPoints[12].x, self.jointPoints[12].y
        leftKnee = self.jointPoints[13].x, self.jointPoints[13].y
        leftAnkle = self.jointPoints[14].x, self.jointPoints[14].y
     
        if kneeT >= hipT:
            #red knee, yellow hip, yellow ankles
            drawGradient(rightHip, rightKnee, yellow, red, self.surface)
            drawGradient(rightKnee, rightAnkle, red, yellow, self.surface)
            drawGradient(leftHip, leftKnee, yellow, red, self.surface)
            drawGradient(leftKnee, leftAnkle, red, yellow, self.surface)
 
        elif hipT > kneeT:
            #red hip, orange knee, yellow ankles
            drawGradient(rightHip, rightKnee, red, orange, self.surface)
            drawGradient(rightKnee, rightAnkle, orange, yellow, self.surface)
            drawGradient(leftHip, leftKnee, red, orange, self.surface)
            drawGradient(leftKnee, leftAnkle, orange, yellow, self.surface)
        
    
    def ROM(self):
        kneeL = 13
        hipL = 12
        kneeR = 17
        hipR = 16
        super().rangeOfMotion(hipL,kneeL,hipR,kneeR)
        
    def lockOut(self):
        hipL = 12
        kneeL = 13
        hipR = 16
        kneeR = 17
        
        ankleL = 14
        ankleR = 18
        
        self.lockOutError = .5
        return super().lockOut(hipL, kneeL, ankleL) or super().lockOut(hipR, kneeR, ankleR)
        

class Bencher(Athlete):
    def draw(self):
        #draws the person
        benchJoints = {0,3,4,5,6,8,9,10}
        #tailbone, head, shoulderL, elbowL, wristL, shoulderR, elbowR, wristR
        super().draw(benchJoints)
        
        elbowT = self.torqueLst[-1][0]
        shoulderT = self.torqueLst[-1][1]
        
        rightShoulder = self.jointPoints[8].x, self.jointPoints[8].y
        rightElbow = self.jointPoints[9].x, self.jointPoints[9].y
        rightWrist = self.jointPoints[10].x, self.jointPoints[10].y
        
        
        leftShoulder = self.jointPoints[4].x, self.jointPoints[4].y
        leftElbow = self.jointPoints[5].x, self.jointPoints[5].y
        leftWrist = self.jointPoints[6].x, self.jointPoints[6].y
 
        
        maxT = max(elbowT, shoulderT)
        if elbowT == maxT:
            elbowColour = red
            if shoulderT > maxT/2:
                shoulderColour = orange
                wristColour = orange
            else:
                shoulderColour = yellow
                wristColour = yellow
            
        elif shoulderT == maxT:
            shoulderColour = red
            if elbowT > maxT/2:
                elbowColour = orange
                wristColour = yellow
            else:
                elbowColour = yellow
                wristColour = yellow

        drawGradient(rightShoulder, rightElbow, shoulderColour, elbowColour, self.surface)
        drawGradient(rightElbow, rightWrist, elbowColour, wristColour, self.surface)
        drawGradient(leftShoulder, leftElbow, shoulderColour, elbowColour, self.surface)
        drawGradient(leftElbow, leftWrist, elbowColour, wristColour, self.surface)
        
    
    def ROM(self):
        wristL = 6
        chest = 20
        wristR = 10
        super().rangeOfMotion(wristL,chest,wristR,chest)
    
    def lockOut(self):
        #print (self.isSupine(), 'supine')
        self.pixelError = 20
        wristL = 6
        elbowL = 5
        shoulderL = 4
        wristR = 10
        elbowR = 9
        shoulderR = 8

        leftLockOut = (self.jointPoints[elbowL].y - self.jointPoints[wristL].y) > 170
        rightLockOut = (self.jointPoints[elbowR].y - self.jointPoints[wristR].y) > 170
        return (leftLockOut or rightLockOut) and self.isSupine()
        

class Deadlifter(Athlete):
    def draw(self):
        #draws the person
        deadliftJoints = {4,8,12,13,14,16,17,18,6,10}
        #shoulderL, shoulderR, hipL, kneeL, ankleL, hipR, kneeR, ankleR, wristL, wristR
        super().draw(deadliftJoints)
        #Dl: Knee, hip, back
        #neck to ass to knee to ankle
        
        kneeT = self.torqueLst[-1][0]
        hipT = self.torqueLst[-1][1]
        backT = self.torqueLst[-1][2]
        
        neck = self.jointPoints[2].x, self.jointPoints[2].y
        back = self.jointPoints[1].x, self.jointPoints[1].y
        tailbone = self.jointPoints[0].x, self.jointPoints[0].y
        
        rightHip = self.jointPoints[16].x, self.jointPoints[16].y
        rightKnee = self.jointPoints[17].x, self.jointPoints[17].y
        rightAnkle = self.jointPoints[18].x, self.jointPoints[18].y
        
        
        leftHip = self.jointPoints[12].x, self.jointPoints[12].y
        leftKnee = self.jointPoints[13].x, self.jointPoints[13].y
        leftAnkle = self.jointPoints[14].x, self.jointPoints[14].y

        maxT = max(kneeT, hipT, backT)
        
        neckColour = yellow
        ankleColour = yellow
        
        if kneeT == maxT: #doubt this will happen
            kneeColour = red
            if hipT > maxT/2:
                hipColour = orange
            else:
                hipColour = yellow
            if backT > maxT/2:
                backColour = orange
                tailboneColour = yellow
            else:
                backColour = yellow
                tailboneColour = yellow
            
        elif hipT == maxT:
            hipColour = red
            if kneeT > maxT/2:
                kneeColour = orange
            else:
                kneeColour = yellow
            if backT > maxT/2:
                backColour = orange
                tailboneColour = yellow
            else:
                backColour = yellow
                tailboneColour = yellow
                
        elif backT == maxT:
            backColour = red
            tailboneColour = orange
            if kneeT > maxT/2:
                kneeColour = orange
            else:
                kneeColour = yellow
            if hipT > maxT/2:
                hipColour = orange
            else:
                hipColour = yellow
            
        drawGradient(neck, back, neckColour, backColour, self.surface)
        drawGradient(back, tailbone, backColour, tailboneColour, self.surface)
      
        drawGradient(rightHip, rightKnee, hipColour, kneeColour, self.surface)
        drawGradient(rightKnee, rightAnkle, kneeColour, ankleColour, self.surface)
        drawGradient(leftHip, leftKnee, hipColour, kneeColour, self.surface)
        drawGradient(leftKnee, leftAnkle, kneeColour, ankleColour, self.surface)
        #print ('GRADIENT DRAWN')
        
    def ROM(self):
        #Note: this is not a strict competition requirement, but I'm writing it to make sure kinect knows that the lifter has picked up the barbell
        wristL = 6
        kneeL = 13
        wristR = 10
        kneeR = 17
        super().rangeOfMotion(6,13,10,17)
        #might not work for people with freakishly short shins :(
        
    def lockOut(self):
        #d: (knee, hip, shoulder --> femur and spine) and (hip, knee, ankle --> femur and shin)
        shoulderL = 4
        hipL = 12
        kneeL = 13
        shoulderR = 8
        hipR = 16
        kneeR = 17
        
        ankleL = 14
        ankleR = 18
        hipLockOut = super().lockOut(shoulderL, kneeL, hipL) or super().lockOut(shoulderR, kneeR, hipR)
        kneeLockOut = super().lockOut(hipL, kneeL, ankleL) or super().lockOut(hipR, kneeR, ankleR)

        return kneeLockOut and hipLockOut

       
