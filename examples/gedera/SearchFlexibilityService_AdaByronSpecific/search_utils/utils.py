from adabyron_environment.AdaByronDEMO_v2 import AdaByronDEMO
    
def define_env(agentes, consumption_curve = [], generated_curve = [], energy_price = [], season=0, temp_range = [21, 25]):
        
    env = AdaByronDEMO(agentes,consumption_curve, generated_curve, energy_price, season, temp_range)
    action_space = env.action_space
    
    return env, action_space