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

def collect_user_subkeys(hive, subkey_path):
    collected_user_data = []
    try:
        with winreg.OpenKey(hive, "") as key:  # HKEY_USERS 루트 키
            i = 0
            while True:
                try:
                    user_sid = winreg.EnumKey(key, i)
                    # 각 사용자의 SID를 포함하여 경로를 구성합니다.
                    full_subkey_path = f"{user_sid}\\{subkey_path}"
                    user_values = check_RDP(hive, full_subkey_path)
                    if user_values:
                        collected_user_data.extend(user_values)
                    i += 1
                except OSError:
                    break
    except Exception as e:
        print(f"오류 발생: {e}")
    return collected_user_data




def print_collected_data2(hive, subkey): # HKU 정보
    hive_name = get_hive_name(hive)
    collected_user_data = collect_user_subkeys(hive, subkey)
    result = []
    for subkey_path, value_name, value_data in collected_user_data:
        if isinstance(value_data, bytes): # 값 데이터가 파이트 형식이라면 16진수로 변환
            value_data_hex = value_data.hex()
            print(f"서브키: {subkey_path}, 값 이름: {value_name}, 값 데이터: {value_data_hex}")
            result.append(f"서브키: {subkey_path}, 값 이름: {value_name}, 값 데이터: {value_data_hex}")    
        else:
            print(f"서브키: {subkey_path}, 값 이름: {value_name}, 값 데이터: {value_data}")
            result.append(f"서브키: {subkey_path}, 값 이름: {value_name}, 값 데이터: {value_data}")

    save_results_to_file(result)
    return result

def save_results_to_file(result):
    artifact_path = os.path.join('./ARTIFACT/REGISTRY/', 'RDP_connect_user.txt')
    os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
    
    with open(artifact_path, 'w', encoding='utf-8') as file:
        for results in result:
            file.write(str(results) + '\n')


def get_hive_name(hive):
    if hive == winreg.HKEY_USERS:
        return "HKEY_USERS"
    elif hive == winreg.HKEY_LOCAL_MACHINE:
        return "HKEY_LOCAL_MACHINE"
    else:
        return f"UNKNOWN_HIVE ({hive})"


def run():
    hive = winreg.HKEY_USERS
    all_collected_data = []
    all_collected_data.append(print_collected_data2 (hive, r"SOFTWARE\Microsoft\Terminal Server Client\LocalDevices"))
