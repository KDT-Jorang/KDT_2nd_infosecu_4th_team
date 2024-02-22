import winreg
import os

key = None


def check_system_info(hive, subkey, value_name):
    try:
        with winreg.OpenKey(hive, subkey) as key:
            value, _ = winreg.QueryValueEx(key, value_name)
            return value
        
    except FileNotFoundError:
        return "그런 파일 없어유"
    except Exception as e:
        return str(e)

def run():
    
    result = []

    value_names = ["ProductName", "RegisteredOwner", "ProductId", "BuildLabEx", "InstallDate", "SystemRoot", "InstallDate", ]
    hive = winreg.HKEY_LOCAL_MACHINE
    subkey = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"

    for value_name in value_names:
        value_info = f"{value_name}: {check_system_info(hive, subkey, value_name)}"
        print(value_info)
        result.append(value_info)
    
    computer_name_key = r"SYSTEM\ControlSet001\Control\ComputerName\ActiveComputerName"
    computer_name = check_system_info(hive, computer_name_key, "ComputerName")
    computer_name_info = f"ComputerName: {computer_name}"
    print(computer_name_info)
    result.append(computer_name_info)

    save_results_to_file(result)
    return result

def save_results_to_file(result):
    artifact_path = os.path.join('./ARTIFACT/REGISTRY/', 'system_info.txt')
    os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
    
    with open(artifact_path, 'w', encoding='utf-8') as file:
        for results in result:
            file.write(str(results) + '\n')
