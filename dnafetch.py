# COPYRIGHT (C) akettunen
# claude made this script faster & did the logo coloring for me. its originally written by a human
import os 
import platform
import csv
import json
import shutil
import subprocess
import ctypes
import psutil
import re
import sys
import socket
import winreg
from concurrent.futures import ThreadPoolExecutor
os.system("")
#coloring made by AI cus im bad at it
TIFFANY = "\033[38;2;129;216;208m"
RED     = "\033[38;2;255;0;0m"
BLUE    = "\033[38;2;0;0;255m"
GREEN   = "\033[38;2;0;128;0m"
YELLOW  = "\033[38;2;255;200;0m"
RESET   = "\033[0m"
BASE_COLOR = {"A": GREEN, "T": RED, "G": YELLOW, "C": BLUE}
COMPLEMENT = {"A": "T", "T": "A", "G": "C", "C": "G"}
sequence = ["A", "G", "T", "C", "C"]
logo_lines = [
    "(==(     )==)",
    " `-.`. ,',-'",
    "    _,-'\"",
    " ,-',' `.`-.",
]
rung = 0
output = []
for i in range(4):
    for line in logo_lines:
        if line.startswith("(==("):
            left = sequence[rung % len(sequence)]
            right = COMPLEMENT[left]
            colored = (
                f"{TIFFANY}({BASE_COLOR[left]}=={TIFFANY}("
                f"     "
                f"){BASE_COLOR[right]}=={TIFFANY}){RESET}"
            )
            output.append(colored)
            rung += 1
        else:
            output.append(f"{TIFFANY}{line}{RESET}")
left = sequence[rung % len(sequence)]
right = COMPLEMENT[left]
output.append(
    f"{TIFFANY}({BASE_COLOR[left]}=={TIFFANY}("
    f"     "
    f"){BASE_COLOR[right]}=={TIFFANY}){RESET}"
)
def reg_value(path, name):
    try:
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
        v = winreg.QueryValueEx(k, name)[0]
        winreg.CloseKey(k)
        return str(v[0] if isinstance(v, list) else v).strip()
    except OSError:
        return "N/A"
#get info
#get os/platform
def get_os():
    return platform.system()
#get kernel
def get_kernel():
    return platform.version()
#get host name
def get_host_name():
    return platform.node()
#get username
def get_username():
    return os.getlogin()
#get uptime
lib = ctypes.windll.kernel32
t = lib.GetTickCount64()
t = int(str(t)[:-3])
mins, sec = divmod(t, 60)
hour, mins = divmod(mins, 60)
days, hour = divmod(hour, 24)
#get memory
def get_memory():
    return psutil.virtual_memory()
#get disk
def get_disk():
    return psutil.disk_usage(os.path.abspath(os.sep))
#get cpu
def get_cpu():
    return psutil.cpu_stats(),psutil.cpu_percent(interval=0.1),psutil.cpu_freq(),psutil.cpu_count(),psutil.cpu_times()
#get gpu nvidia
def get_gpu_nvidia():
    if not shutil.which("nvidia-smi"):
        return []

    fields = [
        "index",
        "name",
        "driver_version",
        "memory.total",
        "memory.used",
        "memory.free",
        "utilization.gpu",
        "temperature.gpu",
    ]
    command = [
        "nvidia-smi",
        f"--query-gpu={','.join(fields)}",
        "--format=csv,noheader,nounits",
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=5)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return []

    gpus = []
    for row in csv.reader(result.stdout.strip().splitlines()):
        gpus.append({field: value.strip() for field, value in zip(fields, row)})
    return gpus
#get gpu
def get_gpu():
    gpus = []
    try:
        base = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}")
    except OSError:
        return gpus
    i = 0
    while True:
        try:
            sub = winreg.EnumKey(base, i)
        except OSError:
            break
        i += 1
        try:
            k = winreg.OpenKey(base, sub)
            gpus.append({"Name": winreg.QueryValueEx(k, "DriverDesc")[0]})
            winreg.CloseKey(k)
        except OSError:
            pass
    return gpus
