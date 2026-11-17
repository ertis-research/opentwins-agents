class Airconditioning():
    def __init__(self, airconditioningID, season = 0, temp_range = [21,25], outside_temp = 23, starting_temp = 23):
        self.airconditioningID      = airconditioningID
        self.airconditioningState   = 0
        self.local_consumption      = 6 # SACADO DE UN AIRE DE INTERNET
        self._action_space          = 6
        self.season                 = season
        
        self.high_modifier          = 1.5
        self.low_modifier           = 1.1
        
        self.temp_range             = temp_range
        self.outside_temp           = outside_temp
        self.starting_temp          = starting_temp

    def getAirconditioningID(self):
        return self.airconditioningID
    def get_action_space(self):
        return self._action_space
    def getState(self):
        return self.airconditioningState

    def stop(self, aData):
        self.airconditioningState = 0
        if (aData["temperature"] + self.outside_temp)/2 < self.temp_range[0] or (aData["temperature"] + self.outside_temp)/2 > self.temp_range[1]:
            return None
        return {
                    'consumption': self.consumption(),
                    self.airconditioningID: {
                        "state":        self.airconditioningState,
                        "temperature":  (aData["temperature"] + self.outside_temp)/2

                    }
            }
    def keep(self, aData):
        if aData["temperature"] < self.temp_range[0] or aData["temperature"] > self.temp_range[1]:
            return None
        return {
                    'consumption': self.consumption(1),
                    self.airconditioningID: {
                        "state":        self.airconditioningState,
                        "temperature":  aData["temperature"]
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
            
        if aData["temperature"] + temp_change > self.temp_range[1]:
            return None
            
        consumption =  self.consumption(modifier) if self.season == 1 else self.consumption(1/modifier)
        return {
                    'consumption': consumption,
                    self.airconditioningID: {
                        "state":        self.airconditioningState,
                        "temperature":  aData["temperature"] + temp_change
                    }
                }
    def lowerTemp(self, aData, modifier):
        if modifier == self.low_modifier:
            self.airconditioningState = 3
            temp_change = -1
        else:
            self.airconditioningState = 4
            temp_change = -2
            
        if aData["temperature"] + temp_change < self.temp_range[0]:
            return None    
            
        consumption =  self.consumption(1/modifier) if self.season == 1 else self.consumption(modifier)
        return {
                    'consumption': consumption,
                    self.airconditioningID: {
                        "state":        self.airconditioningState,
                        "temperature":  aData["temperature"] + temp_change
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
            return round(self.local_consumption * modifier, 2)


    def getName(self):
        return self.airconditioningID
    
    def reset(self):
        self.airconditioningState = 0
        return {
            "state":        self.airconditioningState,
            "temperature":  self.starting_temp
        }