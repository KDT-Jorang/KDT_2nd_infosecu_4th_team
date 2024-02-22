import winreg
key = None
def check_auto_format (hive, subkey, value_name):
    
    try:
        with winreg.OpenKey(hive, subkey) as key:
            value, _ =winreg.QueryValueEx(key, value_name)
            return value
    except FileNotFoundError:
        return "설정되지 않음"
    except Exception as e:
        return str(e)   
def run():
    value_names = ["clear page file at shutdown"]
    hive = winreg.HKEY_LOCAL_MACHINE
    subkey = r"SYSTEM\ControlSet001\Control\Session Manager\Memory Management"

    values = [f"{value_name}:{check_auto_format(hive, subkey, value_name)}" for value_name in value_names]

    for value in values :
        print(value)