#get terminal
def get_terminal():
    if os.environ.get("WT_SESSION"):
        return "Windows Terminal"
    if os.environ.get("TERM_PROGRAM"):
        return os.environ["TERM_PROGRAM"]
    try:
        proc = psutil.Process(os.getpid()).parent()
        while proc:
            name = proc.name().lower()
            if name in ("windowsterminal.exe", "wezterm-gui.exe", "alacritty.exe", "code.exe", "conhost.exe", "openconsole.exe"):
                return proc.name()
            proc = proc.parent()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
    return "N/A"
#get ip
def get_ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "N/A"
    finally:
        s.close()
def get_ip_public():
    import urllib.request
    try:
        return urllib.request.urlopen("https://api.ipify.org", timeout=2).read().decode()
    except OSError:
        return "N/A"
#get bios
def get_bios():
    path = r"HARDWARE\DESCRIPTION\System\BIOS"
    return f"{reg_value(path, 'BIOSVendor')} {reg_value(path, 'BIOSVersion')}"
#get monitor info
class DEVMODE(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", ctypes.c_wchar * 32),
        ("dmSpecVersion", ctypes.c_ushort),
        ("dmDriverVersion", ctypes.c_ushort),
        ("dmSize", ctypes.c_ushort),
        ("dmDriverExtra", ctypes.c_ushort),
        ("dmFields", ctypes.c_ulong),
        ("dmPositionX", ctypes.c_long),
        ("dmPositionY", ctypes.c_long),
        ("dmDisplayOrientation", ctypes.c_ulong),
        ("dmDisplayFixedOutput", ctypes.c_ulong),
        ("dmColor", ctypes.c_short),
        ("dmDuplex", ctypes.c_short),
        ("dmYResolution", ctypes.c_short),
        ("dmTTOption", ctypes.c_short),
        ("dmCollate", ctypes.c_short),
        ("dmFormName", ctypes.c_wchar * 32),
        ("dmLogPixels", ctypes.c_ushort),
        ("dmBitsPerPel", ctypes.c_ulong),
        ("dmPelsWidth", ctypes.c_ulong),
        ("dmPelsHeight", ctypes.c_ulong),
        ("dmDisplayFlags", ctypes.c_ulong),
        ("dmDisplayFrequency", ctypes.c_ulong),
        ("dmICMMethod", ctypes.c_ulong),
        ("dmICMIntent", ctypes.c_ulong),
        ("dmMediaType", ctypes.c_ulong),
        ("dmDitherType", ctypes.c_ulong),
        ("dmReserved1", ctypes.c_ulong),
        ("dmReserved2", ctypes.c_ulong),
        ("dmPanningWidth", ctypes.c_ulong),
        ("dmPanningHeight", ctypes.c_ulong),
    ]
class DISPLAY_DEVICE(ctypes.Structure):
    _fields_ = [
        ("cb", ctypes.c_ulong),
        ("DeviceName", ctypes.c_wchar * 32),
        ("DeviceString", ctypes.c_wchar * 128),
        ("StateFlags", ctypes.c_ulong),
        ("DeviceID", ctypes.c_wchar * 128),
        ("DeviceKey", ctypes.c_wchar * 128),
    ]
def get_displays():
    user32 = ctypes.windll.user32
    displays = []
    i = 0
    while True:
        dev = DISPLAY_DEVICE()
        dev.cb = ctypes.sizeof(dev)
        if not user32.EnumDisplayDevicesW(None, i, ctypes.byref(dev), 0):
            break
        i += 1
        if not dev.StateFlags & 1:
            continue
        dm = DEVMODE()
        dm.dmSize = ctypes.sizeof(dm)
        if user32.EnumDisplaySettingsW(dev.DeviceName, -1, ctypes.byref(dm)):
            displays.append((dm.dmPelsWidth, dm.dmPelsHeight, dm.dmDisplayFrequency))
    return displays
