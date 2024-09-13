from .report.hidereport import HidReport
from ble.packettype import Packet_Type


class HidTransaction:

    def __init__(self, packet: Packet_Type = Packet_Type.TRANSACTION_CMD_DEFAULT) -> None:
        self.transaction_type_cmd = packet
        self.reports: list[HidReport] = []

    def add_report(self, report: HidReport):
        self.reports.append(report)

    def pop_next_report(self):
        return self.reports.pop(0)

    def split(self, count: int):
        result = HidTransaction()
        if count <= len(self.reports):
            while count > 0:
                report = self.reports.pop(0)
                result.add_report(report)
                count -= 1
        return result
