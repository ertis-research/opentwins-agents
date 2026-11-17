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

    
    def stop(self, aData):
        self.airconditioningState = 0
        return {
                'consumption': self.consumption(),
                'temp_change': None,
                self.airconditioningID: {
                    "state":self.airconditioningState
                }
            }
    def keep(self, aData):
        return {
                    'consumption': self.consumption(1),
                    'temp_change': 0,
                    self.airconditioningID: {
                        "state":self.airconditioningState
                    }
                }
        
    # If the air conditioning is on, it will consume more or less depending on the season.
    def raiseTemp(self, aData, modifier):
        if modifier == self.low_modifier:
            self.airconditioningState = 1
            temp_change = 1
        else:
            self.airconditioningState = 2
            temp_change = 2
            
        consumption =  self.consumption(modifier)if self.season == 1 else self.consumption(1/modifier)
        return {
                    'consumption': consumption,
                    'temp_change': temp_change,
                    self.airconditioningID: {
                        "state":self.airconditioningState
                    }
                }
    def lowerTemp(self, aData, modifier):
        if modifier == self.low_modifier:
            self.airconditioningState = 3
            temp_change = -1
        else:
            self.airconditioningState = 4
            temp_change = -2
            
        consumption =  self.consumption(1/modifier)if self.season == 1 else self.consumption(modifier)
        return {
                    'consumption': consumption,
                    'temp_change': temp_change,
                    self.airconditioningID: {
                        "state":self.airconditioningState
                    }
                }    
    
    
    def step(self, action, aData):
        #print("Air conditioning {}, Action {}".format(self.airconditioningID, action))
        match action:
            case 0:
                return self.stop(aData)
            case 1:
                return self.keep(aData)
            case 2:
                return self.raiseTemp(aData, self.low_modifier)
            case 3:
                return self.raiseTemp(aData, self.high_modifier)
            case 4:
                return self.lowerTemp(aData, self.low_modifier)
            case 5:
                return self.lowerTemp(aData, self.high_modifier)
                
            
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


    def getName(self):
        return self.airconditioningID
    
    def reset(self):
        self.airconditioningState = 0
        return {
            "state":self.airconditioningState
        }