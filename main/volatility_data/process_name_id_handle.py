import psutil
import os


def print_process_handles(process, denied_list):
    try:
        for handle in process.open_files():
            print(
                f"Process ID : {process.pid}, Process Name : {process.name()}, Handle : {handle}"
            )
    except psutil.AccessDenied:
        denied_list.append({"pid": process.pid, "name": process.name})


def run():
    # Get a list of all running processes
    processes = psutil.process_iter(["pid", "name"])
    access_denied_processes = []

    # Iterate over each process
    for process in processes:
        # Print information about the handles for each process
        print_process_handles(process, access_denied_processes)

    return {"Access denied for processes": access_denied_processes}
