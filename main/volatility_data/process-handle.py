import psutil


def get_process_handles(process):
    try:
        # Get the list of handles for the process
        handles = process.open_files() + process.connections()

        # Iterate over each handle
        for handle in handles:
            # Check if the handle has a path attribute (file)
            if "path" in handle._fields:
                print(f"Handle: {handle.fd} - File ({handle.path})")
            # Else it might be a connection
            else:
                print(f"Handle: {handle.fd} - Connection ({handle.laddr})")
    except psutil.AccessDenied:
        return False

    return True


def run():
    # Get a list of all running processes
    processes = psutil.process_iter(["pid", "name"])

    failed_processes = []

    # Iterate over each process
    for process in processes:
        # Get and print the list of handles
        if not get_process_handles(process):
            failed_processes.append(f"{process.info['pid']} - {process.info['name']}")

    # Print the processes for which access to handles failed
    if failed_processes:
        print("\n핸들 정보를 가져오는 데 실패한 프로세스:")
        for proc in failed_processes:
            print(proc)

    return failed_processes


if __name__ == "__main__":
    # Get all process handles
    run()
