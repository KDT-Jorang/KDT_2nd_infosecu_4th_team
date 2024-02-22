import winreg
import os

# 마지막 연결시간
def enumerate_subkeys(hive, subkey_path):
    try:
        with winreg.OpenKey(hive, subkey_path) as key: #레지스트리 오픈
            subkeys = []
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i) #하위키값 받음
                    subkeys.append(subkey_name) #하위키값 리스트에 추가
                    i += 1
                except OSError:
                    break
            return subkeys
    except FileNotFoundError:
        return []

def enumerate_values(hive, subkey_path):
    try:
        with winreg.OpenKey(hive, subkey_path) as key:
            values = []
            i = 0
            while True:
                try:
                    value = winreg.EnumValue(key, i) #값이름, 값데이터, 값 타입 저장
                    values.append(value)  # (value_name, value_data, value_type)
                    i += 1
                except OSError:
                    break
            return values
    except FileNotFoundError:
        return []

def check_usb_info(hive):
    result = []
    with winreg.OpenKey(hive, "") as user_key: #서브키에 대한 자유도
        i = 0                                   #HKU 특성 상 여러 유저 아이디 존재하기에 이렇게 함.
        while True:
            try:
                user_sid = winreg.EnumKey(user_key, i) 
                subkey_path = f"{user_sid}\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\MountPoints2"
                mountpoints = enumerate_subkeys(hive, subkey_path) #1차 키 열거 후 값 수집
                for mountpoint in mountpoints:
                    mountpoint_path = f"{subkey_path}\\{mountpoint}"
                    print(f"User SID {user_sid}, Mountpoint: {mountpoint}")
                    mountpoint_values = enumerate_values(hive, mountpoint_path)
                    result.append(f"User SID {user_sid}, Mountpoint: {mountpoint}")
                    for value_name, value_data, value_type in mountpoint_values:
                        print(f"  Value Name: {value_name}, Value Data: {value_data}, Value Type: {value_type}")
                        result.append(f"  Value Name: {value_name}, Value Data: {value_data}, Value Type: {value_type}")
                    if mountpoint.lower() == "cpc": # CPC 값 있으면 
                        cpc_path = f"{mountpoint_path}\\Volume"# ~~ \\CPC \\ Volume 경로 추가
                        cpc_volumes = enumerate_subkeys(hive, cpc_path)
                        for cpc_volume in cpc_volumes:
                            cpc_volume_path = f"{cpc_path}\\{cpc_volume}"
                            cpc_volume_values = enumerate_values(hive, cpc_volume_path)
                            for value_name, value_data, value_type in cpc_volume_values:
                                print(f"  CPC Volume: {cpc_volume}, Value Name: {value_name}, Value Data: {value_data}, Value Type: {value_type}")
                                result.append(f"  CPC Volume: {cpc_volume}, Value Name: {value_name}, Value Data: {value_data}, Value Type: {value_type}")
                i += 1

                
            except OSError:
                break
    save_results_to_file(result)
    return result

def save_results_to_file(result):
    artifact_path = os.path.join('./ARTIFACT/REGISTRY/', 'USER_USB.txt')
    os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
    
    with open(artifact_path, 'w', encoding='utf-8') as file:
        for results in result:
            file.write(str(results) + '\n')          
def run():
    hive = winreg.HKEY_USERS
    check_usb_info(hive)
