import os
import winreg

# 값을 출력시키는 말단 수집 부서
def collect_values(hive, subkey_path):
    values = []
    try:
        with winreg.OpenKey(hive, subkey_path) as key: # key에 변수값들을 저장
            i = 0
            while True:
                try:                                            #키에 저장된게 i 번째 순서로 저장된다. 
                    value_name, value_data, _ = winreg.EnumValue(key, i) #3번째 값인 데이터 타입은 "_"로 무시한다.
                    # subkey_path를 포함하여 튜플로 값을 저장
                    values.append((subkey_path, value_name, value_data)) #원하는 값인 경로, 값 이름, 값 데이터로 저장시킨 모습
                    i += 1
                except OSError:
                    break
    except FileNotFoundError:
        print(f"Subkey {subkey_path} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return values # 현재 경로, 값 이름, 값 데이터까지 들어가 있음. = 이하 "개미"라 부르겠다.

# 서브키를 수집해 말단에게 값 찾아오라고 시키는 말단 2부
def collect_subkeys_and_values(hive, subkey_path):
    collected_data = collect_values(hive, subkey_path) # 개미가 들어있다.
    try:
        with winreg.OpenKey(hive, subkey_path) as key: # 같은 경로를 연다.
            i = 0
            while True:    
                try:
                    subkey_name = winreg.EnumKey(key, i) #  키 이름을 순서대로 열거하고 서브키네임에 값이 들어감 하나씩!
                    subkey_full_path = f"{subkey_path}\\{subkey_name}"  # 경로가 하나씩 추가되며 없을 때 까지 경로가 추가된다.
                    collected_data += collect_subkeys_and_values(hive, subkey_full_path) #함수가 재호출 되면서 collect_value를 재호출 = value 값(이름, 데이터)도 새롭게 수집한다.                        
                    i += 1 # 순차적으로 실행
                except OSError:
                    break
    except FileNotFoundError:
        print(f"Subkey {subkey_path} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return collected_data # 모든 하위키와 데이터들이 들어간다. = "슈퍼개미"

#지휘부
def print_collected_data(hive, subkey):
    result = []
    collected_data = collect_subkeys_and_values(hive, subkey) #하위 경로가 들어가 있음.
    for subkey_path, value_name, value_data in collected_data: # 슈퍼개미에서 원하는 값만 봅는다.
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
    artifact_path = os.path.join('./ARTIFACT/REGISTRY/', 'USB_info.txt')
    os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
    
    with open(artifact_path, 'w', encoding='utf-8') as file:
        for results in result:
            file.write(str(results) + '\n')   
def run():
    hive = winreg.HKEY_LOCAL_MACHINE
    all_collected_data = []
    all_collected_data.extend(print_collected_data(hive, r"SYSTEM\ControlSet001\Enum\USB"))
    all_collected_data.extend(print_collected_data(hive, r"SOFTWARE\Microsoft\Windows Portable Devices\Devices"))

