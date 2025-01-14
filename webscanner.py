import socket
import os
import sys
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from PIL import Image
from io import BytesIO

# DISCLAIMER
# Warning this python script makes active connections to the specified IP address and does port scanning

# Default max amounts of port 65535
port_max = 10000
verbose = 0

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
    ports = {}
    for port in all_ports:
        try:
            result = requests.get(f"http://{ip}:{str(port)}/")
            # Later on add https support here
            ports[f"{str(port)}"] = "http"
        except:
            continue

    # Return key value pair with port number and according protocol (prot) next to it
    return ports

def take_screenshots_browser(ip, port, prot):
    url = prot + "://" + ip + ":" + port
    options = browser_setup()
    browser = webdriver.Chrome(options)
    browser.get(url)
    id = ip + ":" + port + "-" + prot

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

        # Later put all the screenshots in a pdf with relevant information
        screenshot.save('files-web/screenshot-' + id + '.png')
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
___________________
 | _______________ |
 | |XXXXXXXXXXXXX| |
 | |XXXXXXXXXXXXX| |
 | |XXXXXXXXXXXXX| |
 | |XXXXXXXXXXXXX| |
 | |XXXXXXXXXXXXX| |
 |_________________|
     _[_______]_
 ___[___________]___
|         [_____] []|__
|         [_____] []|  \__
L___________________J     \ \___\/
 ___________________      /\
/###################\    (__)
          """)

def check_dir():
    if not os.path.exists("./files-web"):
                os.makedirs("./files-web") 

def main():
    argument_list = sys.argv
    length_args = len(argument_list)

    if (length_args == 1):
        intro()
        print("Please specify the target IP address as an argument to the python script\n-> Such as `python script.py 0.0.0.0`")
        exit()

    if length_args > 2:
        print("Only specify the target IP as the second argument")
        exit()
    
    ip_arg = argument_list[1]
    open_ports = scan_all_ports(ip_arg)
    
    print("Checking for webservers running on found ports...")
    filtered_ports_prot = check_port_service(ip_arg, open_ports)

    for port, protocol in filtered_ports_prot.items():
        take_screenshots_browser(ip_arg, port, protocol)


if __name__ == "__main__":
    main()