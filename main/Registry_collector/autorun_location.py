import winreg
import os

def check_autorunP(hive, subkey):
    values = []
    try:
        with winreg.OpenKey(hive, subkey) as key:
            i = 0
            while True:
                try:
                    value_name, value_data, _ = winreg.EnumValue(key, i)
                    values.append(value_name)
                    i += 1
                except OSError:
                    break
    except FileNotFoundError:
        return "그런 파일 없어유"
    except Exception as e:
        return str(e)
    return values

def run():
    # 사용자 레지스트리 값 이름 추출
    hive = winreg.HKEY_CURRENT_USER
    subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
    value_names = check_autorunP(hive, subkey)

# 로컬 머신 레지스트리 값 이름 추출
    Explorer_hive = winreg.HKEY_LOCAL_MACHINE
    Explorer_subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
    Explorer_values = check_autorunP(Explorer_hive, Explorer_subkey)

# 사용자 레지스트리 시스템 실행 시 딱 한번만 실행
    once_hive = winreg.HKEY_CURRENT_USER
    once_subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"
    once_values = check_autorunP(once_hive, once_subkey)

#로컬머신 레지스트리 시스템 실행 시 딱 한번만 실행
    once_hive2 = winreg.HKEY_LOCAL_MACHINE
    once_subkey2 = r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"
    once_values2 = check_autorunP(once_hive2, once_subkey2)

    result = []

# 결과 출력
    print("HKEY_CURRENT_USER values:")
    for value in value_names:
        print(value)
        result.append(value)
    
    print("\nHKEY_LOCAL_MACHINE values:")
    for value in Explorer_values:
        print(value)
        result.append(value)
    
    print("\nHKEY_CURRENT_USER values:")
    for value in once_values:
        print(value)   
        result.append(value)
    
    print("\nHKEY_LOCAL_MACHINE values:")
    for value in once_values2:
        print(value)   
        result.append(value)

    save_results_to_file(result)

    return result

def save_results_to_file(result):
    artifact_path = os.path.join('./ARTIFACT/REGISTRY/', 'autorun_location.txt')
    os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
    
    with open(artifact_path, 'w', encoding='utf-8') as file:
        for results in result:
            file.write(str(results) + '\n')

