import asyncio
import os
import discord
import psutil
from discord.ext import tasks
import socket
from pathlib import Path
from psutil._common import bytes2human


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


class MyClient(discord.Client):

    async def on_ready(self):
        print('Logged on as', self.user)

    async def setup_hook(self) -> None:
        self.check_temp.start()
        self.check_disk.start()

    async def on_message(self, message):
        # Don't respond to ourselves
        if message.author == self.user:
            return

        if message.content.lower() == 'ping':
            cpu_temp_max, cpu_load, ram_usage, cpu_freq_max, disk_usage = monitor_server()
            await message.channel.send(
                f'Server: *{socket.gethostname()}*\n'
                f'- T_CPU_max = {cpu_temp_max}°C\n'
                f'- CPU_load = {cpu_load}%\n'
                f'- RAM_usage = {ram_usage}%\n'
                f'- f_CPU_max = {int(cpu_freq_max)}Hz\n'
                f'- C_home_usage = {disk_usage.percent}%\n'
            )

    @tasks.loop(seconds=10)
    async def check_temp(self):
        channel = self.get_channel(1082732904788000770)  # channel ID goes here
        if channel is None:
            print('Channel not found')

        cpu_temp_max, cpu_load, ram_usage, cpu_freq_max, disk_usage = monitor_server()

        if cpu_temp_max > 80:
            await channel.send(
                f'Warning @here!\n'
                f'Server: *{socket.gethostname()}*\n'
                f'Getting hot in here: '
                f'- T_CPU_max = {cpu_temp_max}°C\n'
                f'- CPU_load = {cpu_load}%\n'
            )
            await asyncio.sleep(60 * 60 * 0.5)

    @tasks.loop(hours=1)
    async def check_disk(self):
        channel = self.get_channel(1082732904788000770)  # channel ID goes here
        if channel is None:
            print('Channel not found')
        _, _, _, _, disk_usage = monitor_server()
        if disk_usage.percent > 90:
            await channel.send(
                f'**Warning @here!**\n'
                f'Server: *{socket.gethostname()}*\n'
                f'Running out of disk space on /home:\n'
                f'- C_home_usage = {disk_usage.percent}%\n'
                f'- C_home_used = {bytes2human(disk_usage.used)}\n'
                f'- C_home_free = {bytes2human(disk_usage.free)}\n'
                f'- C_home_total = {bytes2human(disk_usage.total)}\n'
            )
            await asyncio.sleep(60 * 60 * 24)

    @check_temp.before_loop
    async def before_check_temp(self):
        await self.wait_until_ready()  # wait until the bot logs in

    @check_disk.before_loop
    async def before_check_disk(self):
        await self.wait_until_ready()  # wait until the bot logs in


intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)

# Load token from file that contains only the token
path = os.path.join(Path.home(), "server_monitoring_discord_token.txt")
with open(path, 'r') as file:
    token = file.read()

client.run(token)
