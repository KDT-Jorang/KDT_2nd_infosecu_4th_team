import winreg
import os

key = None

def check_user_info(hive, subkey_path, value_name):
    try:
        with winreg.OpenKey(hive, subkey_path) as key:
            value, _ = winreg.QueryValueEx(key, value_name)
            return value
        
    except FileNotFoundError:                       
        return "그런 파일 없어유"
    except Exception as e:     # 이것도 다시 생각해 보자
        return str(e)



def collect_user_subkeys(hive, subkey_path):
    collected_user_data = {}
    try:
        with winreg.OpenKey(hive, "") as key:  # HKEY_USERS 루트 키
            i = 0
            while True:
                try:
                    user_sid = winreg.EnumKey(key, i)
                    full_subkey_path = f"{user_sid}\\{subkey_path}"
                    collected_user_data[user_sid] = {}
                    with winreg.OpenKey(hive, full_subkey_path) as subkey:
                        j = 0
                        while True:
                            try:
                                value_name, value_data, _ = winreg.EnumValue(subkey, j)
                                collected_user_data[user_sid][value_name] = value_data
                                j += 1
                            except OSError:
                                break
                    i += 1
                except OSError:
                    break
    except Exception as e:
        print(f"오류 발생: {e}")
    return collected_user_data


def run():
    result = []

    value_names = ["SelectedUserSID", "LastLoggedOnUserSID", "LastLoggedOnUser", "LastLoggedOnProvider", "IdleTime"]
    hive = winreg.HKEY_LOCAL_MACHINE
    subkey_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Authentication\LogonUI"
    for value_name in value_names:
        value = check_user_info(hive, subkey_path, value_name)
        result.append({value_name: value})
        print(f"{value_name}: {value}")

    auto_login_account_key = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
    auto_login_account = check_user_info(hive, auto_login_account_key, "DefaultUserName")
    result.append({"DefaultUserName": auto_login_account})


    user_info_hive = winreg.HKEY_USERS
    user_info_subkey = r'Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders'
    user_info_values = collect_user_subkeys(user_info_hive, user_info_subkey)
    result.append({"UserShellFolders": user_info_values})

    for sid, folders in user_info_values.items():
        print(f"SID: {sid}")
        for folder_name, folder_path in folders.items():
            print(f"  {folder_name}: {folder_path}")

    save_results_to_file(result)
    return result

def save_results_to_file(result):
    artifact_path = os.path.join('./ARTIFACT/REGISTRY/', 'user_info.txt')
    os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
    
    with open(artifact_path, 'w', encoding='utf-8') as file:
        for results in result:
            file.write(str(results) + '\n')
