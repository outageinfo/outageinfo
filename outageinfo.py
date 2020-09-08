#!/usr/bin/env python3 

import string
import requests
import time
import json
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import phonenumbers

# Store bash color values
CRED = '\033[91m'
CBHL = '\33[34m'
CYEL = '\33[96m'
CEND = '\033[0m'


def aep(phone):
    companylist = [("https://www.appalachianpower.com/outages/report/","Appalachian Power"), 
        ("https://www.swepco.com/outages/report/","Southwestern Electric Power"),
        ("https://www.aeptexas.com/outages/report/","AEP Texas"),
        ("https://www.aepohio.com/outages/report/","AEP Ohio"),
        ("https://www.psoklahoma.com/outages/report/","PS Oklahoma")
        ]

    for item in companylist:
        starturl = item[0]
        subsidiary = item[1]
        print(CRED + '~~~Trying ' + str(phone) + ' in ' + subsidiary + '~~~ ' + CEND)
        driver = webdriver.Firefox()
        driver.implicitly_wait(10)
        driver.get(starturl) 
        driver.find_element_by_css_selector("input[type='radio'][value='N']").click()
        driver.find_element_by_xpath('//*[@id="cphContentMain_ctl00_BtnContinueHazard"]').click()
        time.sleep(1)
        phonebox = driver.find_element_by_xpath('//*[@id="cphContentMain_ctl00_TbPhoneSearch"]') 
        phonebox.send_keys(phone)
        phonebox.send_keys(Keys.ENTER)
        time.sleep(4)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        error = soup.find('div',{'id':'cphContentMain_ctl00_DivPhoneNotFound'})
        if error:
            print('Not found in ' + subsidiary)
            driver.quit()
        else:
            address = soup.find('p',{'class':'margin-bottom-0-5'})
            address2 = address.text.lstrip()
            print(CBHL + 'Phone number is connected to a ' + subsidiary + 'subscriber account, partial address is: ' + str(address2) + CEND) 
            driver.quit() 



def firstenergy(phone):
    phone = str(phone)
    nums = [phone[i:i+1] for i in range(0, len(phone), 1)]
    print(CRED + '~~~Trying ' + str(phone) + ' in First Energy~~~ ' + CEND)
    starturl = 'https://www.firstenergycorp.com/outages_help/Report_Power_Outages.html'

    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    driver.get(starturl)
    time.sleep(1)
    phoneInput = driver.find_element_by_xpath('//*[@id="quickAccessPhone"]')
    for num in nums:
        phoneInput.send_keys(num)
        time.sleep(.1)
    click = driver.find_element_by_name('next')
    click.send_keys(Keys.ENTER)
    time.sleep(4)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    error = soup.find('div', {'class':'alert error-block'})
    if error:
        print('Not found in First Energy')
        driver.quit()
    else:
        address = soup.findAll('input', {'id' : 'acctAddressNum1'})
        for addresses in address:
            houseNum = str(addresses.attrs.get('value'))
            print(CBHL + 'Phone number is connected to a First Energy subscriber account, partial house number is ' + houseNum + CEND)
            driver.quit()


def xcel(phone):
    print(CRED + '~~~Trying ' + str(phone) + ' in Xcel Energy~~~' + CEND)
    url = 'https://www.xcelenergy.com/xcel-dpmextn/searchByPhone.html'
    payload = 'phonenum=(123)+456-7890&radioSearch=callPhoneService&premisenum=1111111'
    r = requests.post(url, params = payload)
    soup = BeautifulSoup(r.text, 'html.parser')
    if 'Sorry' in str(r.content):
            print('Phone number not connected to Xcel Energy account')
            return
    else:
        print(CBHL + 'Phone number is connected to Xcel Energy subscriber with one of the following partial account nubmers:' + CEND)
        addresses = soup.findAll('label')
        for address in addresses:
            print(address.text)


def dtenergy(phone):
    print('')
    starturl = 'https://newlook.dteenergy.com/api/OutageService/sites?phone=' + str(phone)

    response = requests.get(starturl)
    jsonResponse = response.json()
    print(CRED + '~~~Trying ' + str(phone) + ' in DTE Energy~~~' + CEND) 

    if response.status_code == 404:
        print('Not found in DTE Energy')
        return

    if len(jsonResponse["results"]) > 1:
        print('Multiple subscribers found in DTE Energy for this phone number')

    for result in jsonResponse["results"]:
        print('Result for phone number in DTE Energy')
        print('Address is: ' + CBHL + str(result["address"]) + CEND)
        print('Zipcode is: ' + CBHL + str(result["postal_Code"])+ CEND)
        print('')

