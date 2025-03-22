import socket
import os
import sys
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from io import BytesIO
from matplotlib import font_manager
# DISCLAIMER
# Warning this python script makes active connections to the specified IP address and does port scanning

# Default max amounts of port 65535
port_max = 10000
verbose = 0
images = []

def get_known_ports():
    return [
    20,  # FTP Data Transfer
    21,  # FTP Control
    22,  # SSH
    23,  # Telnet
    25,  # SMTP
    53,  # DNS
    67,  # DHCP Server
    68,  # DHCP Client
    110, # POP3
    143, # IMAP
    3306,# MySQL
    5432,# PostgreSQL
    6379,# Redis
    ]

def scan_all_ports(ip):
    ports = []
    print("Starting scan for host: " + ip)
    for i in range(1,port_max):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(1)
        result = sock.connect_ex((ip,i))
        if result == 0:
            print("- open port found: " + str(i))
            ports.append(i)
        sock.close()
    return ports

def check_port_service(ip, all_ports):
    known_ports = get_known_ports()
    for port in all_ports:
        if (port in known_ports):
            all_ports.remove(port)

    ports = {}
    for port in all_ports:
        try:
            result = requests.get(f"http://{ip}:{str(port)}/")
            # Later on add https support here
            print(f"- found a http service running on {port}")
            ports[f"{str(port)}"] = "http"
        except:
            continue
    
    if (len(ports) == 0):
        print("No ports found with http(s) running on it")
        exit()

    return ports

def take_screenshots_browser(ip, port, protocol):
    url = protocol + "://" + ip + ":" + port
    options = browser_setup()
    browser = webdriver.Chrome(options)
    browser.get(url)
    id = ip + "-" + port + "-" + protocol

    def browser_execute():
        js = 'return Math.max( document.body.scrollHeight, document.body.offsetHeight,  document.documentElement.clientHeight,  document.documentElement.scrollHeight,  document.documentElement.offsetHeight);'

        scrollheight = browser.execute_script(js)

        if verbose > 0: 
            print(scrollheight)

        slices = []
        offset = 0
        while offset < scrollheight:
            if verbose > 0: 
                print(offset)

            browser.execute_script("window.scrollTo(0, %s);" % offset)
            img = Image.open(BytesIO(browser.get_screenshot_as_png()))
            offset += img.size[1]
            slices.append(img)

            if verbose > 0:
                browser.get_screenshot_as_file('%s/screen_%s.png' % ('/tmp', offset))
                print(scrollheight)


        screenshot = Image.new('RGB', (slices[0].size[0], offset))
        offset = 0
        for img in slices:
            screenshot.paste(img, (0, offset))
            offset += img.size[1]

        screenshot.save('files-web/screenshot-' + id + '.png')
        
        Il = ImageDraw.Draw(screenshot)
        output = f"IP: {ip}\nPort: {port}\nProtocol: {protocol}"
        file = font_manager.findfont('Source Code Pro')
        mfont = ImageFont.truetype(file, 20)
        Il.text((10, 10), output, font=mfont)
        images.append(screenshot)
        
        browser.quit()

    check_dir()
    browser_execute()

def browser_setup():
    WINDOW_SIZE = "1920,1080"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
    chrome_options.timeouts = { 'pageLoad': 10000 }

    return chrome_options


def intro():
    print("""
    Welcome to this program written by cixk
    ---------------------------------------

    Usage: python3 webscanner.py ip-address [options]

    Options
        Options are:
        -p [port-number]   Specify one or multiple ports to scan

    Examples
        python3 webscanner.py 192.168.0.1 -p 8080,9090,2000
        python3 webscanner.py 192.168.0.1

    Info:
    If no port number is specified all ports are scanned until 10000 due to performance reasons
    -> The maximium port number can be changed using the port_max var

          """)

def check_dir():
    if not os.path.exists("./files-web"):
                os.makedirs("./files-web")

def create_pdf_report(ip):
    pdf_path = f"./web-{ip}-report.pdf"

    if (len(images) == 0):
        print("Only 1 screenshot taken not enough for a pdf please see the files directory")
    else:
        images[0].save(
            pdf_path, "PDF", resolution=100.0, save_all=True, append_images=images[1:]
        )

def get_ip_by_hostname(target_hostname):
    # Catch errors thrown later
    return socket.gethostbyname(target_hostname)

def main():
    argument_list = sys.argv
    length_args = len(argument_list)

    if (length_args == 1):
        intro()
        exit()

    target_arg = argument_list[1]

    ip_arg = get_ip_by_hostname(target_arg)

    open_ports = scan_all_ports(ip_arg)
    
    print("Checking for webservers running on found ports...")
    filtered_ports_prot = check_port_service(ip_arg, open_ports)

    print("Starting screenshotting...")
    for port, protocol in filtered_ports_prot.items():
        take_screenshots_browser(ip_arg, port, protocol)

    create_pdf_report(ip_arg)

if __name__ == "__main__":
    main()
