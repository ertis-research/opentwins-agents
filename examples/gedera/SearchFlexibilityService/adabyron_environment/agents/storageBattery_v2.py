class StorageBattery():
    def __init__(self, storageBatteryID, capacity = 120.0, recharges = 2, current_soc = 20):
        """
            Initilization method
            : param
                capacity - Capacity of the Storage Battery
        """
        self.storageBatteryID: str  = storageBatteryID
        
        self.capacity: float        = capacity
        self.recharges = recharges
        self.maxCharges = capacity * recharges
        
        #self._action_space = 7
        self._action_space = 17
        self.maxChargePower = 60
        self.maxDischargePower = 100

        self.init_soc = current_soc
        
    def charge(self, bData, s_cons):
        """
            Simulation of 20Kwh charge (20kwh = 5kw per 15 minutes)
            : return consumption
        """
        newBData = bData.copy()
        consumption: float    = s_cons
        newSOC: float         = newBData['soc'] + consumption
        newChargeHistory: float = newBData['chargeHistory'] + consumption
        #difference = bData['soc'] + consumption - self.capacity
        
        if newSOC > self.capacity or newChargeHistory > self.maxCharges:
            return None
        
        newBData['soc'] = newSOC
        newBData['chargeHistory'] += consumption
        newBData['consumption'] = consumption
        
        #print(bData)
        
        return {
            'consumption' : consumption,
            self.storageBatteryID: newBData
        }
    
    def discharge(self, bData, s_cons):
        """
            Simulation of 20Kwh charge (20kwh = 5kw per 15 minutes)
            : return consumption
        """
        newBData = bData.copy()
        consumption: float    = s_cons
        newSOC: float         = newBData['soc'] - consumption
        newChargeHistory: float = newBData['dischargeHistory'] + consumption
        #difference = bData['soc'] + consumption - self.capacity
        
        if newSOC < 0 or newChargeHistory > self.maxCharges:
            return None
        
        newBData['soc'] = newSOC
        newBData['dischargeHistory'] += consumption
        newBData['consumption'] = -consumption
        
        #print(bData)
        
        return {
            'consumption' : -consumption,
            self.storageBatteryID: newBData
        }
        
    def skip(self, bData):
        """
            Stop processing
        """
        return {
            'consumption' : 0,
            self.storageBatteryID: bData
        } 
        
    
    def step(self, action, bData):
        match action:
            # case 0:
            #     return self.skip(bData)
            # case 1:
            #     return self.charge(bData, 30)
            # case 2:
            #     return self.charge(bData, 60)
            # case 3:
            #     return self.charge(bData, 100)
            # case 4:
            #     return self.discharge(bData, 30)
            # case 5:
            #     return self.discharge(bData, 60)
            # case _:
            #     return self.discharge(bData, 100)
            case 0:
                return self.skip(bData)
            case 1:
                return self.charge(bData, 10)
            case 2:
                return self.charge(bData, 20)
            case 3:
                return self.charge(bData, 30)
            case 4:
                return self.charge(bData, 40)
            case 5:
                return self.charge(bData, 50)
            case 6:
                return self.charge(bData, 60)
            case 7:
                return self.discharge(bData, 10)
            case 8:
                return self.discharge(bData, 20)
            case 9:
                return self.discharge(bData, 30)
            case 10:
                return self.discharge(bData, 40)
            case 11:
                return self.discharge(bData, 50)
            case 12:
                return self.discharge(bData, 60)
            case 13:
                return self.discharge(bData, 70)
            case 14:
                return self.discharge(bData, 80)
            case 15:
                return self.discharge(bData, 90)
            case _:
                return self.discharge(bData, 100)

    def render(self, mode="human", bData = None):
        """
            Print the ev charging station status
        """
        print ("SB {} -> TotalCapacity: {}".format(self.storageBatteryID, self.capacity))
        if bData: 
            print(bData)
            
    def reset(self):
        return {
            'soc' : self.init_soc,
            'chargeHistory':0,
            'dischargeHistory':0,
            'consumption':0
        }

    def getName(self):
        return self.storageBatteryID
    def get_action_space(self):
        return self._action_space