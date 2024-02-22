
import winreg
from datetime import datetime, timedelta, timezone
import os

def run():
    key = None
    result = []
    try:
        
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\ControlSet001\Control\Windows")

        value, regtype = winreg.QueryValueEx(key, "ShutdownTime")
    
        filetime = int.from_bytes(value, 'little')

        unix_time = filetime // 10**7 - 11644473600

        shutdown_time_utc = datetime.fromtimestamp(unix_time, timezone.utc)
        shutdown_time_korea = shutdown_time_utc + timedelta(hours=9)
        
        result.append(f"Shutdown time :{shutdown_time_korea}")
        print(f"Shutdown time :{shutdown_time_korea}")
        print(f'Type : {regtype}')
        
        save_results_to_file(result)
        return result
    
    except FileNotFoundError:
        print("그런 파일 없음")
    except Exception as e:
        print(f"오류발생:{e}")

    finally:
        if key is not None :
            winreg.CloseKey(key)
    
    

def save_results_to_file(result):
    artifact_path = os.path.join('./ARTIFACT/REGISTRY/', 'shutdowntime.txt')
    os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
    
    with open(artifact_path, 'w', encoding='utf-8') as file:
        for results in result:
            file.write(str(results) + '\n')