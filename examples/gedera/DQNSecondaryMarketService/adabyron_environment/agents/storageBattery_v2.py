class StorageBattery():
    def __init__(self, storageBatteryID, capacity = 120.0, recharges = 2, original_soc = 120):
        """
            Initilization method
            : param
                capacity - Capacity of the Storage Battery
        """
        #ACTUALMENTE LA BATERIA ESTA CONFIGURADA PARA FUNCIONAR DE FORMA HORARIA
        self.storageBatteryID: str  = storageBatteryID
        self.original_soc: float    = original_soc
        self.capacity: float        = capacity #kWh
        self.recharges         = recharges
        self.maxCharges      = capacity * recharges
        self._action_space          = 7
        self.maxChargePower         = 60 #kWh
        self.maxDischargePower      = 100 #kWh
        
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
            case 0:
                return self.skip(bData)
            case 1:
                return self.charge(bData, 20)
            case 2:
                return self.charge(bData, 40)
            case 3:
                return self.charge(bData, 60)
            case 4:
                return self.discharge(bData, 20)
            case 5:
                return self.discharge(bData, 40)
            case 7:
                return self.discharge(bData, 60)

    def render(self, mode="human", bData = None):
        """
            Print the ev charging station status
        """
        print ("SB {} -> TotalCapacity: {}".format(self.storageBatteryID, self.capacity))
        if bData: 
            print(bData)
            
    def reset(self):
        return {
            'soc' : self.original_soc,
            'chargeHistory':0,
            'dischargeHistory':0
        }

    def getName(self):
        return self.storageBatteryID
    def get_action_space(self):
        return self._action_space