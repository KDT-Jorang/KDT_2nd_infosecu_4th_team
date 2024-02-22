import winreg
import os

def check_RDP(hive, subkey_path):
    values = [] 
    try:
        with winreg.OpenKey(hive, subkey_path) as key:
            i = 0
            while True:
                try:
                    value_name, value_data, _ = winreg.EnumValue(key, i)
                    values.append((subkey_path, value_name, value_data))
                    i += 1
                except OSError:
                    break
    except FileNotFoundError:
        return [(subkey_path, "Error", "FileNotFoundError")]
    except Exception as e:
        return [(subkey_path, "Error", str(e))]
    return values



def collect_subkeys_and_values(hive, subkey_path):
    collected_data = check_RDP(hive, subkey_path)
    try:
        with winreg.OpenKey(hive, subkey_path) as key:
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i) #하위키 열거 후 모두 정보 수집
                    subkey_full_path = f"{subkey_path}\\{subkey_name}"
                    collected_data += collect_subkeys_and_values(hive, subkey_full_path)
                    i += 1
                except OSError:
                    break
    except FileNotFoundError:
        print(f"Subkey {subkey_path} not found.")           ######  RDP 해야한다  ######
    except Exception as e:                                  #유저의 RDP와 HKLM의 RDP가 다르다. 두 개를 모두 가져오자
        print(f"{subkey_path}에 없어!")
    
    return collected_data

def print_collected_data(hive, subkey): # HKLM 정보
    hive_name = get_hive_name(hive)
    collected_data = collect_subkeys_and_values(hive, subkey)
    result = []
    for subkey_path, value_name, value_data in collected_data:
        if isinstance(value_data, bytes):
            value_data_hex = value_data.hex()
            print(f"루트키 {get_hive_name(hive)} : 서브키: {subkey_path}, 값 이름: {value_name}, 값 데이터: {value_data_hex}")
            result.append(f"서브키: {subkey_path}, 값 이름: {value_name}, 값 데이터: {value_data_hex}")    
        else:
            print(f"루트키 {get_hive_name(hive)} : 서브키: {subkey_path}, 값 이름: {value_name}, 값 데이터: {value_data}")
            result.append(f"서브키: {subkey_path}, 값 이름: {value_name}, 값 데이터: {value_data}")    
    
    save_results_to_file(result)
    return result

def save_results_to_file(result):
    artifact_path = os.path.join('./ARTIFACT/REGISTRY/', 'RDP_connect.txt')
    os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
    
    with open(artifact_path, 'w', encoding='utf-8') as file:
        for results in result:
            file.write(str(results) + '\n')

def print_collected_data2(hive, subkey): # HKU 정보
    hive_name = get_hive_name(hive)
    collected_user_data = collect_subkeys_and_values(hive, subkey)
    result = []
    for subkey_path, value_name, value_data in collected_user_data:
        if isinstance(value_data, bytes):
            value_data_hex = value_data.hex()
            print(f"루트키 {get_hive_name(hive)} : 서브키: {subkey_path}, 값 이름: {value_name}, 값 데이터: {value_data_hex}")
            result.append(f"서브키: {subkey_path}, 값 이름: {value_name}, 값 데이터: {value_data_hex}")    
        else:
            print(f"루트키 {get_hive_name(hive)} : 서브키: {subkey_path}, 값 이름: {value_name}, 값 데이터: {value_data}")
            result.append(f"서브키: {subkey_path}, 값 이름: {value_name}, 값 데이터: {value_data}")
    return result


def get_hive_name(hive):
    if hive == winreg.HKEY_CURRENT_USER:
        return "HKEY_CURRENT_USER"
    elif hive == winreg.HKEY_LOCAL_MACHINE:
        return "HKEY_LOCAL_MACHINE"
    else:
        return f"UNKNOWN_HIVE ({hive})"

def run():
    hive = winreg.HKEY_CURRENT_USER
    HKLM_hive = winreg.HKEY_LOCAL_MACHINE
    all_collected_data = []
    all_collected_data.extend(print_collected_data (HKLM_hive, r"SOFTWARE\Microsoft\Terminal Server Client"))
    all_collected_data.extend(print_collected_data2 (hive, r"SOFTWARE\Microsoft\Terminal Server Client"))

