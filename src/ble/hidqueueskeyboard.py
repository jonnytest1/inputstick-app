

from collections import deque
from queue import Queue
from typing import Literal, Union

from ble.hidinfo import HidInfo
from .packettype import Packet_Type

from .packet import Packet
from inputstick.report.keyboardreport import KeyboardReport
from inputstick.hidtransaction import HidTransaction
from inputstick.modifiers import Modifiers, modifiers_instance, zero_modifiers
from inputstick.config import typing_speed
from inputstick.packetqueue import packet_queue


class HidTransactionQueue:
    DEFAULT_BUFFER_SIZE = 32
    DEFAULT_MAX_REPORTS_PER_PACKET = 32

    INTERFACE_KEYBOARD = 0
    INTERFACE_CONSUMER = 1
    INTERFACE_MOUSE = 2
    INTERFACE_RAW_HID = 3

    def __init__(self, interface: int, buffer_capacity=DEFAULT_BUFFER_SIZE, max_packets_per_report=DEFAULT_MAX_REPORTS_PER_PACKET) -> None:
        self.buffer_capacity = buffer_capacity
        self.free_space = buffer_capacity
        self.max_reports_per_packet = max_packets_per_report
        self.queue: deque[HidTransaction] = deque()

        self.sent_since_notif = 0
        self.interface = interface
        if self.interface == HidTransactionQueue.INTERFACE_KEYBOARD:
            self.packet_type = Packet_Type.CMD_HID_DATA_KEYB

        self.buffer_empty_ct = 0

    def set_capacity(self, cap: int):
        diff = cap-self.buffer_capacity

        self.buffer_capacity += diff
        self.free_space -= diff

    def append_transaction(self, transaction: HidTransaction):

        while len(transaction.reports) > self.max_reports_per_packet:
            temptransaction = transaction.split(self.max_reports_per_packet)
            self.queue.append(temptransaction)

        self.queue.append(transaction)

    def update(self, hid: HidInfo):
        freed_space = 0
        buffer_empty = False

        if self.interface == HidTransactionQueue.INTERFACE_KEYBOARD:
            freed_space = hid.keyreport_sent_to_host
            buffer_empty = hid.keyboard_ready
        else:
            raise Exception("not implemented")

        self.free_space += freed_space
        if self.free_space > self.buffer_capacity:
            self.free_space = self.buffer_capacity

        if buffer_empty:
            self.buffer_empty_ct += 1

            if self.buffer_empty_ct == 10:
                self.free_space = self.buffer_capacity
        else:
            self.buffer_empty_ct = 0

        if len(self.queue) == 0:
            if self.free_space == self.buffer_capacity and self.sent_since_notif != 0:
                self.sent_since_notif = 0
                self.notif_on_remote_buffer_empty()
        else:
            self.send()

    def notif_on_remote_buffer_empty(self):
        print("notif_on_remote_buffer_empty")

    def notif_on_local_buffer_empty(self):
        # print("notif_on_local_buffer_empty")
        pass

    def send(self):
        send_state: Union[Literal["initial"],
                          Literal["sent"], Literal["send_next"]] = "initial"

        while send_state == "initial" or send_state == "send_next":
            send_state = "sent"
            if len(self.queue) > 0 and self.free_space > 0:
                reports = 0
                remaining_reports = min(
                    self.max_reports_per_packet, self.free_space)
                packet = Packet(False, self.packet_type, reports)

                transaction = self.queue[0]
                first_transaction_cmd = transaction.transaction_type_cmd

                while True:
                    try:
                        transaction = self.queue[0]
                    except IndexError as e:
                        break
                    if transaction == None:
                        break
                    trnsaction_cmd = transaction.transaction_type_cmd
                    if trnsaction_cmd != first_transaction_cmd:
                        break
                    report_length = len(transaction.reports)
                    if report_length > remaining_reports:
                        break
                    remaining_reports -= report_length
                    reports += report_length
                    while len(transaction.reports) > 0:
                        next_report = transaction.pop_next_report()
                        packet.add_bytes(next_report.get_bytes())
                    self.queue.popleft()

                if reports > 0:
                    if first_transaction_cmd != Packet_Type.TRANSACTION_CMD_DEFAULT:
                        packet.modify_byte(0, first_transaction_cmd.value)

                    packet.modify_byte(1, reports)
                    packet_queue.put(packet)
                    print("add packet to queue")
                    self.free_space -= reports
                    self.sent_since_notif += reports

                if len(self.queue) == 0:
                    self.notif_on_local_buffer_empty()
                if reports > 0:
                    send_state = "send_next"


keyboardQueue = HidTransactionQueue(HidTransactionQueue.INTERFACE_KEYBOARD)


def press_and_release(key: int, typing_speed=typing_speed, mofier: Modifiers = modifiers_instance):
    transaction = HidTransaction()

    if typing_speed < 1:
        typing_speed = 1

    for i in range(typing_speed):
        transaction.add_report(
            report=KeyboardReport(mofier, KeyboardReport.NONE))

    for i in range(typing_speed):
        transaction.add_report(
            report=KeyboardReport(mofier, key))

    for i in range(typing_speed):
        transaction.add_report(
            report=KeyboardReport(zero_modifiers, KeyboardReport.NONE))

    keyboardQueue.append_transaction(transaction)
    keyboardQueue.send()
