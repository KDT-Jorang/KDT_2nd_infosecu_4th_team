import winreg
import datetime
import os

key = None

def filetime_to_dt(ft):
    microseconds = (ft //10) % 1000000
    seconds = (ft // 10000000) - 11644473600
    dt = datetime.datetime.utcfromtimestamp(seconds)
    dt=  dt.replace(microsecond = microseconds)
    korea_timezone = datetime.timezone(datetime.timedelta(hours=9))
    dt_korea = dt.astimezone(korea_timezone)

    return dt_korea

def check_software_values(hive, subkey_path, full_path):
    values = []
    try:
        with winreg.OpenKey(hive, subkey_path) as subkey:
            _, _, last_modified = winreg.QueryInfoKey(subkey) 
            index = 0
            while True:
                try:
                    value = winreg.EnumValue(subkey, index)
                    values.append(f"{full_path}\\{value[0]}: {value[1]}")
                    values.append(f"마지막 수정 시간: {filetime_to_dt(last_modified)}")
                    print(f"{full_path}\\{value[0]}: {value[1]}")
                    print(f"마지막 수정 시간: {filetime_to_dt(last_modified)}")
                    index += 1
                except OSError:
                    break
    except PermissionError:
        print(f"권한이 거부되었습니다: {full_path}")
    return values    

def check_software_key(hive, subkey_path="", root_key_name=''):
    full_path = f"{root_key_name}\\{subkey_path}".strip("\\")
    result = []
    try:
        with winreg.OpenKey(hive, subkey_path) as subkey:
            _, _, last_modified = winreg.QueryInfoKey(subkey)
            try:
                value, _ = winreg.QueryValueEx(subkey, "")
                result.append(f"{full_path}:{value}")
                print(f"{full_path}:{value}")
            except FileNotFoundError:
                pass
            index = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(subkey, index)
                    next_subkey_path = f"{subkey_path}\\{subkey_name}" if subkey_path else subkey_name
                    next_full_path = f"{full_path}\\{subkey_name}"
                    values = check_software_values(hive, next_subkey_path, next_full_path)
                    if values:
                        result.extend(values)
                    subkey_results = check_software_key(hive, next_subkey_path, root_key_name)
                    result.extend(subkey_results)
                    index += 1
                    
                except OSError:
                    break
    except PermissionError:
        print(f"권한이 거부되었습니다: {full_path}")

    return result

def save_results_to_file(result):
    artifact_path = os.path.join('./ARTIFACT/REGISTRY/', 'software_info.txt')
    os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
    
    with open(artifact_path, 'w', encoding='utf-8') as file:
        for value in result:
            file.write(str(value) + '\n')

def run():
    hive = winreg.HKEY_LOCAL_MACHINE
    subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
    results = check_software_key(hive, subkey)
    for result in results:
        print(result)
    save_results_to_file(results)
