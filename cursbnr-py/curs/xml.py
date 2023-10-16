from xml.sax.handler import ContentHandler
from xml.sax import parse as xml_parse
from xml.sax.saxutils import escape
from curs.types import CursMap

import datetime as dt


def escape_attr(data):
    entities = {
        "\n": "&#10;",
        "\r": "&#13;",
        "\t": "&#9;",
        "'": "&apos;",
        '"': "&quot;",
    }
    return escape(data, entities)


class _BnrXmlHandler(ContentHandler):
    def __init__(self, map: CursMap) -> None:
        super().__init__()
        assert isinstance(map, CursMap)
        self._map = map
        self._stack = []
        self._currency = None

    def startElement(self, name, attrs):
        stack = self._stack
        stack.append(name)

        if stack == ["values", "currency"]:
            self._currency = attrs["name"]

        elif stack == ["values", "currency", "rate"]:
            self._map.put_value(attrs["date"], self._currency, attrs.get("value", None))

    def endElement(self, name):
        stack = self._stack
        if stack == ["values", "currency"]:
            self._currency = None

        stack.pop()

    pass


def parse_bnr_xml(file) -> CursMap:
    map = CursMap()
    xml_parse(file, _BnrXmlHandler(map))
    return map


def write_bnr_xml(map: CursMap, file):
    with open(file, "w", encoding="utf-8", newline="\r\n") as f:
        f.write("<?xml version='1.0' encoding='utf-8'?>\n")
        f.write("<values>\n")
        for currency in sorted(map.keys()):
            f.write(f"\t<currency name='{escape_attr(currency)}'>\n")
            for date, value in sorted(map[currency].items()):
                assert isinstance(date, dt.date)
                date_iso = date.isoformat()
                if value is not None:
                    value = (
                        "{:.6g}".format(value)
                        if isinstance(value, float)
                        else str(int(value))
                    )
                    f.write(
                        f"\t\t<rate date='{escape_attr(date_iso)}' value='{escape_attr(value)}' />\n"
                    )
                else:
                    f.write(f"\t\t<rate date='{escape_attr(date_iso)}' />\n")
            f.write("\t</currency>\n")
        f.write("</values>")
