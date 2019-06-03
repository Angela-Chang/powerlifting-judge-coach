#the main that ties everything together. UI, lifter tracking
from pykinect2 import PyKinectV2, PyKinectRuntime
from pykinect2.PyKinectV2 import *
import sys
from Athlete import*
from fT import*
from Lift import*
import ctypes
import _ctypes
import pygame
import statistics

import math
import time
###This is based on code from the Kinect lecture, has been massively modified 
###https://github.com/Kinect/PyKinect2/blob/master/examples/PyKinectBodyGame.py
class GameRuntime(object):
    def __init__(self):
        pygame.init()

        # data = Struct
        self.message = ''
        self.lifterFound = False
        self.screenWidth = 1920
        self.screenHeight = 1080
        # Used to manage how fast the screen updates
        self.clock = pygame.time.Clock()

        # Set the width and height of the window [width/2, height/2]
        #PRINT ("DISP")
        self.screen = pygame.display.set_mode((960,540), pygame.HWSURFACE|pygame.DOUBLEBUF, 32)
        # Loop until the user clicks the close button.
        self.done = False
        self.setComplete = False

        # Kinect runtime object, we want color and body frames 
        self.kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)

        # back buffer surface for getting Kinect color frames, 32bit color, width and height equal to the Kinect color frame size
        self.frameSurface = pygame.Surface((self.kinect.color_frame_desc.Width, self.kinect.color_frame_desc.Height), 0, 32)

        # here we will store skeleton data 
        self.bodies = None
        
        self.mode = None


    def drawFrame(self):
        pass

    def drawColorFrame(self, frame, targetSurface):
        targetSurface.lock()
        address = self.kinect.surface_as_array(targetSurface.get_buffer())
        # replacing old frame with new one
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        targetSurface.unlock()

    def run(self):
        #only looks for the lifter once; this prevents bugginess and imporves efficiency
        self.W, self.H = pygame.display.get_surface().get_size()
                
        # -------- Main Program Loop -----------
        while not self.done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
                    pygame.quit()
            while self.mode == 't':
                #ts, tb, td
                rectS = (0, 0, self.W//3, self.H)
                rectB = (self.W//3, 0, 2*self.W//3, self.H)
                rectD = (2*self.W//3, 0, self.W, self.H)
                
                self.screen.fill(white)
                black = (0,0,0)
                black1 = (40,40,40)
                black2 = (80,80,80)
                pygame.draw.rect(self.screen,black, rectS)
                pygame.draw.rect(self.screen, black1, rectB)
                pygame.draw.rect(self.screen,black2, rectD)
                
                font = pygame.font.SysFont('copperplategothic', 28)
                lg = (250, 250, 250)
                
                
                sText = font.render('Squat', True, lg, None)
                sR = sText.get_rect()
                sR.center = (self.W//6, self.H//2)
                                
                bText = font.render('Bench', True, lg, None)
                bR = bText.get_rect()
                bR.center = (self.W//2, self.H//2)
                
                dText = font.render('Deadlift', True, lg, None)
                dR = dText.get_rect()
                dR.center = (5*self.W//6, self.H//2)
                
                self.screen.blit(sText, sR)
                self.screen.blit(bText, bR)
                self.screen.blit(dText, dR)

                pygame.display.flip()
                
                if pygame.event.get()!= None:
        
                    if pygame.mouse.get_pressed()[0]:#another click
        
                            x,y = pygame.mouse.get_pos()                 
                            if 0<x<self.W//3: self.mode = 'ts'
                            elif self.W//3 < x < 2*self.W//3: self.mode = 'tb'
                            elif 2*self.W//3 < x < self.W: self.mode = 'td'
                    
     
                        
            
            while self.mode == None:
                self.W, self.H = pygame.display.get_surface().get_size()
                
                white=(255,255,255)
                bg = white
                blue=(0,0,255)
                green = (0, 255, 0)

                rect1 = (0, 0, self.W//2, self.H)
                rect2 = (self.W//2, 0, self.W, self.H)
                
                self.screen.fill(white)
                comp = pygame.image.load('comp.png')
                comp = pygame.transform.scale (comp,(self.W//2, self.H) )
                
                train = pygame.image.load('plates.jpg')  
                train = pygame.transform.scale (train,(self.W//2, self.H) )              
                self.screen.blit(comp, rect1)
                self.screen.blit(train, rect2)
                black = (0,0,0)
                font = pygame.font.SysFont('copperplategothic', 60)
                lg = (250, 250, 250)
                compText = font.render('Competition', True, lg, None)
                cTR = compText.get_rect()
                cTR.center = (self.W//4, self.H//2)
                                
                trainText = font.render('Training', True, lg, None)
                tTR = trainText.get_rect()
                tTR.center = (3*self.W//4, self.H//2)
                
                self.screen.blit(compText, cTR)
                self.screen.blit(trainText, tTR)

                pygame.display.flip()

                for event in pygame.event.get(): 
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            
                            clickX, clickY = pygame.mouse.get_pos()
                            if clickX <= self.W//2:
                                self.mode = 'c'
                            elif clickX > self.W//2:
                                self.mode = 't'
                         
            if self.kinect.has_new_color_frame() and not self.lifterFound:
                self.bodies = self.kinect.get_last_body_frame() 
                if self.bodies is not None:
                    if self.mode == 'c':
                    #looks for the lifter and differentiates from spotters in comp mode
                        self.lifter = Athlete.findAthlete(self.bodies, self.kinect, self.frameSurface)#athlete is a buncha joints
                        if self.lifter is not None:
                            self.lifterFound = True
                            self.lifterIndex = self.lifter.index
                
                    for i in range(len(self.bodies.bodies)):
                        body = self.bodies.bodies[i]
                        if body.is_tracked:
                            jointPoints = self.kinect.body_joints_to_color_space(body.joints)
                            self.lifterIndex = i
                            if self.mode == 'ts':
                                
                                self.lifter = Squatter(body.joints, jointPoints, self.frameSurface, i)
                                self.lifterFound = True
                                
                                
                            elif self.mode == 'tb':
                                self.lifter = Bencher(body.joints, jointPoints, self.frameSurface, i)
                                self.lifterFound = True
                            elif self.mode == 'td':
                                self.lifter = Deadlifter(body.joints, jointPoints, self.frameSurface, i)
                                self.lifterFound = True
                 
            
            frame = self.kinect.get_last_color_frame()
            self.drawColorFrame(frame, self.frameSurface)
            frame = None
        
            
            if self.lifterFound and self.mode == 'c':
                if self.setComplete: self.whiteLights()
                try:
                    if self.kinect.has_new_body_frame(): 
                        self.bodies = self.kinect.get_last_body_frame()
                    bodyLst = list(self.bodies.bodies)
                    self.lifter.joints = bodyLst[self.lifterIndex].joints
                    self.lifter.jointPoints = self.kinect.body_joints_to_color_space(self.lifter.joints)
                    self.lifter.analyzeForm()
                    self.lifter.draw()
                    
                    self.lifter.oldJointPoints = self.lifter.joints
                    self.lifter.jointMovement.append(self.lifter.joints)

                    self.lifter.ROM()
                    if self.lifter.fullROM:
                     
                        if self.lifter.lockOut():
    
                            self.storeLift()
                            self.whiteLights()
                            
                except:                        
                    try:
                        self.lifter.jointPoints = self.lifter.oldJointPoints
                        self.lifter.analyzeForm()
                        self.lifter.draw()
                        self.lifter.ROM()
                        if self.lifter.fullROM:
                            
                            if self.lifter.lockOut():
                                
                                self.storeLift()
                                self.whiteLights()
                             
                    except: 
                        pass
                        
            elif self.lifterFound and not self.setComplete: # training mode
                bodyLst = list(self.bodies.bodies)
                if not bodyLst[self.lifterIndex].is_tracked:
                    self.finishedSet()
                try:
               
                    if self.kinect.has_new_body_frame(): 
                        self.bodies = self.kinect.get_last_body_frame()
                
                    self.lifter.joints = bodyLst[self.lifterIndex].joints
                    self.lifter.jointPoints = self.kinect.body_joints_to_color_space(self.lifter.joints)
                    self.lifter.analyzeForm()
                    self.lifter.draw()
                    self.lifter.oldJointPoints = self.lifter.joints
                    self.lifter.jointMovement.append(self.lifter.joints)
                    
                    if not self.lifter.fullROM:
                        self.lifter.ROM()
    
                    if self.lifter.fullROM and self.lifter.lockOut():
                        self.lifter.fullROM = False
                        self.lifter.reps += 1
                        self.storeLift()
                        
                except:                        
                    try:
                        self.lifter.jointPoints = self.lifter.oldJointPoints
                        self.lifter.draw()
                    except:
                        pass
            if self.setComplete and self.mode != 'c':
                self.finishedSet()        

            if not self.setComplete:
                hToW = float(self.frameSurface.get_height()) / self.frameSurface.get_width()
                targetHeight = int(hToW * self.screen.get_width())
                surfaceToDraw = pygame.transform.scale(self.frameSurface, (self.screen.get_width(), targetHeight));
                self.screen.blit(surfaceToDraw, (0,0))
                surfaceToDraw = None
              
                font = pygame.font.SysFont('arial', 28)
                lg = (250, 250, 250)
                if self.lifterFound and self.mode in {'ts', 'tb', 'td'}:
                
                    repText = font.render(str(self.lifter.reps)+' reps', True, lg, (0,0,0))
                    rect = repText.get_rect()
                    rect.center = (100,100)
                    self.screen.blit(repText, rect)
                    pygame.display.flip()
              
                elif self.lifterFound and self.mode == 'c':
                    if self.lifter.fullROM and not self.setComplete:
                        compText = font.render("Range of motion completed", True, lg, (0,0,0))
                        rect = compText.get_rect()                    
                        rect.center = (self.W//2,100)
                        self.screen.blit(compText, rect)
                        pygame.display.flip()
                    if self.lifter.fullROM and self.lifter.lockOut():
                        self.whiteLights()
                pygame.display.update()

            # --- Limit to 60 frames per second
            self.clock.tick(60)

        if self.done:
            self.kinect.close()
            pygame.quit()
            

        
            
    def getMessage(self):
        self.message = ''
        dataSet = Lift.makeDataSet(self.liftType)
        fastestTimes = list(dataSet.keys())
        fastestTimes.sort()
        
        holes = []
        stickingPoints = [] #list of tuples
        
        i=0
        while len(holes) < (50):
            #try:
                time = fastestTimes[i]
                fastLift = dataSet[time]
                hole = len(fastLift)//2
                hole = fastLift[hole]
            
                # halfway up and 3/4 of the way up are where people commonly fail lifts
                if '' not in hole: holes.append(hole)
                i += 1
                
            #except:
                #pass
        i = 0
        while len(stickingPoints) < 50:
                time = fastestTimes[i]
                fastLift = dataSet[time]
          
                stickingPoint = int(len(fastLift)*.75)
                stickingPoint = fastLift[stickingPoint]
                if '' not in stickingPoint: stickingPoints.append(stickingPoint)
                i+= 1
            
        #exit loop
        if self.liftType == 'squat':
            # 2 torques: average all of them
            kneeHole = [float(hole[0]) for hole in holes]
            kneeHoleMean = removeOutliers(kneeHole)
            hipHole = [float(hole[1]) for hole in holes]
            hipHoleMean = removeOutliers(hipHole)
            kneeSP = [float(point[0]) for point in stickingPoints]
            kneeSPMean = removeOutliers(kneeSP)
            hipSP = [float(point[0]) for point in stickingPoints]
            hipSPMean = removeOutliers(hipSP)
            
            newMid = len(self.newLift.torques)//2
            newMidTorque = self.newLift.torques[newMid]
            newKneeHole = newMidTorque[0]
            newHipHole = newMidTorque[1]
            
            newSP =int (len(self.newLift.torques)*.75)
            newSPT = self.newLift.torques[newSP]
            newKneeSP = newSPT[0]
            newHipSP = newSPT[1]
            self.message = []
            if newKneeHole <= .8*(kneeHoleMean):
                self.message.append("Try to stay more upright at the bottom.")
            if newHipHole <= .8*(hipHoleMean):
                self.message.append("Focus on pushing your hips up.")
            if newHipSP <= .8*(hipSPMean):
                self.message.append("Keep your knees out throughout the movement.")
            if newKneeSP <= .8*(kneeSPMean):
                self.message.append("Make sure to push through the middle your foot.")
            
    def whiteLights(self):
        self.setComplete = True

        pygame.font.init()
        font = pygame.font.SysFont('arial', 28)
        lg = (250, 250, 250)
        endText = font.render('Congratulations, your attempt was successful!', True, lg, None)
        rect = endText.get_rect()
        rect.center = (self.W//2, self.H//2)
        self.screen.fill((0,0,0))
        self.screen.blit(endText, rect)
        pygame.display.flip()
   
        #pygame.display.update
    def finishedSet(self):
            self.setComplete = True
            if not isinstance(self.lifter, Squatter):
                font = pygame.font.SysFont('arial', 28)
                lg = (250, 250, 250)
                endText = font.render('You completed '+str(self.lifter.reps)+' reps', True, lg, None)
                rect = endText.get_rect()
                rect.center = (self.W//2, self.H//2)
                self.screen.fill((0,0,0))
                self.screen.blit(endText, rect)
                pygame.display.flip()
            
            else:
                if self.message != '':
                    font = pygame.font.SysFont('arial', 28)
                    lg = (250, 250, 250)
                    center = [self.W//2, self.H//2-30]
                    self.screen.fill ((0,0,0))
                    
                    
                    for line in self.message:
                        center[1] += 30
                        msgText = font.render(line, True, lg, (0,0,0))
                        rect = msgText.get_rect()
                        rect.center = tuple(center)
                        self.screen.blit(msgText, rect)
                    pygame.display.flip()
                    pygame.display.update()
                elif self.message == []:
                    font = pygame.font.SysFont('arial', 28)
                    lg = (250, 250, 250)
                    center = (self.W//2, self.H//2)
                    self.screen.fill ((0,0,0))
                    msgText = font.render('Great lift! No criticism here.', True, lg, (0,0,0))
                    rect = msgText.get_rect()
                    rect.center = center
                    self.screen.blit(msgText, rect)
                    
                    
                
                elif self.message == '' and isinstance(self.lifter, Squatter):
                    font = pygame.font.SysFont('arial', 28)
                    lg = (250, 250, 250)
                    endText = font.render('You completed '+str(self.lifter.reps)+' reps', True, lg, None)
                    rect = endText.get_rect()
                    rect.center = (self.W//2, self.H//2)
                    self.screen.fill((0,0,0))
                    self.screen.blit(endText, rect)
                    
                    #form analysis stuff
                    rect = (0, int(self.H*.7), self.W, self.H)
                    
                    grey = (202, 204, 206)
                    pygame.draw.rect(self.screen,grey, rect)
                    
                    font = pygame.font.SysFont('copperplategothic', 18)
                    lg = (250, 250, 250)
                    
                    
                    text = font.render('Click here for form analysis!', True, lg, None)
                    textRect = text.get_rect()
                    textRect.center = (self.W//2, int(self.H*.85))
                    
                    self.screen.blit(text, textRect)            
                    pygame.display.flip()
                    
                    if pygame.event.get()!= None:
                    
                        if pygame.mouse.get_pressed()[0]:
                                x,y = pygame.mouse.get_pos()                 
                                if self.H*.7<y<self.H: self.getMessage()
                          

        
    
    def storeLift(self):

        if isinstance(self.lifter, Squatter): type = "squat"
        elif isinstance(self.lifter, Bencher): type = 'bench'
        elif isinstance(self.lifter, Deadlifter): type = 'deadlift'
        self.liftType = type
        self.lifter.end=time.time()
        timeToComplete = self.lifter.end - self.lifter.start
        self.newLift = Lift(type, timeToComplete, self.lifter.jointMovement, self.lifter.torqueLst)
       
        #a new rep:
        self.lifter.start = time.time()
        self.lifter.jointMovement = []
        self.lifter.torqueLst = []
        
        
def removeOutliers(lst):
    mean = statistics.mean(lst)
    sd = statistics.stdev(lst)
    for ele in lst:
        if abs(ele - mean) > .5*sd:
            lst.remove(ele)
    newMean = statistics.mean(lst)
    return newMean
game = GameRuntime();
game.run();
