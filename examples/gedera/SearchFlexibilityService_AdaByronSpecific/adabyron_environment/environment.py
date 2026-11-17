import json

class State():
    def __init__(self, 
                 father = None, 
                 consumption = 0,
                 cumulative_consumption = 0,
                 price=0,
                 cumulative_price = 0,
                 episode_ended = False,
                 day_step = -1,
                 actions = {},
                 agents_info = {},
                 specific = {}):
        # Final solution building
        self.father = father
        
        # Global consumption and price info
        self.consumption                = consumption
        self.cumulative_consumption     = cumulative_consumption
        self.price                      = price
        self.cumulative_price           = cumulative_price
        self._episode_ended             = episode_ended
        
        self.day_step                   = day_step
        self.actions                    = actions
        self.agents_info                = agents_info
        self.specific                   = specific

        
        
        
    def __lt__(self, other):
        if self.day_step == other.day_step:
            return self.cumulative_price < other.cumulative_price
        elif self.day_step > other.day_step:
            return True
        else:
            return False

    def __gt__(self, other):
        if self.day_step == other.day_step:
            return self.cumulative_price > other.cumulative_price
        elif self.day_step < other.day_step:
            return True
        else:
            return False
        
    def __str__(self):
        return json.dumps({
        "consumption"             : self.consumption,
        "cumulative_consumption"  : self.cumulative_consumption,
        "price"                   : self.price,
        "cumulative_price"        : self.cumulative_price,
        "_episode_ended"          : self._episode_ended,
        "day_step"                : self.day_step,
        "actions"                 : self.actions,
        "agents_info"             : self.agents_info,
        "specific"                : self.specific,
                }, indent = 4)
        
        
    def to_dict(self):

        # Global consumption and price info

        return {
        "father"                  : self.father.to_dict() if self.father else None,
        "consumption"             : self.consumption,
        "cumulative_consumption"  : self.cumulative_consumption,
        "price"                   : self.price,
        "cumulative_price"        : self.cumulative_price,
        "_episode_ended"          : self._episode_ended,
        "day_step"                : self.day_step,
        "actions"                 : self.actions,
        "agents_info"             : self.agents_info,
        "specific"                : self.specific,
                }