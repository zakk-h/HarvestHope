import pandas as pd

data = [
    ["Item", "Quantity", "Comments"],
    ["Laptops", "", ""],
    ["Dell Latitude 5540", 2, ""],
    ["Dell Latitude 3420 with charger", 2, ""],
    ["Lenovo 100e Chromebook (not working)", 1, "Includes charger"],
    ["Lenovo AMD4 Chromebook (keyboard not working)", 1, ""],
    ["Lenovo AMD4 Chromebook (damaged)", 1, ""],
    ["Dell Laptop i3 Latitude 3520 with charger", 1, ""],
    ["Dell Laptop i3 Latitude 3520 (low memory)", 1, "No charger"],
    ["Laptop Chargers", "", ""],
    ["Lenovo 65W Laptop Charger", 2, ""],
    ["Dell Notebook Power Bank Plus", 1, "Includes cables"],
    ["Dell 45W DC Adapter", 1, ""],
    ["Laptop Batteries", "", ""],
    ["Generic Laptop Batteries", 2, ""],
    ["Laptop Accessories", "", ""],
    ["Kensington Adjustable Laptop Riser and Cooling Stand", 2, ""],
    ["Dell USB-C Docking Station (with cables)", 1, ""],
    ["Dell USB-C Docking Station (separate power)", 2, ""],
    ["Tablets", "", ""],
    ["Lenovo 100e Chromebook Gen3 4GB RAM 32GB EMMC", 10, "AMD chip, includes 65W charger"],
    ["Galaxy Tabs in orange case", 4, ""],
    ["Galaxy Tabs in black case", 3, ""],
    ["Galaxy Tabs (no case)", 2, ""],
    ["Dell Tablet running Windows 8 Pro Intel", 3, ""],
    ["Windows Surface with attachable keyboard", 1, ""],
    ["AT&T Cellular Galaxy Tab A", 1, ""],
    ["Old iPad in leather case", 1, ""],
    ["Tablet Chargers", "", ""],
    ["Galaxy Tab Chargers with bricks", 3, ""],
    ["Tablet Cases and Accessories", "", ""],
    ["Black Galaxy Tab Cases", 14, "Not on tablets"],
    ["Bluetooth Keyboard Case for Tab", 1, ""],
    ["Tempered Glass Screen Protector Packs", 5, ""],
    ["Phones", "", ""],
    ["iPhone XR", 2, ""],
    ["iPhone 11", 1, ""],
    ["iPhone 6S", 1, ""],
    ["iPhone 5S", 1, "Unopened"],
    ["S20 FE 5G", 2, ""],
    ["Phone Cases", "", ""],
    ["S21 Phone Case", 5, ""],
    ["S21+ Phone Case", 1, ""],
    ["Networking Equipment", "", ""],
    ["Juniper Networks SRX300 Gateway Router", 1, "Includes Asian power devices adapter"],
    ["Linksys Router with 4 Port Switch", 1, ""],
    ["Netgear 8 Port Gigabit Ethernet Switch", 1, ""],
    ["Zyxel Smart Managed Switch GS1900", 1, ""],
    ["Netgear ProSafe 16 Port Ethernet Switch", 1, ""],
    ["D-Link 5 Port Gigabit Ethernet Switch", 1, ""],
    ["Access Points", "", ""],
    ["Linksys 2.4 GHz Wireless Access Point", 1, ""],
    ["E400 CNPilot Gigabit Access Point", 7, ""],
    ["CNPilot E510 Access Point", 2, ""],
    ["UniFi Access Point AC Pro", 1, ""],
    ["Storage Devices", "", ""],
    ["Seagate 1TB HDD Baracuda", 3, ""],
    ["Seagate 2TB 7200RPM SATA HDD", 3, ""],
    ["Bytec Res Core Mobile External Hard Drive", 1, ""],
    ["Kingwin 3.5\" Hard Drive", 1, ""],
    ["SmartDrive Mobile Drive HDD", 1, ""],
    ["Miscellaneous Tech", "", ""],
    ["Brother Color Printer HL L8500CDN", 1, ""],
    ["Panini Vision X Check Scanner", 1, ""],
    ["ScanSnap Scanner", 1, ""],
    ["Dymo Label Printer 450", 1, ""],
    ["Brother P-Touch Label Maker", 1, ""],
    ["DYMO Embossing Label Maker", 1, ""],
    ["Olympus 8MP Camera with AV Cable", 1, ""],
    ["Casio DC1 Camera 3x Zoom", 1, ""],
    ["Panasonic TV with Power Cable", 1, ""],
    ["Old HP TVs Bulky with Power Cables", 2, ""],
    ["Muzak Digital Music Power Amplifier", 1, ""],
    ["Supermicro Bundle of Jumper Wires", 1, ""],
    ["Audiocodes HTTPS Fax ATA", 1, ""],
    ["Hipro 50W AC Adapter", 1, ""],
    ["Symbol Charge Cradle, DC Charger", 3, ""],
    ["Symbol Handheld Lithium Batteries", 8, ""],
    ["Power Supplies (generic)", 4, ""],
    ["Thermal Transfer Ribbon Rolls", 8, ""],
    ["Cables and Adapters", "", ""],
    ["Ethernet Cables", 6, ""],
    ["USB A to USB A", 2, ""],
    ["USB A to USB B", 2, ""],
    ["USB A to Type B", 5, ""],
    ["USB 2.0 Slim Portable Optical Drive with USB Cable", 1, ""],
    ["Apple 30-pin to USB-A", 1, ""],
    ["USB to HDMI Cable", 1, ""],
    ["Lightning Cable", 34, ""],
    ["USB-C to USB-C (supports 100W)", 2, ""],
    ["DisplayPort to HDMI Adapter", 2, ""],
    ["DVI to HDMI Adapter", 2, ""],
    ["DVI to HDMI Cable", 2, ""],
    ["VGA Adapter", 3, ""],
    ["VGA Cable", 2, ""],
    ["Ethernet Cable RJ45 Connector", 1, ""],
    ["Extension Cords (short)", 7, ""],
    ["6ft USB Extension Cable", 1, ""],
    ["USB A Splitter (1 to 3)", 1, ""],
    ["Jabra USB Hub", 1, ""],
    ["VisionTek USB Hub (no cable)", 1, ""],
    ["USB Gigabit LAN Cable", 1, ""],
    ["Mouse and Keyboard Extension Cable (6-pin Belkin)", 1, ""],
    ["Audio Cable 3.5mm", 3, ""],
    ["Benfei DisplayPort to HDMI Adapter", 2, ""],
    ["USB A to USB A", 1, ""],
    ["Ethernet Cable", 1, ""],
    ["Power Supply", 1, ""],
    ["Panfore Power Supply", 1, ""],
    ["ITE Power Supply", 1, ""],
    ["USB Cable", 1, ""],
    ["Computer Peripherals", "", ""],
    ["Logitech Wireless Keyboard (no accessories)", 1, ""],
    ["K350 Wireless Keyboard and Mouse (no accessories)", 1, ""],
    ["Wired Keyboard", 1, ""],
    ["Wired Microsoft Mouse", 1, ""],
    ["IBM Wired Keyboard", 1, ""],
    ["Monitors", "", ""],
    ["Dell 27\" Monitor with Stand and HDMI", 2, ""],
    ["HannsG Monitor", 1, ""],
    ["Dell Monitor", 1, ""],
    ["Dell Monitor with Mount", 1, ""],
    ["Dell Wide Stand (to hang/attach 2 monitors)", 1, ""],
    ["TVs", "", ""],
    ["Panasonic TV with Power Cable", 1, ""],
    ["Old HP TVs Bulky with Power Cables", 2, ""],
    ["Panasonic TV Remote", 1, ""],
    ["HP TV Remote", 1, ""],
    ["Other Accessories", "", ""],
    ["Shrradoo Anti-theft Laptop Backpack", 2, ""],
    ["Bluetooth Tracking Keychain with Selfie Remote", 1, ""],
    ["Verbatim External CD/DVD Writer with Cable", 1, "Software Nero Burn Archive included"],
    ["Inateck 2.4G Wireless Barcode Scanner", 1, "Includes USB cable and USB port receiver"],
    ["Bluetooth Keyboards for Tablets with Props", 4, ""],
    ["Insignia TV Wall Mount for Flat Panel TV (<50lbs)", 1, ""],
    ["Desktop Computer Tower (old, with optical and floppy disk)", 1, ""],
    ["Honeywell Quad Battery Charger with Wall Plug", 1, ""],
    ["Honeywell Rugged Device (phone form factor) with Laser Scanner", 2, ""],
    ["Handheld Scanner to Put Honeywell Device In", 5, ""],
    ["MountIt Height Adjustable Anti-theft iPad Floor Stand", 1, ""]
]

df = pd.DataFrame(data[1:], columns=data[0])

file_path = '/mnt/data/Harvest_Hope_Inventory.xlsx'
df.to_excel(file_path, index=False)

file_path
