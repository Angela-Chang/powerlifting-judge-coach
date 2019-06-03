#draw gradient line as a collection of dots
#yay pretty colours
import pygame

        
def drawGradient(point1, point2, colour1, colour2, surface):
    #points are tuples (x,y)
    #pixels between 2 points
        x1 = point1[0]
        x2 = point2[0]
        y1 = point1[1]
        y2 = point2[1]
        dx = x2-x1
        dy = y2-y1
        slope = dy/dx
        n = ((dy**2 + dx**2)**(1/2))
        n = int(n)
        
        dc0 = (colour2[0] - colour1[0])/n
        dc1 = (colour2[1] - colour1[1])/n
        dc2 = (colour2[2] - colour1[2])/n
        
        dotColour = (colour1)
        x0 = int(x1)
        y0 = int(y1)
        i = 0
        while i <= n:
            x = int(x0)
            y = int(y0)
            colour = (int(dotColour[0]), int(dotColour[1]), int(dotColour[2]))
            pygame.draw.circle(surface, dotColour, (x, y), 10)
            dotColour = (dotColour[0]+ dc0, dotColour[1]+ dc1, dotColour[2]+dc2)
            x0+=dx/n
            y0+=dy/n
            i += 1

        
        
    
        
        
    
    