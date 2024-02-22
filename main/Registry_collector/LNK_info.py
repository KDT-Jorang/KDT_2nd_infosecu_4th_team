import winreg
import os


def check_LNK(hive, subkey_path):
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
    collected_data = check_LNK(hive, subkey_path)
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
        print(f"Subkey {subkey_path} not found.")          
    except Exception as e:                                  
        print(f"{subkey_path}에 없어!")
    save_results_to_file(collected_data)

    return collected_data

def save_results_to_file(collected_data):
    artifact_path = os.path.join('./ARTIFACT/REGISTRY/', 'LNK_artifact.txt')
    os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
    
    with open(artifact_path, 'w', encoding='utf-8') as file:
        for result in collected_data:
            file.write(str(result) + '\n')



def print_collected_data2(hive, subkey): # HKU 정보
    hive_name = title(hive)
    collected_user_data = collect_subkeys_and_values(hive, subkey)
    for subkey_path, value_name, value_data in collected_user_data:
        if isinstance(value_data, bytes):
            value_data_hex = value_data.hex()
            print(f"루트키 {title(hive)} : 서브키: {subkey_path}, 값 이름: {value_name}, 값 데이터: {value_data_hex}")
        else:
            print(f"루트키 {title(hive)} : 서브키: {subkey_path}, 값 이름: {value_name}, 값 데이터: {value_data}")

def title (hive):
    if hive == winreg.HKEY_CURRENT_USER:
        return "HKEY_CURRENT_USER"

def run():
    hive = winreg.HKEY_CURRENT_USER
    print_collected_data2 (hive, r"Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist")