def coned(phone):
    print(CRED + '~~~Trying ' + str(phone) + ' ConEd ' + CEND)
    coned_url = 'https://www.coned.com/en/services-and-outages/report-track-service-issue/report-outage-status'

    boroughs = ['Bronx','Brooklyn','Manhattan','Queens','Staten Island','Westchester']

    for borough in boroughs:    
        driver = webdriver.Firefox()
        driver.implicitly_wait(10)
        driver.get(coned_url)
        time.sleep(1)

        first_selector = Select(driver.find_element_by_name('havePower'))
        first_selector.select_by_visible_text('No')

        second_selector = Select(driver.find_element_by_name('findAccount'))
        second_selector.select_by_visible_text('Phone Number')

        phone_field = driver.find_element_by_name('phoneNumber')
        phone_field.send_keys(phone)
        #phone format 1234567890
        final_select = Select(driver.find_element_by_name('borough'))

        final_select.select_by_visible_text(borough)
        time.sleep(.6)
        button = driver.find_element_by_xpath('/html/body/div[3]/div[3]/div/form/div[3]/div/fieldset/div[5]/div/button')
        button.click()

        time.sleep(5)

        soup=BeautifulSoup(driver.page_source, 'html.parser')

        errorl1 = soup.find('p',{'class' : 'transactional__error js-lookup-service-error'})
        try:
            errorl2 = errorl1.find('span', {'class' : 'js-error-message'})
            if errorl2.contents:
                print('Phone number not found in ' + borough)
                driver.quit()  
                continue
        except:

            find_test = soup.find('div', {'class' : 'address-box address-box--no-margin js-dropdown-button-contain'})
            nycstreet = str(find_test.attrs.get('data-street'))
            nyccity = str(find_test.attrs.get('data-city'))
            nycadd2 = str(find_test.attrs.get('data-address2'))
            nyczip = str(find_test.attrs.get('data-zipcode'))
            nycunit = str(find_test.attrs.get('data-unit'))
            nycco = str(find_test.attrs.get('data-company'))

            print(CBHL + 'Phone number connected to utilities in ' + borough + CEND)
            print('Not all data fields may be present')
            print('Street: ' + nycstreet)
            print('City: ' + nyccity)
            print('Secondary address: ' + nycadd2)
            print('Zipcode: ' + nyczip)
            print('Unit: ' + nycunit)
            print('Company: ' + nycco)
            driver.quit()


def nyseg(areaPhone, exchagePhone, stationPhone):
    print('')
    print(CRED + '~~~Trying ' + str(phone) + ' New York State Electric & Gas~~~ ' + CEND)
    starturl = 'https://ebiz1.nyseg.com/cusweb/outagenotification.aspx'

    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    driver.get(starturl)
    time.sleep(1)

    areacode = driver.find_element_by_name('uctlServicePhone:TextBox1')
    areacode.send_keys(areaPhone)
    exchange = driver.find_element_by_name('uctlServicePhone:TextBox2')
    exchange.send_keys(exchangePhone)
    subscriberno = driver.find_element_by_name('uctlServicePhone:TextBox3')
    subscriberno.send_keys(stationPhone)
    time.sleep(1)
    click = driver.find_element_by_name('Button1')
    click.send_keys(Keys.ENTER)
    time.sleep(6)

    soup=BeautifulSoup(driver.page_source, 'html.parser')

    test_for_error = soup.find('span', {'id' : 'lblInvalidData'})

    if test_for_error:
            print (test_for_error)
            print ('Not found in New York Gas & Electric')
            driver.quit()
            return

    else:
        address_interim = soup.find('span', {'id' : 'lblAddresSelect'})
        address = address_interim.find('strong').text
        print ('FOUND IN NEW YORK GAS & ELECTRIC')
        print ('Address is: ' + address)
        driver.quit()
        return


def rochesterge(areaPhone, exchagePhone, stationPhone):
    print('')
    print(CRED + '~~~Trying ' + str(phone) + ' Rochester (NY) Gas & Electric~~~ ' + CEND)

    starturl = 'https://ebiz1.rge.com/cusweb/outagenotification.aspx'

    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    driver.get(starturl)
    time.sleep(1)
    areacode = driver.find_element_by_name('uctlServicePhone:TextBox1')
    areacode.send_keys(areaPhone)
    exchange = driver.find_element_by_name('uctlServicePhone:TextBox2')
    exchange.send_keys(exchangePhone)
    subscriberno = driver.find_element_by_name('uctlServicePhone:TextBox3')
    subscriberno.send_keys(stationPhone)
    time.sleep(1)
    click = driver.find_element_by_name('Button1')
    click.send_keys(Keys.ENTER)
    time.sleep(5)

    soup=BeautifulSoup(driver.page_source, 'html.parser')

    test_for_error = soup.find('span', {'id' : 'lblInvalidData'})

    if test_for_error:
            print ('Not found in Rochester Gas & Electric')
            driver.quit()
            return

    else:
        address_interim = soup.find('span', {'id' : 'lblAddresSelect'})
        address = address_interim.find('strong').text
        pring ('FOUND IN ROCHESTER GAS & ELECTRIC')
        print ('Address is: ' + address)
        driver.quit()
        return

