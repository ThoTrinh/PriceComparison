"""
@author ThoTrinh
@info   Program allows users to check when the price of a product they are interested on is on sale
        Program utilizes anonymous proxy IP and uses intelligence to change IP on request and also to delay
        activity on websites to avoid bot detection, which will not allow program to check price on product
        anymore.

        You will need to install tor and privoxy for this. Here are some good manuals that cover installation
        Tor: Tor is pretty simple. I'll explain it here so you don't have to look around

        1. run this command. the "ANY_PASSWORD" below is not to be taken literally. replace it with your own passsword
            a. tor --hash-passsword ANY_PASSWORD
            b. You will use "ANY_PASSWORD" and replace areas designated INSERT_PASSWORD_HERE with it below
            c. You will get a hash output from this. IT IS IMPERATIVE YOU COPY THE HASH OUTPUT EXACTLY AND SAVE IT
        2. Go to the folder where tor is installed. If you used homebrew to install, type "brew info tor"
            a. find the file named "torrc", if no file, then create one
            b. type the command             vim torrc
            c. enter the following into the file

            ControlPort 9051

            #Set your hashed password.
            HashedControlPassword 16:HASH_OUTPUT

            d. If you haven't figured out yet, place the hash output from step 1c. in the area designated
               HASH_OUTPUT

            e. when this is all done, to run tor, just type "tor"


        Privoxy: http://www.andrewwatters.com/privoxy/

        You should run tor and privoxy before running this file
"""

from stem import Signal
from stem.control import Controller
from bs4 import BeautifulSoup
import requests
import smtplib
import urllib3
import time


class ConnectionFactory:

    # replace this with your own user agent
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Safari/605.1.15'
    header = {'user-agent':user_agent}

    numberofIps = 12
    secondsofdelay = 5
    #Holders
    defaultIP = "0.0.0.0"
    newIP = "0.0.0.0"
    oldIP="0.0.0.0"

    def createConnection(self):
        # sends new IP address
        with Controller.from_port(port = 9051) as controller:

            controller.authenticate(password = "INSERT_PASSWORD_HERE") # for users, you would insert tor password here
            if controller.is_newnym_available():
                controller.signal(Signal.NEWNYM)
            controller.close()

    def createnewIP(self):

        if self.newIP == self.defaultIP:
            self.createConnection()
            self.newIP = self.openurl('http://icanhazip.com/')
            # if icanhazip doesn't work, use http://checkip.amazonaws.com/
            print("New IP address is now {}".format( self.newIP ))
            print( self.newIP )
        else:
            self.oldIP = self.newIP
            self.createConnection()
            self.newIP = self.openurl('http://icanhazip.com/')
            # if icanhazip doesn't work, use http://checkip.amazonaws.com/
            print("New IP address is now {}".format( self.newIP ))
            print( self.newIP )

        wait = 0
        while ( self.oldIP == self.newIP ):
            time.sleep( self.secondsofdelay )
            wait += self.secondsofdelay
            print("{} Seconds until new IP address".format( wait ))
            self.newIP = self.openurl( 'http://icanhazip.com/' )
            # if icanhazip doesn't work, use http://checkip.amazonaws.com/

    def openurl( self, url ):
        http = urllib3.PoolManager()
        proxy = urllib3.ProxyManager( "http://127.0.0.1:8118", timeout=20 )
        req = proxy.request( method='GET' ,url=url , headers=self.header )
        ip = req.data
        req.release_conn()
        return ip


class ParseFactory():

    # Set if you would like to see when product has gone on sale
    original_price = 0

    def priceChecker( self, html, titleID, priceID, time ):

        soup = BeautifulSoup(html, 'html.parser')

        title = soup.find( id=titleID ).get_text()
        price = soup.find( id=priceID ).get_text()

        separation = ','
        inter_price = price.split( separation, 1 )[0]
        converted_price = int( inter_price.replace('.', '') )

        # Print out product name and price
        print( title.strip() )
        print( converted_price )

        if ( time == 0 ):
            original_price = converted_price

        if (int( converted_price ) < original_price ):
            print( "Product has gone on sale ")
        else:
            print("Price is still the same!\n")


class item():
    name = ""
    url =""
    def __init__(self,name,url):
        self.name = name
        self.url = url


if __name__ == '__main__':
    connect = ConnectionFactory()
    parser = ParseFactory()

    i = 0
    while i < 1000:
        connect.createnewIP()
        URL = 'https://www.amazon.com/Rick-Roll-Definition-T-Shirt-Internet/dp/B07PQLYXBJ/ref=sr_1_8?keywords=rick+roll&qid=1648177153&sr=8-8'
        resp = connect.openurl(URL)

        # replace 2nd and 3rd arguments with corresponding id for your URL. different for amazon, walmart, ebay, etc.
        items = parser.priceChecker(resp, "productTitle", "buyNew_noncbb", i)
        i = i+1
        time.sleep( 7200 ) # wait two hours in between checking price
