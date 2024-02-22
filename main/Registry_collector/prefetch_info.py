import winreg
import os


def collect_values(hive, subkey_path):
    values = []
    try:
        with winreg.OpenKey(hive, subkey_path) as key: # key에 변수값들을 저장
            i = 0
            while True:
                try:                                            #키에 저장된게 i 번째 순서로 저장된다. 
                    value_name, value_data, value_type = winreg.EnumValue(key, i) 
                    # subkey_path를 포함하여 튜플로 값을 저장
                    values.append((subkey_path, value_name, value_data, value_type)) #원하는 값인 경로, 값 이름, 값 데이터로 저장시킨 모습
                    i += 1
                except OSError:
                    break
    except FileNotFoundError:
        print(f"Subkey {subkey_path} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    save_results_to_file(values)
    return values # 현재 경로, 값 이름, 값 데이터까지 들어가 있음. = 이하 "개미"라 부르겠다.
  
def save_results_to_file(values):
    artifact_path = os.path.join('./ARTIFACT/REGISTRY/', 'prefetch_artifact.txt')
    os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
    
    with open(artifact_path, 'w', encoding='utf-8') as file:
        for result in values:
            file.write(str(result) + '\n')

def run():
    result = []
    hive = winreg.HKEY_LOCAL_MACHINE
    subkey_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters"

    collected_values = collect_values(hive, subkey_path)

    for value in collected_values:
        print(value)
        result.append(value)
    return result