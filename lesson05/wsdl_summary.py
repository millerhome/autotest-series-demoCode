"""把 WSDL 整理成一份「介面摘要」：每個操作一行、每個型別的欄位各一行，方便比對。"""
from zeep import Client


def summarize(wsdl_url, namespace="http://example.test/policy/"):
    client = Client(wsdl_url)
    lines = []
    for service in client.wsdl.services.values():
        for port in service.ports.values():
            for name, op in sorted(port.binding._operations.items()):
                lines.append(f"operation {name}({op.input.signature()}) -> {op.output.signature(as_output=True)}")
    for t in sorted(client.wsdl.types.types, key=lambda t: str(t.qname)):
        if t.qname is None or t.qname.namespace != namespace:
            continue
        lines.append(f"type {t.qname.localname}")
        for field, element in t.elements:
            lines.append(f"    {field}: {element.type.qname.localname}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    import sys
    print(summarize(sys.argv[1]), end="")
