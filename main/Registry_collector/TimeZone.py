import winreg
key = None
def check_timezone (hive, subkey, value_name):
    
    try:
        with winreg.OpenKey(hive, subkey) as key:
            value, _ =winreg.QueryValueEx(key, value_name)
            return value
    except FileNotFoundError:
        return "그런 파일 없어유"
    except Exception as e:
        return str(e)   

def run():
    value_names = ["TimeZoneKeyName", "StandardName", "StandardBias", "DaylightStart", "DaylightName", "DaylightBias", "Bias", "ActiveTimeBias"]
    hive = winreg.HKEY_LOCAL_MACHINE
    subkey = r"SYSTEM\CurrentControlSet\Control\TimeZoneInformation"

    values = [f"{value_name}: {check_timezone(hive, subkey, value_name)}" for value_name in value_names]

    for value in values:
        print(value)

    