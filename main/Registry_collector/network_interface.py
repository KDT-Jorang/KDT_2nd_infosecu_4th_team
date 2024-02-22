import winreg
import os

def check_net_interface (hive, subkey):
    values = [] 
    try:
        with winreg.OpenKey(hive, subkey)as key :
            i = 0
            while True:
                try:
                    value_name, value_data, value_type = winreg.EnumValue(key, i)
                    values.append((value_name,value_data,value_type))
                    i += 1
                except OSError:
                    break
    except FileNotFoundError:
        return "그런 파일 없어유"
    except Exception as e:
        return str(e)
    return values


def collect_subkeys_and_values(hive, subkey_path):
    collected_data = check_net_interface(hive, subkey_path)
    try:
        with winreg.OpenKey(hive, subkey_path) as key:
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey_full_path = f"{subkey_path}\\{subkey_name}"
                    collected_data += collect_subkeys_and_values(hive, subkey_full_path)
                    i += 1
                except OSError:
                    break
    except FileNotFoundError:
        print(f"Subkey {subkey_path} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return collected_data

def print_collected_data(hive, subkey):
    result = []
    collected_data = collect_subkeys_and_values(hive, subkey)
    for subkey_path, value_name, value_data in collected_data:
        if isinstance(value_data, bytes):
            value_data_hex=value_data.hex()
            print(f"서브키 : {subkey_path}, 값 이름 {value_name}, 값 데이터 {value_data_hex}")
            result.append(f"서브키: {subkey_path}, 값 이름: {value_name}, 값 데이터: {value_data_hex}")    
        else:
            print(f"서브키 : {subkey_path}, 값 이름 {value_name}, 값 데이터 {value_data}")
            result.append(f"서브키: {subkey_path}, 값 이름: {value_name}, 값 데이터: {value_data}")    
    save_results_to_file(result)
    return result

def save_results_to_file(result):
    artifact_path = os.path.join('./ARTIFACT/REGISTRY/', 'network_interface.txt')
    os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
    
    with open(artifact_path, 'w', encoding='utf-8') as file:
        for results in result:
            file.write(str(results) + '\n')
def run():
    hive = winreg.HKEY_LOCAL_MACHINE
    all_collected_data = []
    all_collected_data.extend(print_collected_data(hive, r"SYSTEM\ControlSet001\Services\Tcpip\Parameters\Interfaces"))
    all_collected_data.extend(print_collected_data(hive, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList\Signatures\Unmanaged"))





