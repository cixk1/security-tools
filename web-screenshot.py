from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from PIL import Image
from io import BytesIO
import sys
import socket
import os

# Warning this python script makes active connections to the specified IP address and does port scanning

verbose = 0
# Default max amounts of port 65535
port_max = 10000

def get_all_ports(target_ip):
    ports = []
    print("Starting scan for host: " + target_ip)
    for i in range(1,port_max):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(1)
        result = sock.connect_ex((target_ip,i))
        if result == 0:
            print("- open port found: " + str(i))
            ports.append(i)
        sock.close()
    return ports

def write_history(target_ip, open_ports):
    #while open("web_dir/history.txt", "w") : Still confused on this part
    return 1

def get_protocol(port):
        switch={
            80:'http',
            443:'https'
        }
        return switch.get(port, "http")

def browser_setup():
    WINDOW_SIZE = "1920,1080"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
    chrome_options.timeouts = { 'pageLoad': 10000 }


    return chrome_options

def get_status():
    return 200


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


if (len(sys.argv) <= 1):
    print("Specify the target IP as second argument")
else:
    target_ip  = sys.argv[1]
    open_ports = get_all_ports(target_ip)
    print("Starting browser requests...")
    for port in open_ports:
        protocol = get_protocol(port)
        url = protocol + '://'  + target_ip + ':' + str(port)
        options = browser_setup()
        browser = webdriver.Chrome(options=options) # Something is wrong here, cannot specify capabilities a parameter
        browser.get(url)

        if not os.path.exists("./web-screens"):
                os.makedirs("./web-screens")
        
        status_code = get_status() # TODO
        if (status_code == 200):
            id = target_ip + ':' + str(port) + '--' + protocol
            browser_execute(id)