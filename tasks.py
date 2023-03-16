import psutil
from gpustat import GPUStatCollection


def monitor_cpu():
    try:
        all_cpus = psutil.sensors_temperatures()['coretemp']
        cpu_temps = [t.current for t in all_cpus]
        cpu_temp_crit = all_cpus[0].critical
    except KeyError:
        with open('/sys/class/hwmon/hwmon0/temp1_input') as f:
            cpu_temps = [float(f.read()) / 1000]
        with open('/sys/class/hwmon/hwmon0/temp1_crit') as f:
            cpu_temp_crit = float(f.read()) / 1000

    cpu_temp_max = max(cpu_temps)
    cpu_load = psutil.cpu_percent()
    cpu_freq_max = psutil.cpu_freq().max

    return cpu_temp_max, cpu_temp_crit, cpu_load, cpu_freq_max


def monitor_disk():
    disk_usage = psutil.disk_usage('/home')
    return disk_usage


def monitor_ram():
    ram_usage = psutil.virtual_memory().percent
    return ram_usage


def monitor_gpu():
    gpus = GPUStatCollection.new_query(debug=False).gpus
    gpu_temp = 0
    for gpu in gpus:
        _gpu_temp = gpu.temperature
        _gpu_util = gpu.utilization
        _gpu_memory_free = gpu.memory_free
        _user = gpu.processes[0]['username']
        _gpu_idx = gpu.index
        _gpu_name = gpu.name
        if _gpu_temp > gpu_temp:
            gpu_temp = _gpu_temp
            gpu_util = _gpu_util
            gpu_memory_free = _gpu_memory_free
            user = _user
            gpu_idx = _gpu_idx
            gpu_name = _gpu_name

    return gpu_temp, gpu_util, gpu_memory_free, user, gpu_idx, gpu_name
