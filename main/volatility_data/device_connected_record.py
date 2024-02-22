import wmi


def run():
    c = wmi.WMI()
    device_list = []
    for device in c.Win32_DiskDrive():
        device_info = f"Device Model: {device.Model}, Status: {device.Status}"
        device_list.append(device_info)
    print(device_list)
    return device_list

run()

