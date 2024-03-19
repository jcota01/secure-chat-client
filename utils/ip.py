import re
from netifaces import interfaces, ifaddresses, AF_INET

"""
We use fixed32 to represent IPv4 addresses on the server as an IPv4 address is made of 4 octets (bytes).
This allows for greater performance and scalability on the server, with only a little overhead in each client. 
"""
def ipv4_to_fixed32(ipv4: str) -> int:
    assert re.fullmatch(
        r"^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])$",
        ipv4)
    octets = ipv4.split(".")
    return (int(octets[0]) << (8 * 3)) | (int(octets[1]) << (8 * 2)) | (int(octets[2]) << (8 * 1)) | (
            int(octets[3]) << (8 * 0))


def fixed32_to_ipv4(fixed32: int) -> str:
    assert 0 <= fixed32 <= 2 ** 32
    return ".".join(
        [str((fixed32 >> (8 * 3)) & 0xff), str((fixed32 >> (8 * 2)) & 0xff), str((fixed32 >> (8 * 1)) & 0xff),
         str((fixed32 >> (8 * 0)) & 0xff)])


# this code is from https://stackoverflow.com/a/274644
def get_local_ipv4_addresses():
    ip_list = []
    for interface in interfaces():
        for link in ifaddresses(interface)[AF_INET]:
            ip_list.append(link['addr'])
    return ip_list
