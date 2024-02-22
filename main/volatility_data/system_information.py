import platform
import os
import socket
import psutil
import wmi
import subprocess
from datetime import datetime


def run():
    # Create a dictionary to store all the information
    system_info = {}

    # 시스템 이름 및 버전
    system_info["시스템 이름 및 버전"] = (platform.system(), platform.release())

    # 현재 시스템 사용자
    system_info["현재 시스템 사용자"] = os.getlogin()

    # 시스템 환경
    system_info["시스템 환경"] = dict(os.environ)

    # 디스크 볼륨 정보
    system_info["디스크 볼륨 정보"] = [
        str(partition) for partition in psutil.disk_partitions()
    ]

    w = wmi.WMI()

    # 설치된 소프트웨어 정보
    system_info["설치된 소프트웨어 정보"] = [
        (software.Caption, software.Version) for software in w.Win32_Product()
    ]

    # 핫픽스 정보
    system_info["핫픽스 정보"] = [
        (hotfix.HotFixID, hotfix.Description)
        for hotfix in w.Win32_QuickFixEngineering()
    ]

    # 시스템에 적용된 서비스 설정 정보
    system_info["서비스 정보"] = [
        (service.Caption, service.State) for service in w.Win32_Service()
    ]

    # 설치 날짜, 시리얼 정보, 윈도우 업데이트 정보는 레지스트리나 시스템 명령을 사용하여 수집
    install_date = subprocess.check_output("wmic os get installdate", shell=True)
    system_info["설치 날짜"] = install_date.decode("utf-8")

    serial_info = subprocess.check_output("wmic bios get serialnumber", shell=True)
    system_info["시리얼 정보"] = serial_info.decode("utf-8")

    windows_update_info = subprocess.check_output("wmic qfe", shell=True)
    system_info["윈도우 업데이트 정보"] = windows_update_info.decode("utf-8")

    return system_info


if __name__ == "__main__":
    # Get all system information
    print(run())
