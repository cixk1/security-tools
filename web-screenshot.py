from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from PIL import Image
from io import BytesIO
import socket
import os
import sys

# Warning this python script makes active connections to the specified IP address and does port scanning

verbose = 0
# Default max amounts of port 65535
port_max = 10000

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

def check_port_service(host, list_ports):
    # Check the service running on port
    # Wether is is running a http/s service

    # Return an array at the end of all ports that have http/s service running on them
    return 0

def browser_setup():
    WINDOW_SIZE = "1920,1080"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
    chrome_options.timeouts = { 'pageLoad': 10000 }


    return chrome_options

def browser_execute(id):
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
    screenshot.save('web-screens/screenshot-' + id + '.png')
    browser.quit()


""" if (len(sys.argv) <= 1):
    print("Specify the target IP as second argument")
else:
    target_ip  = sys.argv[1]
    open_ports = get_all_ports(target_ip)
    print("Starting browser requests...")

    
    for port in open_ports:
        url, status_code = check_http_protc(target_ip, port)


        options = browser_setup()
        browser = webdriver.Chrome(options=options) # Something is wrong here, cannot specify capabilities a parameter
        browser.get(url)

        if not os.path.exists("./files_web"):
                os.makedirs("./files_web") 
        
        browser_execute(id)
"""

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
    filtered_ports = check_port_service(ip_arg, open_ports)


if __name__ == "__main__":
    main()