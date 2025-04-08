import numpy as np

def get_human_delay(mean=8, std=2, min_delay=4, max_delay=12):
    delay = np.random.normal(loc=mean, scale=std)
    return round(max(min(delay, max_delay), min_delay), 2)
