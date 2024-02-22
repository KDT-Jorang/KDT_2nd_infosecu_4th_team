import psutil


def run():
    info_list = []

    # 네트워크 카드 정보 추출
    info_list.append("Network Cards Information:")
    for name, snics in psutil.net_if_addrs().items():
        for snic in snics:
            info_list.append(
                f"{name}: {snic.family}, {snic.address}, {snic.netmask}, {snic.broadcast}"
            )

    # 라우팅 테이블 정보 추출
    info_list.append("\nRouting Table:")
    for item in psutil.net_connections(kind="inet"):
        info_list.append(f"{item.laddr}, {item.raddr}, {item.status}")

    # ARP 테이블 정보 추출
    info_list.append("\nARP Table:")
    for item in psutil.net_if_stats().items():
        info_list.append(str(item))

    return info_list
