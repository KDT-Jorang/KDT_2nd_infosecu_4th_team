import psutil


def get_startup_processes():
    processes = []
    for proc in psutil.process_iter(["pid", "name", "create_time"]):
        try:
            if proc.info["create_time"] < psutil.boot_time():
                processes.append(proc.info)
        except Exception as e:
            print(e)
    return processes


def run():
    startup_processes = get_startup_processes()
    process_list = []
    for process in startup_processes:
        process_info = f'PID: {process["pid"]}, Name: {process["name"]}, Created at: {process["create_time"]}'
        process_list.append(process_info)
    print(process_list)
    return process_list

run()