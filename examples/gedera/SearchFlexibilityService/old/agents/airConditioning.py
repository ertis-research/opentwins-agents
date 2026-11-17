class Airconditioning():
    def __init__(self, airconditioningID, season = 0):
        self.airconditioningID = airconditioningID
        self.airconditioningState = 0
        self.local_consumption = 35
        self._action_space = 6
        self.season = season
        
        self.high_modifier = 1.5
        self.low_modifier = 1.1

    def getAirconditioningID(self):
        return self.airconditioningID
    def get_action_space(self):
        return self._action_space
    def getState(self):
        return self.airconditioningState

    
    def stop(self):
        self.airconditioningState = 0
        return [self.consumption(), None]
    def keep(self):
        return [self.consumption(1), 0]
    # If the air conditioning is on, it will consume more or less depending on the season.
    def raiseTempLow(self):
        self.airconditioningState = 1
        return [self.consumption(self.low_modifier), 1] if self.season == 1 else [self.consumption(1/self.low_modifier), 1]
    def raiseTempHigh(self):
        self.airconditioningState = 2
        return [self.consumption(self.high_modifier), 2] if self.season == 1 else [self.consumption(1/self.high_modifier), 2]
    def lowerTempLow(self):
        self.airconditioningState = 3
        return [self.consumption(1/self.low_modifier), -1] if self.season == 1 else [self.consumption(self.low_modifier), -1]
    def lowerTempHigh(self):
        self.airconditioningState = 4
        return [self.consumption(1/self.high_modifier), -2] if self.season == 1 else [self.consumption(self.high_modifier), -2]
    
    
    
    def step(self, action, aData):
        #print("Air conditioning {}, Action {}".format(self.airconditioningID, action))
        match action:
            case 0:
                return self.stop(aData)
            case 1:
                return self.raiseTempLow(aData)
            case 2:
                return self.raiseTempHigh(aData)
            case 3:
                return self.lowerTempLow(aData)
            case 4:
                return self.lowerTempHigh(aData)
            case 5:
                return self.keep()
            
    def render(self, mode = "human"):
        print("Air conditioning {} -> State {}, Consumption {}".format(self.airconditioningID, self.airconditioningState, self.consumption()))
        
    def consumption(self, modifier = 1):
        if self.airconditioningState == 0:
            #return -20
            #print("Consumo del dispositivo apagado: {}".format(0))
            return 0
        else:
            #Base consumption + consumption addded per grade
            # 1,13 - It is the coefficient of passage from frigories to watts.
            #print("Consumo del dispositivo: {}".format(round(20 + self.airconditioningState*15, 2)))
            #return round(20 + self.airconditioningState*15, 2) # Using 15 because it is a quarter-hourly time slot.
            self.local_consumption  = self.local_consumption * modifier
            return round(self.local_consumption, 2)
    def reset(self):
        self.airconditioningState = 0
    def getName(self):
        return self.airconditioningID
    
    def reset(self):
        return {
            "state":self.airconditioningState
        }