#get monitor names
def get_monitor_names():
    cmd = ("Get-CimInstance -Namespace root\\wmi -ClassName WmiMonitorID | "
           "ForEach-Object { [System.Text.Encoding]::ASCII.GetString($_.UserFriendlyName).Trim([char]0) }")
    try:
        out = subprocess.check_output(["powershell", "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", cmd], text=True, timeout=10)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return []
    return [line.strip() for line in out.splitlines() if line.strip()]
#get motherboard
def get_motherboard():
    path = r"HARDWARE\DESCRIPTION\System\BIOS"
    return f"{reg_value(path, 'BaseBoardManufacturer')} {reg_value(path, 'BaseBoardProduct')}"
#get battery
def get_battery():
    try:
        battery = psutil.sensors_battery()
    except Exception:
        return "N/A"
    if battery is None:
        return "N/A"
    status = "Charging" if battery.power_plugged else "Discharging"
    return f"{battery.percent:.0f}% ({status})"

#print the info
pool = ThreadPoolExecutor(max_workers=6)
f_names = pool.submit(get_monitor_names)
f_nvidia = pool.submit(get_gpu_nvidia)
f_public = pool.submit(get_ip_public)
f_cpu = pool.submit(get_cpu)
f_terminal = pool.submit(get_terminal)

mem = get_memory()
disk = get_disk()
displays = get_displays()
cpu = f_cpu.result()
cpu_freq = f"{cpu[2].current / 1000:.2f}GHz" if cpu[2] else "N/A"

info = [
    f"{TIFFANY}OS:{RESET} {get_os()}",
    f"{TIFFANY}KERNEL:{RESET} {get_kernel()}",
    f"{TIFFANY}BIOS:{RESET} {get_bios()}",
    f"{TIFFANY}MOTHERBOARD:{RESET} {get_motherboard()}",
    f"{TIFFANY}HOST:{RESET} {get_host_name()}",
    f"{TIFFANY}USERNAME:{RESET} {get_username()}",
    f"{TIFFANY}UPTIME:{RESET} {days}d:{hour}h:{mins}m",
    f"{TIFFANY}MEMORY:{RESET} {mem.used / 1024**3:.1f}GB / {mem.total / 1024**3:.1f}GB ({mem.percent}%)",
    f"{TIFFANY}DISK:{RESET} {disk.used / 1024**3:.0f}GB / {disk.total / 1024**3:.0f}GB ({disk.percent}%)",
]
names = f_names.result()
for n, (w, h, hz) in enumerate(displays):
    name = names[n] if n < len(names) else "Unknown"
    info.append(f"{TIFFANY}DISPLAY:{RESET} {name} {w}x{h} @ {hz}Hz")
info.append(f"{TIFFANY}CPU:{RESET} {platform.processor()} ({cpu[3]} threads) @ {cpu_freq} {cpu[1]}%")

for gpu in get_gpu():
    info.append(f"{TIFFANY}GPU:{RESET} {gpu['Name']}")
for gpu in f_nvidia.result():
    info.append(
        f"{TIFFANY}VRAM:{RESET} {gpu['memory.used']}MiB / {gpu['memory.total']}MiB "
        f"({gpu['utilization.gpu']}%, {gpu['temperature.gpu']}°C)"
    )
info.append(f"{TIFFANY}TERMINAL:{RESET} {f_terminal.result()}")
info.append(f"{TIFFANY}IP LOCAL:{RESET} {get_ip_local()}")
info.append(f"{TIFFANY}IP PUBLIC:{RESET} {f_public.result()}")
battery = get_battery()
if battery:
    info.append(f"{TIFFANY}BATTERY:{RESET} {get_battery()}")
pool.shutdown()


#logo place
ansi = re.compile(r"\033\[[0-9;]*m")
logo_width = max(len(ansi.sub("", row)) for row in output)
offset = 0
info = [""] * offset + info

print()
for i in range(max(len(output), len(info))):
    row = output[i] if i < len(output) else ""
    pad = " " * (logo_width - len(ansi.sub("", row)) + 4)
    text = info[i] if i < len(info) else ""
    print(f"{row}{pad}{text}")
print()