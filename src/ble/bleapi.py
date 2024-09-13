from datetime import datetime
from queue import Empty, Queue
from bleak.backends.scanner import AdvertisementData
from bleak.backends.device import BLEDevice
import asyncio
from bleak import BleakScanner, BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic

from ble.packet import Packet
from pygamelib.status import ConnectionStatus
from .bleconnection import BLEConnection, CON_STATE
from threading import current_thread
import traceback
stick_mac = ":DD"

# stick_mac = ":F2"


def on_ad(device: BLEDevice, advertisement_data: AdvertisementData):
    global found
    print(device.address, device.name)

    if device.name is not None and "Input" in device.name and not found and stick_mac in device.address:
        print("got one")
        found = True
        asyncio.create_task(on_ad_async(device, advertisement_data))


UUID_NRF_SPS = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"

found = False


pakcet_queue: Queue[Packet] = Queue()
con_status: ConnectionStatus
scanner = BleakScanner(on_ad, service_uuids=[UUID_NRF_SPS])

loop = asyncio.new_event_loop()


async def on_ad_async(device: BLEDevice, advertisement_data: AdvertisementData):
    global found
    try:
        await asyncio.sleep(1)
        print(f"connecting to {device.address} {device.name}")

        def on_disconnect(c):
            global found
            print("on_disconnect")
            found = False
            asyncio.create_task(scanner_loop())
        client = BleakClient(
            device, timeout=4, disconnected_callback=on_disconnect)
        await client.connect()
        con_status.connected()

        services = client.services

        for service in services:
            print("svc"+service.uuid)

            if UUID_NRF_SPS in service.uuid:
                print("found device")
                con = BLEConnection(client, service, loop)

                def on_ready(state, con=con):
                    if state.state == CON_STATE.READY:
                        con_status.ready()

                        async def async_packet_loop():
                            print("starting packet queue")
                            while True:
                                try:
                                    packet = pakcet_queue.get_nowait()
                                    print("> sending packet")
                                    con.send_packet(packet)
                                    pakcet_queue.task_done()
                                    await asyncio.sleep(0.1)
                                except Empty as e:
                                    await asyncio.sleep(0.1)
                        asyncio.create_task(async_packet_loop())

                con.connection_status.on_emit(on_ready)
                print("got service")
                try:
                    connected = await con.init()
                    if not connected:
                        print("reset on not connected")
                        found = False
                        await scanner_loop()
                except Exception as e:
                    print("reset on exc")
                    print(traceback.format_exc())
                    found = False
                    await scanner_loop()
                    return
        print("connection init done")
    except asyncio.TimeoutError:
        print("reset on timeout")
        found = False
        await scanner_loop()


async def scanner_loop():
    # "00001101-0000-1000-8000-00805F9B34FB",
    # "00002902-0000-1000-8000-00805f9b34fb",

    #

    while True:
        if (found):
            return
        print("(re)starting scanner")
        await scanner.start()
        await asyncio.sleep(5.0)
        await scanner.stop()


def start_ble_conection(queue: Queue[Packet], status: ConnectionStatus):
    global pakcet_queue
    global con_status

    con_status = status

    pakcet_queue = queue

    loop.create_task(scanner_loop())
    print("running loop in "+current_thread().name)
    loop.run_forever()
