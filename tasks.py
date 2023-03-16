import psutil


def monitor_server():
    try:
        all_cpus = psutil.sensors_temperatures()['coretemp']
        cpu_temps = [t.current for t in all_cpus]
        cpu_temp_crit = all_cpus[0].critical
    except KeyError:
        with open('/sys/class/hwmon/hwmon0/temp1_input') as f:
            cpu_temps = [float(f.read()) / 1000]
        with open('/sys/class/hwmon/hwmon0/temp1_crit') as f:
            cpu_temp_crit = [float(f.read()) / 1000]

    cpu_temp_max = max(cpu_temps)
    cpu_load = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    cpu_freq_max = psutil.cpu_freq().max
    disk_usage = psutil.disk_usage('/home')

    return cpu_temp_max, cpu_temp_crit, cpu_load, ram_usage, cpu_freq_max, disk_usage
