import psutil
import time
import gc

def log_resource_utilization(stage, data_processed=None, start_time=None):
    gc.collect()
    process = psutil.Process()
    # Get memory usage specific to this process (RSS - Resident Set Size)
    memory_info = process.memory_full_info().uss  / (1024 * 1024)
    cpu_usage = process.cpu_percent(interval=1)
    print(f"[{stage}] CPU Usage: {cpu_usage}% Memory Usage: {memory_info:.2f} MB")
    if data_processed is not None and start_time is not None:
        end_time = time.time()
        time_taken = end_time - start_time
        throughput = data_processed / time_taken
        print(f"Throughput: {throughput:.2f} units/second")



