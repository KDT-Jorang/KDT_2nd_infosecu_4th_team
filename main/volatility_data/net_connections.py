import psutil
import socket


def run():
    # 사용 중인 모든 네트워크 연결 정보를 가져옵니다.
    connections = psutil.net_connections()
    connection_list = []

    # 각 연결에 대해 정보를 출력합니다.
    for conn in connections:
        laddr, raddr, status, pid = conn.laddr, conn.raddr, conn.status, conn.pid
        if raddr:
            connection_info = f"Local address: {laddr.ip}:{laddr.port}, Remote address: {raddr.ip}:{raddr.port}, Protocol: {'TCP' if conn.type == socket.SOCK_STREAM else 'UDP'}, Status: {status}, PID: {pid}"
        else:
            connection_info = f"Local address: {laddr.ip}:{laddr.port}, Protocol: {'TCP' if conn.type == socket.SOCK_STREAM else 'UDP'}, Status: {status}, PID: {pid}"
        connection_list.append(connection_info)
    return connection_list
