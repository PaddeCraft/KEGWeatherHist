import sched
import time

current_data = {
    "temperature": ""
}

def load_data(scheduler):
    scheduler.enter(60, 1, load_data, (scheduler,))
    
def start_loading_loop():
    loading_scheduler = sched.scheduler(time.time, time.sleep)
    load_data(loading_scheduler)
    loading_scheduler.run(False)
    
    return loading_scheduler