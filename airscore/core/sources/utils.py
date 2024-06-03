"""
Source utilities functions

Antonio Golfari - 2024
"""

from lxml import etree
from pathlib import Path

def read_xml_file(file: Path, clean_namespace: bool = True) -> "etree | None":
    """read the xml file"""
    try:
        tree = etree.parse(file)
    except TypeError:
        tree = etree.parse(file.as_posix())
    except etree.Error as e:
        print(f"XML Read Error: {e}")
        return None
    finally:
        root = tree.getroot()
        if clean_namespace:
            clean_xml_namespaces(root)
        return root

def clean_xml_namespaces(root):
    for element in root.getiterator():
        if isinstance(element, etree._Comment):
            continue
        element.tag = etree.QName(element).localname
    etree.cleanup_namespaces(root)


def get_time(string: str) -> int:
    print(string)
    if len(string) < 3:
        # sometimes this incredibly happens
        string += ':00'
    h, m = string.replace(';', ':').split(':')[:2]
    return int(h) * 3600 + int(m[:2]) * 60
