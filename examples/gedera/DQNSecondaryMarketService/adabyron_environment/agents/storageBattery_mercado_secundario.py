class StorageBatteryMS():
    def __init__(self, storageBatteryID, capacity = 120.0, recharges = 2, original_soc = 120):
        """
            Initilization method
            : param
                capacity - Capacity of the Storage Battery
        """
        self.storageBatteryID: str  = storageBatteryID
        self.original_soc: float    = original_soc
        self.capacity: float        = capacity #kWh
        self.recharges         = recharges
        self.maxCharges      = capacity * recharges
        #print(self.maxCharges)
        self._action_space          = 3
        self.maxChargePower         = 60 #kWh
        self.maxDischargePower      = 100 #kWh
        
        
    # Si cargo pago    
    def charge(self, bData):
        
        newBData = bData.copy()
        consumption_max: float    = self.maxChargePower
        consumption          = min(consumption_max, self.capacity-bData['soc'])
        consumption          = min(consumption, self.maxCharges-bData['chargeHistory'])
        newSOC: float             = newBData['soc'] + consumption
        newChargeHistory: float   = newBData['chargeHistory'] + consumption
        
        if newSOC > self.capacity or newChargeHistory > self.maxCharges or consumption == 0:
            return None, {
            'consumption' : consumption,
            self.storageBatteryID: newBData
        }
        
        newBData['soc']             = newSOC
        newBData['chargeHistory']   = newChargeHistory
        
        
        
        return {
            'consumption' : consumption,
            self.storageBatteryID: newBData
        }, None
    
    # Si descargo me pagan
    def discharge(self, bData):
        newBData               = bData.copy()
        consumption_max: float      = self.maxDischargePower
        consumption            = min(consumption_max, bData['soc'])
        consumption            = min(consumption, self.maxCharges-bData['dischargeHistory'])
        newSOC: float               = newBData['soc'] - consumption
        newDischargeHistory: float  = newBData['dischargeHistory'] + consumption
        #difference = bData['soc'] + consumption - self.capacity
        
        
        
        newBData['soc']              = newSOC
        newBData['dischargeHistory'] = newDischargeHistory
        
        #print(bData)
        
        if newSOC < 0 or newDischargeHistory > self.maxCharges or consumption == 0:
            return None, {
            'consumption' : -consumption,
            self.storageBatteryID: newBData
        }
            
        return {
            'consumption' : -consumption,
            self.storageBatteryID: newBData
        }, None
        
    def skip(self, bData):
        """
            Stop processing
        """
        return {
            'consumption' : 0,
            self.storageBatteryID: bData
        }, None
        
    
    def step(self, action, bData):
        match action:
            case 0:
                return self.skip(bData)
            case 1:
                return self.charge(bData)
            case 2:
                return self.discharge(bData)

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
    def get_action_name(self, action):
        match action:
            case 0:
                return 'skip'
            case 1:
                return 'charge'
            case 2:
                return 'discharge'