def exelon(phone):
    phone = str(phone)

    companylist = [("https://secure.bge.com/.euapi/mobile/custom/anon/BGE/outage/query","Baltimore Gas & Electric"), 
        ("https://secure.comed.com/.euapi/mobile/custom/anon/ComEd/outage/query","Commonwealth Edison"),
        ("https://secure.peco.com/.euapi/mobile/custom/anon/PECO/outage/query","Philadelphia Electric"),
        ("https://secure.pepco.com/.euapi/mobile/custom/anon/PEP/outage/query","Potomac Power & Electric"),
        ("https://secure.atlanticcityelectric.com/.euapi/mobile/custom/anon/ACE/outage/query","Atlantic City Electic"),
        ("https://secure.delmarva.com/.euapi/mobile/custom/anon/DPL/outage/query","Delmarva Power")
        ]

    for item in companylist:

        url = item[0]
        subsidiary = item[1]

        print('')
        print(CRED + '~~~Trying ' + str(phone) + ' in ' + subsidiary + '~~~' + CEND)
        payload = {'phone':phone}

        r = requests.post(url, json = payload)

        if r:
            jsonResponse = r.json()
            failCheck = str(jsonResponse["success"])
            if failCheck == "False":
                print('Not found in ' + subsidiary)
                continue
            if "meta" in jsonResponse:
                print(CBHL + '###########################' + CEND)
                print(CBHL + ' Multiple customers found!' + CEND)
                print(CBHL + '###########################' + CEND)
                for customer in jsonResponse["data"]:
                    print('')
                    acctno = customer["accountNumber"]
                    houseno = customer["addressNumber"]
                    address = customer["addressName"]
                    print('Address is: ' + houseno + ' ' + address)
                    if "apartmentUnitNumber" in customer:
                            apartment_no = customer["apartmentUnitNumber"]
                            print('Apartment number: ' + str(apartment_no))
                    print('Account number is: ' + str(acctno))

            else:
                acctno = jsonResponse["data"][0]["accountNumber"]
                address = jsonResponse["data"][0]["address"]
                customername = jsonResponse["data"][0]["OutageInfoBGE"]["customerName"]
                print('Subscriber name is: ' + CBHL + customername + CEND)
                print('Address is: ' + address)
                print('Account number is: ' + acctno)

        elif r.status_code == 404:
            print('Not found in ' + subsidiary)

if __name__ == "__main__":
    print(CRED +""" 
    ________          __                        .___        _____       
    \_____  \  __ ___/  |______     ____   ____ |   | _____/ ____\____  
     /   |   \|  |  \   __\__  \   / ___\_/ __ \|   |/    \   __\/  _ \ 
    /    |    \  |  /|  |  / __ \_/ /_/  >  ___/|   |   |  \  | (  <_> )
    \_______  /____/ |__| (____  /\___  / \___  >___|___|  /__|  \____/ 
            \/                 \//_____/      \/         \/             
          < a tool to find utility information by phone number>
        """ + CEND)

    if len(sys.argv) <= 1:
        print('Usage: python3 outageinfo.py 1234567890')
        print('')
        phone = input("Please enter a US phone number: ")
    else:
        phone = sys.argv[1]
   
    parsedPhone = phonenumbers.parse(phone, "US")

    # get raw ########## verson
    rawPhone = phonenumbers.format_number(parsedPhone, phonenumbers.PhoneNumberFormat.E164)
    rawPhone = str(rawPhone.replace("+1", ""))

    # get 1########## version
    onePhone = phonenumbers.format_number(parsedPhone, phonenumbers.PhoneNumberFormat.E164)
    onePhone = str(onePhone.replace("+",""))

    # get ###-###-#### version
    dashPhone = phonenumbers.format_number(parsedPhone, phonenumbers.PhoneNumberFormat.NATIONAL)
    dashPhone = str(dashPhone.replace("(", ""))
    dashPhone = str(dashPhone.replace(")", ""))
    dashPhone = str(dashPhone.replace(" ", "-"))

    # get xcel phone (###)+###+###
    xcelPhone = phonenumbers.format_number(parsedPhone, phonenumbers.PhoneNumberFormat.NATIONAL)
    xcelPhone = str(xcelPhone.replace(" ", "+"))
    xcelPhone = str(xcelPhone.replace("-", "+"))

    # get area code, exchange, station number
    areaPhone = rawPhone[0:3]
    exchangePhone = rawPhone[3:6]
    stationPhone = rawPhone[6:10]
    
    #Call subroutines with phone numbers
    exelon(onePhone)
    rochesterge(areaPhone, exchangePhone, stationPhone)
    nyseg(areaPhone, exchangePhone, stationPhone)
    if phonenumbers.is_valid_number(parsedPhone) == True:
        coned(rawPhone)
    dtenergy(rawPhone)
    xcel(xcelPhone)
    firstenergy(rawPhone)
    aep(rawPhone)