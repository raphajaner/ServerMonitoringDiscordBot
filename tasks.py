import psutil


def monitor_server():
    try:
        cpu_temps = [t.current for t in psutil.sensors_temperatures()['coretemp']]
    except KeyError:
        with open('/sys/class/hwmon/hwmon0/temp1_input') as f:
            cpu_temps = [float(f.read()) / 1000]

    cpu_temp_max = max(cpu_temps)
    cpu_load = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    cpu_freq_max = psutil.cpu_freq().max
    disk_usage = psutil.disk_usage('/home')

    return cpu_temp_max, cpu_load, ram_usage, cpu_freq_max, disk_usage
