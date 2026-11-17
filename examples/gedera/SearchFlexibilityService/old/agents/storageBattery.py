class StorageBattery():
    def __init__(self, storageBatteryID, capacity = 120.0, soc = 0.5, maxCharges = 2):
        """
            Initilization method
            : param
                capacity - Capacity of the Storage Battery
        """
        self.storageBatteryID = storageBatteryID
        
        self.capacity = capacity
        self.maxCharge = capacity * 2
        self.maxDischarge = capacity * 2
        
        self.state = soc
        self.soc = self.capacity * self.state if self.state else self.capacity * 0.5 
        self.consumption = 0
        self._action_space = 7
        
        self.chargeHistory = 0
        self.dischargeHistory = 0
        
    def charge20(self, bStatus):
        """
            Simulation of 20Kwh charge (20kwh = 5kw per 15 minutes)
        """
        # Nuevo estado de carga
        diff = self.capacity - (bStatus["soc"] + 5)
        if diff > 0
        
        # TODO: Hay que comprobar de nuevo como funciona la bateria, no tiene sentido como estaba hecho
        
        if bStatus["chargeHistory"] + newConsumption > self.maxCharge or :
            return None
        
        bStatus["soc"] -= newConsumption
        bStatus["chargeHistory"] += newConsumption
        return {
            "consumption":-self.consumption,
            "storageBatteryID": bStatus
        }
    def charge40(self, bStatus):
        """
            Simulation of 40Kwh charge (40kwh = 10kw per 15 minutes)
            : return consumption
        """
        
        newConsumption = bStatus["soc"] -  min(self.capacity, bStatus["soc"] + 10)
        
        if bStatus["chargeHistory"] + newConsumption > self.maxCharge:
            return None
        
        
        bStatus["soc"] -= newConsumption
        bStatus["chargeHistory"] += newConsumption
        return {
            "consumption":-self.consumption,
            "storageBatteryID": bStatus
        }
    def charge60(self, bStatus):
        """
            Simulation of 60Kwh charge (60kwh = 15kw per 15 minutes)
            : return consumption
        """
        newConsumption = bStatus["soc"] -  min(self.capacity, bStatus["soc"] + 15)
        
        if bStatus["chargeHistory"] + newConsumption > self.maxCharge:
            return None
        
        
        bStatus["soc"] -= newConsumption
        bStatus["chargeHistory"] += newConsumption
        return {
            "consumption":-self.consumption,
            "storageBatteryID": bStatus
        }
    
    def discharge20(self, bStatus):
        """
            Simulation of 20Kwh discharge (20kwh = 5kw per 15 minutes)
            : return consumption
        """
        newConsumption = min(5, abs(bStatus["soc"]-5))
        
        if bStatus["dischargeHistory"] - newConsumption < self.maxDischarge:
            return None
        
        
        if self.dischargeHistory >= self.capacity:
            return None, None
        
        self.consumption = min(5, abs(self.soc - 5))
        self.soc -=  self.consumption
        self.dischargeHistory += self.consumption
        return -self.consumption, 0
    def discharge40(self, bStatus):
        """
            Simulation of 40Kwh discharge (40kwh = 10kw per 15 minutes)
            : return consumption
        """
        if self.dischargeHistory >= self.capacity:
            return None, None
        
        self.consumption = min(10, abs(self.soc - 10))
        self.soc -= self.consumption
        self.dischargeHistory += self.consumption
        return -self.consumption, 0
    def discharge60(self, bStatus):
        """
            Simulation of 60Kwh discharge (60kwh = 15kw per 15 minutes)
            : return consumption
        """
        if self.dischargeHistory >= self.capacity:
            return None, None
        
        self.consumption = min(15, abs(self.soc - 15))
        self.soc -= self.consumption
        self.dischargeHistory += self.consumption
        return -self.consumption, 0
    
    def step(self, action):
        match action:
            case 0:
                return self.stop()
            case 1:
                return self.charge20()
            case 2:
                return self.charge40()
            case 3:
                return self.charge60()
            case 4:
                return self.discharge20()
            case 5:
                return self.discharge40()
            case _:
                return self.discharge60()
    def stop(self, bStatus):
        """
            Stop processing
        """
        self.consumption = 0
        return self.consumption, 0
        
    def get_soc(self):
        """
            get state of charge
        """
        return self.soc       
    def render(self, mode="human"):
        """
            Print the ev charging station status
        """
        
        print ("SB {} -> TotalCapacity: {}".format(self.storageBatteryID, self.capacity)) 
    def reset(self):
        self.soc = self.capacity * self.state if self.state else self.capacity * 0.5 
        self.consumption = 0
        return {
            "soc" : 0,
            "chargeHistory" : 0,
            "dischargeHistory" : 0
        }

    def getStorageBatteryID(self):
        return self.storageBatteryID
    def get_action_space(self):
        return self._action_space
    def getState(self):
        return self.state