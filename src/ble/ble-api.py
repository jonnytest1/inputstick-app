from datetime import datetime
from bleak.backends.scanner import AdvertisementData
from bleak.backends.device import BLEDevice
import asyncio
from bleak import BleakScanner, BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic

from bleconnection import BLEConnection


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


async def on_ad_async(device: BLEDevice, advertisement_data: AdvertisementData):

    try:
        print(f"connecting to {device.address} {device.name}")
        async with BleakClient(device) as client:
            services = client.services

            for service in services:
                print("svc"+service.uuid)

                if UUID_NRF_SPS in service.uuid:
                    print("found device")
                    con = BLEConnection(client, service)
                    print("got service")
                    await con.init()

                    device_connection = asyncio.get_running_loop().create_future()

                    print("set connection future")
                    await asyncio.wait([device_connection])
    except asyncio.TimeoutError:
        print("timeout connecting")
        exit(1)

scanner = BleakScanner(on_ad, service_uuids=[
    UUID_NRF_SPS])


async def main():

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

loop = asyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()
