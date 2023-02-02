from xml.sax.handler import ContentHandler
from xml.sax import parse as xml_parse

import datetime as dt

def _str2num(x: str) -> int | float:
    f = float(x)
    i = int(f)
    return f if i != f else i

class _BnrXmlHandler(ContentHandler):
    def __init__(self) -> None:
        super().__init__()
        self._stack = []
        self._items = {}
        self._currency = None

    def startElement(self, name, attrs):
        stack = self._stack
        stack.append(name)

        if len(stack) >= 2:
            if stack[0] == "values" and stack[1] == "currency":
                if len(stack) == 2:
                    if "name" in attrs:
                        self._currency = self._items.setdefault(attrs["name"], dict())
                elif self._currency is not None:
                    if stack[2] == "rate":
                        if len(stack) == 3:
                            if "date" in attrs and "value" in attrs:
                                date = dt.date.fromisoformat(attrs["date"])
                                value = _str2num(attrs["value"])
                                self._currency[date] = value


    def endElement(self, name):
        stack = self._stack
        if stack == ["values", "currency"]:
            self._currency = None

        assert stack.pop() == name

    pass

def parse_bnr_xml(file):
    handler = _BnrXmlHandler()
    xml_parse(file, handler)
    return handler._items


