import xml.etree.ElementTree as ET
from point import Point6D

def point_from_state(xml_bytes: bytes, name="Touchup"):
    root = ET.fromstring(xml_bytes.decode())
    cart = root.find(".//Cartesian")
    return Point6D(
        name=name,
        x=float(cart.get("X")),
        y=float(cart.get("Y")),
        z=float(cart.get("Z")),
        a=float(cart.get("A")),
        b=float(cart.get("B")),
        c=float(cart.get("C")),
    )
