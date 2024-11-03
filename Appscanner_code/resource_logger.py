import psutil
import time
def log_resource_utilization(stage, data_processed=None, start_time=None):
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent
    print(f"[{stage}] CPU Usage: {cpu_usage}%, Memory Usage: {memory_usage}%")
    if data_processed is not None and start_time is not None:
        end_time = time.time()
        time_taken = end_time - start_time
        throughput = data_processed / time_taken
        print(f"Throughput: {throughput:.2f} units/second")
