import os
import subprocess
import random
import sys

import psutil
import requests
import regex
from pefile import lru_cache
from regexfilesearch import regex_filesearch, get_all_files_in_folders_with_subdir_limit
from collections import deque
from repeatdecorator import repeat_func
from kthread_sleep import sleep
import keyboard

avastcon = sys.modules[__name__]
avastcon.allusedips = ["0.0.0.0"]
avastcon.allprocs = deque([], 1)
avastcon.clearips = 600
avastcon.myip = None
avastcon.get_new_ip_now = False
avastcon.kill_em_all_now = False
avastcon.sleeptime_reconnect = 3


@lru_cache
def get_server_from_log(path=r"C:\ProgramData\Avast Software\SecureLine VPN"):

    ipr = r"""\((\d+\.\d+\.\d+\.\d+)(:?.{0,20})?\)"""
    alf = get_all_files_in_folders_with_subdir_limit(folders=path, maxsubdirs=10)
    alf = [x for x in alf if str(x).lower().endswith(".log")]
    df = regex_filesearch(
        files=alf,
        regexpressions=[ipr],
        with_context=True,
        chunksize=8192,
        flags=regex.IGNORECASE,
    )
    df = df.loc[
        df.aa_result_utf8.str.contains(
            r"""\b(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[1-9])\.)(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.){2}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\b""",
            na=False,
            regex=True,
        )
    ]

    df.aa_full_match = (
        df.aa_full_match.astype("string")
        .str.replace(r"\\r\\n", " ", regex=True)
        .str.extract(r"Newly resolved server is\s+([^\s\r\n]+)")
    )
    df = df.dropna(subset="aa_full_match")
    df = df.dropna(subset="aa_result_utf8")
    df = df.loc[~df.aa_result_utf8.str.contains("(", regex=False, na=False)]
    df = df.drop_duplicates(subset=["aa_full_match", "aa_result_utf8"])
    serv = list(zip(df.aa_full_match.__array__(), df.aa_result_utf8.__array__()))
    return serv


ipr = r"""\b(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[1-9])\.)(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.){2}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\b"""
ipaddrg = regex.compile(ipr)


def get_public_ip():
    ipcheckeraddress = "https://api.ipify.org"
    myipaddress = requests.get(ipcheckeraddress).text.strip()
    checkreg = ipaddrg.findall(myipaddress)
    if not checkreg:
        return "0.0.0.0"
    else:
        return checkreg[0]


@repeat_func(
    repeat_time=avastcon.clearips,
    variablename="represults",
    activate_lock=True,
    ignore_exceptions=True,
    exception_value="EXCEPTION",
    max_len_allresults=None,
    print_results=False,
    print_exceptions=True,
    execution_limit=-1,
    max_concurrent_threads=-1,
    check_max_threads_every_n_seconds=0.015,
)
def clear_proxies():
    print(avastcon.allusedips)
    avastcon.allusedips = ["0.0.0.0", avastcon.myip]
    print(avastcon.allusedips)


def get_new_ip(
    dns="100.122.0.0",
    path_app=r"C:\Program Files\Avast Software\SecureLine VPN",
    path_data=r"C:\ProgramData\Avast Software\SecureLine VPN",
):

    path_app = os.path.normpath(path_app)
    path_data = os.path.normpath(path_data)
    allavastips = get_server_from_log(path=path_data)
    newip = "0.0.0.0"

    for pr in avastcon.allprocs:
        try:
            pr.kill()
        except Exception:
            continue
    while newip in avastcon.allusedips:
        try:
            gw, ipw = random.choice(allavastips)
            avastexecute = rf'''"{path_app}\Mimic\mimictun.exe" -server {ipw}:443 -ca "{path_data}\SecureLine\ca.crt.pem" -credentials "{path_data}\SecureLine\auth.mimic" -dns {dns} -tlsdomain "{gw}" -connect-attempts 1 -connect-timeout 1s -reconnect-delay 0 -reconnect-delay-rnd 0 -reconnect-delay-max 0 -reconnect-delay-factor 0.1 -device "SecureLine"'''

            avastcon.allprocs.append(subprocess.Popen(avastexecute))
            sleep(avastcon.sleeptime_reconnect)
            newip = get_public_ip()
            if avastcon.myip == newip:
                try:
                    kill_em_all(killscript=False)
                    sleep(avastcon.sleeptime_reconnect)
                    continue
                except Exception as fe:
                    print(fe)
                    continue
            if newip not in avastcon.allusedips:
                print(f"using: {newip}")
                avastcon.allusedips.append(newip)
                return newip
            else:
                kill_em_all(killscript=False)
                sleep(avastcon.sleeptime_reconnect)
                continue
        except Exception as fe:
            kill_em_all(killscript=False)
            sleep(avastcon.sleeptime_reconnect)


def change_server():
    avastcon.get_new_ip_now = True


def change_kill_em_all():
    avastcon.kill_em_all_now = True


def kill_em_all(killscript=True):
    for p in psutil.process_iter():
        if p.name().lower() == "mimictun.exe":
            try:
                p.kill()
            except Exception as fe:
                print(fe)
                continue
    for pr in avastcon.allprocs:
        try:
            pr.kill()
        except Exception:
            continue
    if killscript:
        os._exit(0)


def start_avast(
    sleeptime_reconnect=3,
    hotkey_change="ctrl+alt+m",
    hotkey_stop="ctrl+alt+n",
    dns="100.122.0.0",
    rotate_server_each_n_seconds=30,
    clear_used_ips_after_n_seconds=900,
    path_app=r"C:\Program Files\Avast Software\SecureLine VPN",
    path_data=r"C:\ProgramData\Avast Software\SecureLine VPN",
):
    avastcon.sleeptime_reconnect = sleeptime_reconnect
    for p in psutil.process_iter():
        if p.name().lower() == "mimictun.exe":
            try:
                p.kill()
            except Exception as fe:
                print(fe)
                continue

    avastcon.clearips = clear_used_ips_after_n_seconds
    clear_proxies()
    keyboard.add_hotkey(hotkey_change, lambda: change_server())
    keyboard.add_hotkey(hotkey_stop, lambda: change_kill_em_all())
    while True:
        totalsleeptime = 0
        get_new_ip(dns=dns, path_app=path_app, path_data=path_data)
        avastcon.get_new_ip_now = False
        while True:
            sleep(1)
            totalsleeptime += 1
            if totalsleeptime >= rotate_server_each_n_seconds:
                break
            if avastcon.get_new_ip_now:
                break
            if avastcon.kill_em_all_now:
                kill_em_all()


for p in psutil.process_iter():
    if p.name().lower() == "mimictun.exe":
        try:
            p.kill()
        except Exception as fe:
            print(fe)
            continue
avastcon.myip = get_public_ip()
avastcon.allusedips.append(avastcon.myip)
