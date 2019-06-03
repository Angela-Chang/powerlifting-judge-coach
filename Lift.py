#stores every lift performed in a text file and uses that to reconstruct a dictionary of times mapping to torque-tuples

class Lift (object):
    def __init__(self, type, time, jointMovement, torques):
        self.type = type
        self.time = time
        self.jointMovement = jointMovement
        self.torques = torques
        self.writeToFile()
        
    def __repr__(self):

        return str(self.time) + "$" + self.lstToStr() + 'n'
        
    def lstToStr(self):

        result = ''
 
        for ele in self.torques:
            result += str(ele)+'%'
        return result

    def writeToFile(self):
 
        if self.type == 'squat':
            f = open('squat.txt', 'a+')
            f.write(str(self))
        elif self.type == 'bench':
            f = open('bench.txt', 'a+')
            f.write(str(self))
        elif self.type == 'deadlift':
            f = open('deadlift.txt', 'a+')
   
            f.write(str(self))
            
            
    @staticmethod
    def makeDataSet(liftType):
        data = {}
        g = open(str(liftType)+'.txt', 'r')
        g = g.read()
    
        
        for lift in g.split('n'):
            result = []
       
            time = lift.split('$')[0]
      
            try:
                timeF = float(time)
           
                torques = lift.split('$')[1]
                for torque in torques.split('%'):
                    
                    newLst = []
                    for ele in torque[1:-2].split(','):
                        newLst.append(ele)
                    newLst = tuple(newLst)
                    result.append(newLst)
                    
                result = tuple(result)
                data[timeF] = result
            except: pass
   
        return data
        
                
            
        