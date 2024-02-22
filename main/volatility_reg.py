
from Registry_collector import autorun_location, LNK_info, MRU_List, network_interface, prefetch_info, RDP_CONNEC, RDP_connect_user_info, shutdowntime, software_info, system_info,TimeZone, USB_info, user_info, USER_USB


def volatility_reg_collect():
    autorun_location.run()
    LNK_info.run()
    MRU_List.run()
    network_interface.run()
    prefetch_info.run()
    RDP_CONNEC.run()
    RDP_connect_user_info.run()
    shutdowntime.run()
    software_info.run()
    system_info.run()
    USB_info.run()
    user_info.run()
    USER_USB.run()


if __name__=="__main__":
    volatility_reg_collect()