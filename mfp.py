#! /usr/bin/env python3.6
# Program for sending data to myfitnesspal
# Author: Dan Whaley https://hypothes.is
# Author: Aleksandar Josifoski https://about.me/josifsk
# 2018 April 30 started;

fparamname = 'mfp_parameters.py'
# dir_in is directory where project files are placed. Don't forget ending slash /
dir_in = '/home/mfp/mfp/'

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import datetime
import time
import html
import os
import re
import sys
import codecs
import random
import ntpath
import glob
import traceback

#reading parameters file
print("loading " + fparamname)
with codecs.open(dir_in + fparamname, "r", "utf-8") as fp:
    sparam = ''
    for line in fp:
        if len(line.strip()) > 0:
            if not line.strip()[0] == '#':
                sparam += line
    try:
        dparameters = dict(eval(sparam))
    except Exception as e:
        print(str(e))
        now = str(datetime.datetime.now())[:16]
        sys.exit()

mfpusername = dparameters["mfpusername"].strip()
mfppassword = dparameters["mfppassword"].strip()
command_wait = dparameters["command_wait"]
timeout = dparameters["timeout"]
geckodriverexcecutablePath = dparameters["geckodriverexcecutablePath"].strip()
usegecko = dparameters["usegecko"]
ffProfilePath = dparameters["ffProfilePath"]
ffWidth = dparameters["ffWidth"]
ffHeight = dparameters["ffHeight"]

allow_selenium = True
script_name = sys.argv[0].split('.')[0]
logfile_name = script_name + '_log.txt'
oldPrint = print
def print(*args, **kwargs):
    '''This function prints both on stdout and log file'''
    now = str(datetime.datetime.now())[:16]
    with open(dir_in + logfile_name, 'a') as fout:
        fout.write(now + " ")
        fout.write(*args, **kwargs)
        fout.write(os.linesep)
        oldPrint(*args, **kwargs)

time1 = time.time()
counter = 0
driver = None
wait = None
mynext = 1

def write_responses(response):
    ''' function to write responses in responses.txt '''
    global mynext
    with codecs.open(dir_in + 'responses/' + 'response_%09d' % mynext + '.txt', 'w', 'utf-8') as fcresp:
        fcresp.write(response)
        mynext += 1

def save_response_to_file(text):
    '''temporary function to analyse html response'''
    with codecs.open(dir_in + "rawresponse.txt", "w", "utf-8") as fresp:
        fresp.write(html.unescape(text))

def waitForLoadbyXpath(xpath):
    '''function to wait until web element is available via xpath check'''
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        return True
    except:
        return False

def openurl(url):
    '''function to open url using selenium'''
    try:
        driver.get(url)
        print('loading ' + url)
    except Exception as e:
        print(str(e))
        write_responses(str(e))

def scroll_down(sbypx):
    '''function to scroll by sbypx pixels'''
    driver.execute_script("window.scrollBy(0, %d);" % (sbypx))
    time.sleep(0.3)

def setbrowser():
    ''' function for preparing browser for automation '''
    print("Preparing browser")
    global driver
    global wait
    profile = webdriver.FirefoxProfile(profile_directory = ffProfilePath)
    capabilities = DesiredCapabilities.FIREFOX
    if usegecko:
        capabilities["marionette"] = True
    driver = webdriver.Firefox(firefox_profile = profile,
                               capabilities = capabilities,
                               executable_path = geckodriverexcecutablePath)
    driver.set_window_size(ffWidth, ffHeight)
    driver.implicitly_wait(timeout)
    wait = WebDriverWait(driver, timeout)

def is_element_present(xpath):
    '''checking is element present based on xpath'''
    try:
        driver.find_element_by_xpath(xpath)
        bprocess = True
    except:
        bprocess = False
    return bprocess
    
def scroll_element_into_view(element):
    """Scroll element into view"""
    x = element.location['x']
    driver.execute_script('window.scrollTo({0}, 0)'.format(x))
    y = element.location['y']
    driver.execute_script('window.scrollTo(0, {0})'.format(y))

def highlight(element):
    """Highlights (blinks) a Selenium webdriver element"""
    driver = element._parent

    def apply_style(s):
        driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, s)

    original_style = element.get_attribute('style')
    apply_style("background: yellow; border: 2px solid red;")
    time.sleep(3)
    apply_style(original_style)    

def check_login():
    ''' function for checking login status on myfitnesspal and if needed login inside '''
    
    xpath = "/html/body/div[2]/ul/li[5]/a" # If element exists shows Logout text on page
    if is_element_present(xpath):
        # We are alrady login
        print("We are already login")
    else:
        # procedure for login
        xpath = "/html/body/div[3]/div/ul/li[8]/a"
        try:
            el = driver.find_element_by_xpath(xpath)
            el.click()
            time.sleep(1)
            xpath = '//input[@name="username"]'
            el = driver.find_element_by_xpath(xpath)
            el.clear()
            el.send_keys(mfpusername)
            time.sleep(1)
            xpath = '//input[@name="password"]'
            el = driver.find_element_by_xpath(xpath)
            el.clear()
            el.send_keys(mfppassword)
            time.sleep(1)
            xpath = '//input[@value="Log In"]'
            el = driver.find_element_by_xpath(xpath)
            el.click()
        except Exception as e:
            print(str(e))
            write_responses(str(e))

    time.sleep(2)

def remove_lines(f, lrnl):
    ''' function to remove lines in text files '''
    fin = codecs.open(f, 'r', 'utf-8')
    temp = codecs.open(dir_in + 'temp', 'w', 'utf-8')
    j = 0
    for line in fin:
        j += 1
        if str(j) in lrnl:
            pass
        else:
            temp.write(line)
    fin.close()
    os.remove(f)
    os.rename(dir_in + 'temp', f)
    pout = str(lrnl) + ' lines removed from notes file'
    print(pout)
    write_responses(pout)
    
def convert_to_oz(nq, sq):
    ''' function to convert quantities in oz format 
    function is invoked with stopcommand, ozs = convert_to_oz(nq, sq)'''
    global fixedterm
    fixedterm = None
    try:
        some = dq[sq]
    except:
        fixedterm = sq
        return False, None
        
    if not nq.strip().replace(',', '').replace('.', '').isdigit():
        pout = "You'll need to set numeric value for servings. Nothing executed."
        print(pout)
        write_responses(pout)
        return True, None
        
    if len(dq[sq].strip().split()) == 2:
        num = dq[sq].strip().split()[0]
        try:
            ozs = round(float(nq) * float(num), 2)
        except Exception as e:
            print('mapping of ' + sq + ' is not correct')
            write_responses(str(e))
        pout = 'ounces of ' + str(nq) +  ' ' + sq + ' '  + str(ozs)
        print(pout)
        return False, str(ozs)
    elif dq[sq].strip().lower() == 'skip':
        fixedterm = sq.strip()
        return False, None
    elif dq[sq].strip().lower() == 'first':
        fixedterm = 'first'
        return False, None
    
def convert_ozs_100g(ozs):
    return str(round(float(ozs) * 0.283, 2))

def convert_ozs_lbs(ozs):
    return str(round(float(ozs) * 0.0625, 2))

def convert_ozs_gr(ozs):
    return str(round(float(ozs) * 28.3, 2))

def convert_ozs_ml(ozs):
    return str(round(float(ozs) * 29.5735, 2))

def convert_ozs_100ml(ozs):
    return str(round(float(ozs) * 0.295735, 2))

def convert_ozs_tbsp(ozs):
    return str(round(float(ozs) * 2, 2))

def convert_ozs_tsp(ozs):
    return str(round(float(ozs) * 6, 2))


def num_quant(selel, ozs, nq, sq, lqvalues, terms, eldescription):
    ''' function to process quantities '''
    
    global fixedterm

    goingon = True
    if ozs:
        if "1 oz(s)" in lqvalues:
            setquant = ozs
            selel.select_by_visible_text("1 oz(s)")
            qv = "1 oz(s)"
            return setquant, qv, goingon
        elif "1 oz" in lqvalues:
            setquant = ozs
            selel.select_by_visible_text("1 oz")
            qv = "1 oz"
            return setquant, qv, goingon
        elif "1 ounce" in lqvalues:
            setquant = ozs
            selel.select_by_visible_text("1 ounce")
            qv = "1 ounce"
            return setquant, qv, goingon
        elif "100 grams" in lqvalues:
            setquant = convert_ozs_100g(ozs)
            selel.select_by_visible_text("100 grams")
            qv = "100 grams"
            return setquant, qv, goingon
        elif "100 gram" in lqvalues:
            setquant = convert_ozs_100g(ozs)
            selel.select_by_visible_text("100 gram")
            qv = "100 grams"
            return setquant, qv, goingon
        elif "100 gr" in lqvalues:
            setquant = convert_ozs_100g(ozs)
            selel.select_by_visible_text("100 gr")
            qv = "100 gr"
            return setquant, qv, goingon
        elif "100 g(s)" in lqvalues:
            setquant = convert_ozs_100g(ozs)
            selel.select_by_visible_text("100 g(s)")
            qv = "100 g(s)"
            return setquant, qv, goingon
        elif "100 g" in lqvalues:
            setquant = convert_ozs_100g(ozs)
            selel.select_by_visible_text("100 g")
            qv = "100 g"
            return setquant, qv, goingon
        elif "1 lb(s)" in lqvalues:
            setquant = convert_ozs_lbs(ozs)
            selel.select_by_visible_text("1 lb(s)")
            qv = "1 lb(s)"
            return setquant, qv, goingon
        elif "1 lb" in lqvalues:
            setquant = convert_ozs_lbs(ozs)
            selel.select_by_visible_text("1 lb")
            qv = "1 lb"
            return setquant, qv, goingon
        elif "1 gram(s)" in lqvalues:
            setquant = convert_ozs_gr(ozs)
            selel.select_by_visible_text("1 gram(s)")
            qv = "1 gram(s)"
            return setquant, qv, goingon
        elif "1 gram" in lqvalues:
            setquant = convert_ozs_gr(ozs)
            selel.select_by_visible_text("1 gram")
            qv = "1 gram"
            return setquant, qv, goingon
        elif "1 gr" in lqvalues:
            setquant = convert_ozs_gr(ozs)
            selel.select_by_visible_text("1 gr")
            qv = "1 gr"
            return setquant, qv, goingon
        elif "1 g" in lqvalues:
            setquant = convert_ozs_gr(ozs)
            selel.select_by_visible_text("1 g")
            qv = "1 g"
            return setquant, qv, goingon
        elif "1 fluid ounce" in lqvalues:
            setquant = ozs
            selel.select_by_visible_text("1 fluid ounce")
            qv = "1 fluid ounce"
            return setquant, qv, goingon
        elif "1 milliliter" in lqvalues:
            setquant = convert_ozs_ml(ozs)
            selel.select_by_visible_text("1 milliliter")
            qv = "1 milliliter"
            return setquant, qv, goingon
        elif "1 ml(s)" in lqvalues:
            setquant = convert_ozs_ml(ozs)
            selel.select_by_visible_text("1 ml(s)")
            qv = "1 ml(s)"
            return setquant, qv, goingon
        elif "1 ml" in lqvalues:
            setquant = convert_ozs_ml(ozs)
            selel.select_by_visible_text("1 ml")
            qv = "1 ml"
            return setquant, qv, goingon
        elif "100 ml(s)" in lqvalues:
            setquant = convert_ozs_100ml(ozs)
            selel.select_by_visible_text("100 ml(s)")
            qv = "100 ml(s)"
            return setquant, qv, goingon
        elif "100 ml" in lqvalues:
            setquant = convert_ozs_100ml(ozs)
            selel.select_by_visible_text("100 ml")
            qv = "100 ml"
            return setquant, qv, goingon
        elif "1 tbsp(s)" in lqvalues:
            setquant = convert_ozs_tbsp(ozs)
            selel.select_by_visible_text("1 tbsp(s)")
            qv = "1 tbsp(s)"
            return setquant, qv, goingon
        elif "1 tbsp" in lqvalues:
            setquant = convert_ozs_tbsp(ozs)
            selel.select_by_visible_text("1 tbsp")
            qv = "1 tbsp"
            return setquant, qv, goingon
        elif "1 tsp(s)" in lqvalues:
            setquant = convert_ozs_tsp(ozs)
            selel.select_by_visible_text("1 tsp(s)")
            qv = "1 tsp(s)"
            return setquant, qv, goingon
        elif "1 tsp" in lqvalues:
            setquant = convert_ozs_tsp(ozs)
            selel.select_by_visible_text("1 tsp")
            qv = "1 tsp"
            return setquant, qv, goingon
        else:
            pout = eldescription + ' not added. \nAvailable quantities descriptions are:\n' + str(lqvalues) + \
            '\nTry some of this match commands:\n(Do not forget to adjust servings)\n'
            for lqval in lqvalues:
                pout += 'm ' + terms + ' @ ' + nq + ' ' + lqval + '\n'
            print(pout)
            write_responses(pout)
            goingon = False
            return None, None, False
    else:
        setquant = nq
        qv = lqvalues[0]
        selel.select_by_visible_text(lqvalues[0])
        return setquant, qv, goingon
    
def write_map_food(key, nq, sq, bopenpages):
    ''' this is function to write in mfp today foods using mappings '''

    stopcommand, ozs = convert_to_oz(nq, sq)
    if stopcommand:
        return None
    if bopenpages:
        url = 'https://www.myfitnesspal.com/food/diary'
        openurl(url)
        time.sleep(1)
        url = 'https://www.myfitnesspal.com/food/add_to_diary?' + 'date=' + today_date() + '&meal=0'
        openurl(url)
        time.sleep(1)
    xpath = '//input[@id="search"]'
    waitForLoadbyXpath(xpath)

    # Enter searching terms in box
    el = driver.find_element_by_xpath(xpath)
    el.clear()
    el.send_keys(dmap[key])
    time.sleep(1)

    # click on green Search button
    xpath = '//input[@value="Search"]'
    el = driver.find_element_by_xpath(xpath)
    el.click()
    
    xpath = '//li[@class="matched-food"]'
    waitForLoadbyXpath(xpath)
    elresults = driver.find_elements_by_xpath(xpath)
    print(str(len(elresults)) + '*' * 100)
    if len(elresults) > 0:
        el = elresults[0]
        el.click()
        time.sleep(0.7)
        elhtml = el.get_attribute('innerHTML')
        soup = BeautifulSoup(elhtml, 'html.parser')
        a = soup.find("a").text.strip()
        try:
            p = soup.find("p").text.strip()
            out = a + ' ' + p
        except:
            out = a
            
        eldescription = out
        pout = 'First hit in database is ' + eldescription
        print(pout)
        
        scroll_down(200)
        time.sleep(0.2)
        
        xpath = '//form//select[@id="food_entry_weight_id"]'
        waitForLoadbyXpath(xpath)
        selel = Select(driver.find_element_by_xpath(xpath))
        getavailquant = driver.find_element_by_xpath(xpath).get_attribute("innerHTML")
        soup = BeautifulSoup(str(getavailquant), 'html.parser')
        lqvalues = []
        soupoptions = soup.find_all('option')
        for option in soupoptions:
            lqvalues.append(option.text.strip())

        goingon = True
        setquant, qv, goingon = num_quant(selel, ozs, nq, sq, lqvalues, dmap[key], eldescription)

        if goingon:
            xpath = '//form//input[@id="food_entry_quantity"]'
            el = driver.find_element_by_xpath(xpath)
            el.clear()
            el.send_keys(setquant)
            time.sleep(0.2)
    
            xpath = '//form//input[@id="update_servings"]'
            el = driver.find_element_by_xpath(xpath)
            time.sleep(1)
            el.click()
            
            wait_for_calendar()
            
            # get calories
            remlen = num_of_entered_foods_for_today()
            eldescription, calories = get_food_calories(remlen + 1)

            pout = 'Added (database)' + ': ' + eldescription + ' (' + setquant + 'x ' + qv + ') ' + calories + ' KCal'
            
            print(pout)
            write_responses(pout)

    else:
        out = key
        pout = 'Nothing found in db for ' + out + ' Correct searching description.'
        print(pout)
        write_responses(pout)
            
def parse_recfreq(terms, nq, sq, searchonly):
    ''' Function to get items in recent, frequent, my foods, meals, recipies and find first hit '''

    if not searchonly:
        stopcommand, ozs = convert_to_oz(nq, sq)
    else:
        stopcommand = False
    if stopcommand:
        return None
    print('searching for ' + terms)
    url = 'https://www.myfitnesspal.com/food/diary'
    openurl(url)
    time.sleep(1)
    url = 'https://www.myfitnesspal.com/food/add_to_diary?' + 'date=' + today_date() + '&meal=0'
    openurl(url)
    time.sleep(1)
    xpath = '//input[@id="search"]'
    waitForLoadbyXpath(xpath)
    
    idtabs = ["recent_tab", "frequent_tab", "my_foods_tab", "meals_tab", "recipes_tab"]
    divs = ["10", "9", "8", "7", "6"]
    tabxpaths = [
        '//form/div[2]/div/ul/li[5]/a',
        '//form/div[2]/div/ul/li[4]/a',
        '//form/div[2]/div/ul/li[3]/a',
        '//form/div[2]/div/ul/li[2]/a',
        '//form/div[2]/div/ul/li[1]/a'
    ]
    
    for counter, tab in enumerate(idtabs, start=0):
        loopNextPageCondition = True
        # is there next page
        there_was_next_page = False
        jnext = 0
        prevnextplen = 0

        el = driver.find_element_by_xpath(tabxpaths[counter])
        el.click()
        time.sleep(0.8)
        
        print("Searching in " + tab)
        while loopNextPageCondition:
            xpath = '//*[@class="next_page" and contains(.,"Next »")]'
            
            nextels = driver.find_elements_by_xpath(xpath)
            print('nextels len = ' + str(len(nextels)) + '*' * 100)
            if len(nextels) > prevnextplen:
                nextp = nextels[-1]
                prevnextplen = len(nextels)
                print('there is next page')
                jnext += 1
                xpathPrefix = "//div[" + divs[counter] + "]/div[" + str(jnext) + "]"
                there_was_next_page = True

            else:
                if not there_was_next_page:
                    xpathPrefix = "//div[" + divs[counter] + "]/div"
                else:
                    jnext += 1
                    xpathPrefix = "//div[" + divs[counter] + "]/div[" + str(jnext) + "]"
                nextp = None

            i = 1
            xpath = xpathPrefix + '/table/tbody//td[2]'
            els = driver.find_elements_by_xpath(xpath)
            print('There are ' + str(len(els)) + ' descriptions on this page')
            for j, elDescription in enumerate(els, start=1):
                text = elDescription.text.lower()

                l = terms.split()
                found = True
                for item in l:
                    item = item.strip('.,;')
                    if item.lower() not in text:
                        found = False
                        break

                if found:
                    if not searchonly:
                        xpath = xpathPrefix + '/table/tbody/tr[' + str(j) + ']/td[1]'
                        el = driver.find_element_by_xpath(xpath)
                        el.click()
                    xpath = xpathPrefix + '/table/tbody/tr[' + str(j) + ']/td[2]'
                    eldescription = driver.find_element_by_xpath(xpath).get_attribute("innerHTML").strip()
                    if jnext > 0:
                        pout = terms + ' found in ' + tab + ' page ' + str(jnext) + ' as ' + eldescription
                    else:
                        pout = terms + ' found in ' + tab + ' as ' + eldescription
                    print(pout)
                    if searchonly:
                        write_responses(pout)
                    else:
                        # checking quantity values
                        xpath = xpathPrefix + '/table/tbody/tr[' + str(j) + ']/td[3]/select'
                        selel = Select(driver.find_element_by_xpath(xpath))
                        
                        getavailquant = driver.find_element_by_xpath(xpath).get_attribute("innerHTML")
                        soup = BeautifulSoup(str(getavailquant), 'html.parser')
                        lqvalues = []
                        soupoptions = soup.find_all('option')
                        for option in soupoptions:
                            lqvalues.append(option.text.strip())
    
                        goingon = True
                        setquant, qv, goingon = num_quant(selel, ozs, nq, sq, lqvalues, terms, eldescription)
                        if goingon:
                            xpath = xpathPrefix + '/table/tbody/tr[' + str(j) + ']/td[3]/input'
                            el = driver.find_element_by_xpath(xpath)
                            el.clear()
                            el.send_keys(setquant)
                            time.sleep(0.2)
                    
                            xpath = '//*[@id="add_button_en"]'
                            el = driver.find_element_by_xpath(xpath)
                            time.sleep(1)
                            el.click()
                            
                            # wait for calendar to be loaded
                            wait_for_calendar()
                            
                            # get calories
                            remlen = num_of_entered_foods_for_today()
                            eldescription, calories = get_food_calories(remlen + 1)
                            
                            pout = 'Added (' + tab + '): ' + eldescription + ' (' + setquant + 'x ' + qv + ') ' + \
                            calories + ' KCal' 
                            print(pout)
                            write_responses(pout)
                            
                            # food added, so no need for further more searching
                            return None
                        else:
                            # food found, but incompatible quantity term, no need for more searching
                            return None

            if nextp:
                loopNextPageCondition = True
                print('Next page')
                try:
                    nextp.click()
                except:
                    loopNextPageCondition = False
                time.sleep(0.8)
            else:
                loopNextPageCondition = False

    if not searchonly:
        pout = 'Nothing found in recent/frequent/myfoods/meals/recipes, hitting now db'
        print(pout)
        dmap[terms] = terms
        write_map_food(terms, nq, sq, False)
    else:
        pout = 'searchtabs ' + terms + ' completed.'
        print(pout)
        write_responses(pout)
    
def wait_for_calendar():
    ''' next xpath is for waiting for datepicker ie. calendar to be loaded '''
    xpath = '//i[@id="datepicker-trigger"]'
    waitForLoadbyXpath(xpath)
    
def opentoday():
    ''' function to open mfp today page with list of added foods '''
    url = 'https://www.myfitnesspal.com/food/diary/'
    openurl(url)
    time.sleep(1)
    wait_for_calendar()
    
def get_food_calories(i):
    ''' function to get items for food description and calories from today list '''
    xpath = '//table/tbody/tr[' + str(i) + ']/td[1]/a'
    el = driver.find_element_by_xpath(xpath)
    eldescription = el.text
    xpath = '//table/tbody/tr[' + str(i) + ']/td[2]'
    el = driver.find_element_by_xpath(xpath)
    calories = el.text
    return eldescription, calories
    
def num_of_entered_foods_for_today():
    ''' function to get number of entered foods for today list '''
    url = 'https://www.myfitnesspal.com/food/diary?date=' + today_date()
    openurl(url)
    time.sleep(1)
    wait_for_calendar()
    xpath = '//tbody/tr//td[8]/a/i'
    els = driver.find_elements_by_xpath(xpath)
    remlen = len(els)
    print('len(els)=' + str(remlen))
    return remlen
    
    
def process_today(tolist, removelast, statusonly):
    ''' function to deal with today items
    this is how it's invoked from undo command:  process_today(tolist = False, removelast = True, statusonly = False)
    this is how it's invoked from lt command:    process_today(tolist = True, removelast = False, statusonly = False)
    this is how it's invoked from match command: process_today(tolist = True, removelast = False, statusonly = True)
    this is how it's invoked from status command:process_today(tolist = True, removelast = False, statusonly = True)'''
    try:
        remlen = num_of_entered_foods_for_today()

        if removelast:
            if remlen > 0:
                xpath = '//tbody/tr//td[8]/a/i'
                els = driver.find_elements_by_xpath(xpath)
                eldescription, calories = get_food_calories(remlen + 1)
                els[-1].click() # remove link
                time.sleep(1)
                wait_for_calendar()
                
                xpath =  '//table/tbody/tr[' + str(remlen + 3) + ']/td[2]'
                el = driver.find_element_by_xpath(xpath)
                nowcal = el.text
                
                xpath =  '//table/tbody/tr[' + str(remlen + 4) + ']/td[2]'
                el = driver.find_element_by_xpath(xpath)
                goalcal = el.text
                
                xpath =  '//table/tbody/tr[' + str(remlen + 5) + ']/td[2]'
                el = driver.find_element_by_xpath(xpath)
                remainingcal = el.text                
                
                # send response info
                pout = 'Removed last food:\n' + eldescription + ' ' + '-' + calories + ' KCal ' + os.linesep + \
                'Now ' + remainingcal + ' KCal left (Total ' + nowcal + ' of ' + goalcal + ' Goal)'
                print(pout)
                write_responses(pout)
            else:
                pout = 'No more foods in today list to be removed'
                print(pout)
                write_responses(pout)
        if tolist:
            pout = ''
            if not statusonly:
                for i in range(2, remlen + 2):
                    eldescription, calories = get_food_calories(i)
                    pout += '[' + str(i-1) + '] ' + eldescription + ' ' + calories + ' KCal' + os.linesep

            xpath =  '//table/tbody/tr[' + str(remlen + 4) + ']/td[2]'
            el = driver.find_element_by_xpath(xpath)
            nowcal = el.text
            
            xpath =  '//table/tbody/tr[' + str(remlen + 5) + ']/td[2]'
            el = driver.find_element_by_xpath(xpath)
            goalcal = el.text
            
            xpath =  '//table/tbody/tr[' + str(remlen + 6) + ']/td[2]'
            el = driver.find_element_by_xpath(xpath)
            remainingcal = el.text

            pout += 'Now ' + remainingcal + ' KCal left (Total ' + nowcal + ' of ' + goalcal + ' Goal)'
                
            print(pout)
            write_responses(pout)
    except Exception as e:
        pout = str(e)
        print(pout)
        write_responses(pout)
        if 'Tried to run command without establishing a connection'.lower() in pout.lower():
            pout = 'Connection in firefox was lost. Reconnecting..'
            print(pout)
            write_responses(pout)
            setbrowser()
            url = "https://www.myfitnesspal.com"
            openurl(url)
            check_login()
        
def show_search_results(x, itorange):
    ''' function to show found results from search command '''
    global ds
    global search_index
    dskeys = ds.keys()
    if x + 9 > itorange:
        towhat = itorange
    else:
        towhat = x + 9
    if itorange > 0 and x > 0:
        glueout = 'Showing ' + str(x) + '-' + str(towhat) + ' of ' + str(itorange) + os.linesep 
        for i in range(x-1, x + 9):
            try:
                preffixedi = '%03d' % (i + 1)
                glueout += ds[preffixedi] + os.linesep
            except:
                pass
        print(glueout)
        write_responses(glueout)
        
def today_date():
    """ function to get today's date """
    now = str(datetime.datetime.now())[:10]
    return now.strip()

def put_info(line):
    '''  this is main function for processing line '''
    global prev_command
    global bozconvert
    global ds
    global search_index
    global torange
    
    lallowed_commands = ['help', 'm', 'match', 'lt', 'listtoday', 'sn', 'searchnotes', 'sm', 'searchmap','cs', 'status', 'n', 'note', 'map', 'dbmap', 'fm', 'frommap', 'undo', 'lqr', 'listquantityrelations', 'rnl', 'removenoteslines', 's', 'sdb', 'search', 'st', 'searchtabs', 'next', 'more', 'prev']
    
    line = line.strip()
    print(line + ' >>>')
    l = line.split()
    
    if l[0].lower() not in lallowed_commands:
        print(l[0] + ' is not recognizible command')
        write_responses(l[0] + ' is not recognizible command')
        return None

    # help
    if l[0].lower() == 'help':
        try:
            if len(l) == 1:
                with codecs.open(dir_in + 'help_commands.txt', 'r', 'utf-8') as fhelp:
                    help = fhelp.read()
                    print(help)
                    write_responses(help)
        except Exception as e:
            print(str(e))
            print('probably help_commands.txt is not existing or not in path')
            write_responses(str(e))
    
    # m, match (Adding food Example: m banana, raw 15 oz) [It will seek in recent/frequent/myfoods/meals/recipes]
    if l[0].lower() in ('m', 'match'):
        if len(l) > 1:
            if allow_selenium:
                if '@' not in ' '.join(l[1:]):
                    terms = ' '.join(l[1:])
                    nq = '1'
                    sq = 'first'
                    parse_recfreq(terms, nq, sq, searchonly = False)
                    process_today(tolist = True, removelast = False, statusonly = True)
                else:
                    terms = ' '.join(l[1:]).split('@')[0].replace(',', '').strip().lower()
                    if terms == '':
                        pout = "You didn't entered description for food"
                        print(pout)
                        write_responses(pout)
                    else:
                        try:
                            rawquantity = ' '.join(l[1:]).split('@')[1].strip()
                            nq = rawquantity.split()[0].strip()
                            sq = ' '.join(rawquantity.split()[1:]).strip()
                            if sq == '':
                                sq = 'first'
                            parse_recfreq(terms, nq, sq, searchonly = False)
                            process_today(tolist = True, removelast = False, statusonly = True)
                        except Exception as e:
                            # next lines depends on imported traceback, they show line number in
                            # code where eventual error may occure
                            for frame in traceback.extract_tb(sys.exc_info()[2]):
                                fname, lineno, fn, text = frame
                                print("Error in %s on line %d" % (fname, lineno))
                            pout = ''
                            pout += "Error in %s on line %d" % (fname, lineno) + os.linesep
                            pout += str(e)
                            print(pout)
                            write_responses(pout)
                            if 'Tried to run command without establishing a connection'.lower() in pout.lower():
                                pout = 'Connection in firefox was lost. Reconnecting..'
                                print(pout)
                                write_responses(pout)
                                setbrowser()
                                url = "https://www.myfitnesspal.com"
                                openurl(url)
                                check_login()
            else:
                pout = 'selenium not allowed'
                print(pout)
                write_responses(pout)
        else:
            pout = "You didn't set any parameters for match command."
            print(pout)
            write_responses(pout)
    
    if l[0].lower() in ('next', 'more'):
        if prev_command in ('next', 'more', 'prev', 's', 'sdb', 'search'):
            if len(ds) > 0:
                search_index += 10
                if search_index <= torange:
                    show_search_results(search_index, torange)
                else:
                    search_index -= 10
                
    if l[0].lower() == 'prev':
        if prev_command in ('next', 'more', 'prev', 's', 'sdb', 'search'):
            if len(ds) > 0:
                search_index -= 10
                if search_index > 0:
                    show_search_results(search_index, torange)
                else:
                    search_index += 10

    if len(l) >= 2:
        # search in db
        if l[0].lower() in ('s', 'sdb', 'search'):
            ds = {}
            search_index = 1
            torange = 0
            if allow_selenium:
                term = ' '.join(l[1:])
                print('searching in db for ' + term)
                url = 'https://www.myfitnesspal.com/food/calorie-chart-nutrition-facts'
                openurl(url)
                time.sleep(1)
                xpath = '//input[@id="search"]'
                el = driver.find_element_by_xpath(xpath)
                el.clear()
                el.send_keys(term)
                time.sleep(0.3)
                xpath = '//input[@value="Search"]'
                el = driver.find_element_by_xpath(xpath)
                el.click()
                time.sleep(2)
                xpath = '//li[@class="matched-food"]'
                els = driver.find_elements_by_xpath(xpath)
                print(str(len(els)) + ' results found')
                glueout = ''
                torange = len(els)
                for i in range(torange):
                    el = els[i]
                    elhtml = el.get_attribute('innerHTML')
                    soup = BeautifulSoup(elhtml, 'html.parser')
                    a = soup.find("a").text.strip()
                    try:
                        p = soup.find("p").text.strip()
                        out = ('[%03d' % (i+1) + '] ' + a + ' ' + p).strip()
                        ds['%03d' % (i+1)] = out
                    except:
                        p = ''
                        out =  ('[%03d' % (i+1) + '] ' + a).strip()
                        ds['%03d' % (i+1)] = out

                # Found foods are placed in dictionary, showing now first 10
                show_search_results(1, torange)
            else:
                write_responses('selenium not allowed')
                
        # searchtabs
        if l[0].lower() in ('st', 'searchtabs'):
            terms = ' '.join(l[1:])
            parse_recfreq(terms, None, None, searchonly = True)
            
        # search in notes
        if l[0].lower() in ('sn', 'searchnotes'):
            notefound = False
            glueoutput = ''
            try:
                with codecs.open(dir_in + 'notes.txt', 'r', 'utf-8') as fnotes:
                    lnotes = fnotes.readlines()
                    j = 0
                    for note in lnotes:
                        j += 1
                        if l[1].lower() in note.lower():
                            notefound = True
                            glueoutput += '[' + str(j) + ']' + ' ' + note.strip() + os.linesep
                if notefound:
                    write_responses(glueoutput)
                else:
                    print('nothing found in notes for ' + str(l[1]))
                    write_responses('nothing found in notes for ' + str(l[1]))
            except Exception as e:
                print(str(e))
                write_responses('notes.txt missing or missing term for search notes')
                
        # rnl (Remove notes lines Example: rnl 3, 5, 8 those lines will be removed. This command is for using after searching notes with sn
        if l[0].lower() in ('rnl', 'removenoteslines'):
            right = ' '.join(l[1:])
            lrnl = right.split(',')
            for ind in range(len(lrnl)):
                lrnl[ind] = lrnl[ind].strip()
            remove_lines(dir_in + 'notes.txt', lrnl)

    # append note
    if l[0].lower() in ('n', 'note'):
        now = str(datetime.datetime.now())[:16]
        now = now.replace('-', '')
        pout = now + ' ' + ' '.join(l[1:])
        with codecs.open(dir_in + 'notes.txt', 'a', 'utf-8') as fnotes:
            fnotes.write(pout + os.linesep)
        print(pout)
        write_responses('Successfully added in notes: ' + pout)

    # calories status
    if l[0].lower() in ('cs', 'status'):
        if allow_selenium:
            print('checking status')
            url = 'https://www.myfitnesspal.com/food/diary/'
            openurl(url)
            time.sleep(1)
            wait_for_calendar()
            process_today(tolist = True, removelast = False, statusonly = True)
        else:
            write_responses('selenium not allowed')

    # undo, remove last added food
    if l[0].lower() == 'undo'.strip():
        if allow_selenium:
            opentoday()
            process_today(tolist = False, removelast = True, statusonly = False)
        else:
            write_responses('selenium not allowed')
            
    # lt [or listtoday] List today entered foods
    if l[0].lower() in ('lt', 'listtoday'):
        if allow_selenium:
            opentoday()
            process_today(tolist = True, removelast = False, statusonly = False)
        else:
            pout = 'selenium is not allowed'
            print(pout)
            write_responses(pout)

    # map (adding manually new mapping example: map eggss : Eggs - Scrambled (whole egg) or map eggsc : Egg, whole, cooked, poached [must have : for separator between key and name in db]
    # map beanspinto : Beans - Pinto, cooked, boiled, with salt
    if l[0] == 'map'.strip():
        if len(l) > 2 and ':' in line:
            try:
                left =  ' '.join(l[1:]).split(':')[0].strip().lower()
                right = ' '.join(l[1:]).split(':')[1].strip()
                if left in dmap.keys():
                    pout = 'mapkey ' + left + " already exist in mappings. You'll have to set other mapkey"
                    print(pout)
                    write_responses(pout)
                    goingon = False
                else:
                    goingon = True
                if goingon:
                    print('Successfully writing ' + left + ' : ' + right + ' in mfp_mappings.txt file')
                    write_responses('Successfully writing ' + left + ' : ' + right + ' in mfp_mappings.txt file')
                    dmap[left] = right
                    dmapkeys = dmap.keys()
                    with codecs.open(dir_in + 'mfp_mappings.txt', 'w', 'utf-8') as fmap:
                        for dmapkey in dmapkeys:
                            fmap.write(dmapkey + ' : ' + dmap[dmapkey] + os.linesep)
            except Exception as e:
                mapelsetext = str(e) + '''not regular line syntax for map'
                example syntax
                map beanspinto : Beans - Pinto, cooked, boiled, with salt
                '''
                print(mapelsetext)
                write_responses(mapelsetext)
        else:
            mapelsetext = '''not regular line syntax for map'
            example syntax
            map beanspinto : Beans - Pinto, cooked, boiled, with salt
            '''
            print(mapelsetext)
            write_responses(mapelsetext)
            
    #fm (adding food via map in today mfp list example: fm peas 1 c [where peas is already present as key in mappings], 1 c means 1 cup)
    if l[0] in ('fm', 'frommap'):
        if len(l) == 4:
            key2add = l[1].strip()
            if key2add.lower() not in dmap.keys():
                pout = key2add + ' is not existing map key in mappings file'
                print(pout)
                write_responses(pout)
            else:
                nq = l[2].strip()
                sq = l[3].strip()
                if nq.isdigit():
                    if sq in dq.keys():
                        if allow_selenium:
                            write_map_food(key2add, nq, sq, True)
                        else:
                            pout = 'selenium is not allowed'
                            print(pout)
                            write_responses(pout)
                    else:
                        pout = sq + ' is not in quantity keys'
                        print(pout)
                        write_responses(pout)
                else:
                    pout = 'third parameter in fm command should be numerical value'
                    print(pout)
                    write_responses(pout)
                
        else:
            print('Not correct fm command')
            write_responses('Not correct fm command')
            
    #dbmap (adding new mapping when previous command was s/sdb/search/more/next/prev example: dbmap  peas : 008 [where 008 is 8.th by sdb listed food])
    if l[0] == 'dbmap':
        if ':' in line:
            if ds != {}:
                dbmapkey = ' '.join(l[1:]).split(':')[0].strip().lower()
                if dbmapkey == '':
                    print("You've set empty mapkey in input. Example: dbmap peas : 007")
                    write_responses("You've set empty mapkey in input. Example: dbmap peas : 007")
                    goingon = False
                else:
                    goingon = True
                if dbmapkey not in dmap.keys() and goingon:
                    try:
                        dbmapvalue = ds[' '.join(l[1:]).split(':')[1].strip()]
                        if ' '.join(l[1:]).split(':')[1].strip() not in ["%03d" % i for i in range(torange + 1)]:
                            pout = 'Wrong refference. Values for refference should be 001 - ' + str('%03d' % torange)
                            print(pout)
                            write_responses(pout)
                            goingon = False
                        else:
                            goingon = True
                        if goingon:
                            dmap[dbmapkey] = ' '.join(dbmapvalue.split()[1:])
                            with codecs.open(dir_in + 'mfp_mappings.txt', 'w', 'utf-8') as fmap:
                                for dmapkey in dmap.keys():
                                    fmap.write(dmapkey + ' : ' + dmap[dmapkey] + os.linesep)
                            pmsg = 'Successfully added in mappings ' + dbmapkey + ' : ' + dmap[dbmapkey]
                            print(pmsg)
                            write_responses(pmsg)
                    except Exception as e:
                        if ' '.join(l[1:]).split(':')[1].strip() not in  ["%03d" % i for i in range(torange + 1)]:
                            pout = 'Wrong refference. Values for refference should be 001 - ' + str('%03d' % torange)
                            print(pout)
                            write_responses(pout)
                        pout = str(e) + ' ' + line + ' is not correct'
                        print(pout)
                        write_responses(pout)
                else:
                    pout = "you've entered existing mapkey " + dbmapkey + " try again with new mapkey after running sdb again" 
                    print(pout)
                    write_responses(pout)
            else:
                pout = 'Previous command was not s/sdb/search/dbmap/more/next/prev'
                print(pout)
                write_responses(pout)
        else:
            pout = 'Missing : in input. Example: dbmap peas : 008' 
            print(pout)
            write_responses(pout)
            
    # lqr  list quantities relations
    if l[0].lower() in ('lqr', 'listquantityrelations'):
        try:
            with codecs.open(dir_in + 'quantities_abbrev.txt', 'r', 'utf-8') as fq:
                ssq = fq.read()
                print(ssq)
                write_responses(ssq)
        except Exception as e:
            print(str(e))
            print('probably quantities_abbrev.txt is not existing or not in path')
            write_responses(str(e) + 'probably quantities_abbrev.txt is not existing or not in path')


    # searchmap abbreviation for search in mfp_mappings.txt file
    # example syntax
    # sm beans
    # it will find all beans regardless in key or description in mfp_mappings.txt
    if l[0] in ('sm', 'searchmap') and len(l) > 1:
        dmapkeys = dmap.keys()
        glueout = ''
        found = False
        for dmapkey in dmapkeys:
            if l[1].strip().lower() in dmapkey.lower() or l[1].strip().lower() in dmap[dmapkey].lower():
                print(dmapkey + ' : ' + dmap[dmapkey])
                glueout += dmapkey + ' : ' + dmap[dmapkey] + os.linesep
                found = True
        if found:
            write_responses(glueout)
        else:
            pout = 'Nothing found in mappings for ' + l[1].strip().lower()
            print(pout)
            write_responses(pout)
            
    prev_command = l[0].lower()

def check_commands():
    ''' This function in some interval (can be set in parameters file in seconds) will check line_commands.txt file
    for eventual new commands. If new command found, will triger system. System will always be active & looged 
    Also function will refresh mfp_mappings.txt and quantities.txt files '''
    
    global mynext
    global firststart
    global dmap # dmap is dictionary for mappings
    global dq   # dq is dictionary for quantities
    if firststart:
        # openning mfp_mappings.txt and populating dmap dictionary
        dmap = {}

        try:
            with codecs.open(dir_in + 'mfp_mappings.txt', 'r', 'utf-8') as fmap:
                for line in fmap:
                    line = line.strip()
                    if len(line) > 0:
                        if line[0] != '#' and ':' in line:
                            dmap[line.split(':')[0].strip()] = line.split(':')[1].strip()
        except Exception as e:
            pout = 'mfp_mappings.txt not found' 
            print(pout)
            write_responses(pout)
        
        # openning quantities_abbrev.txt and populating dq dictionary
        dq = {}
        dq['first'] = 'first'
        try:
            with codecs.open(dir_in + 'quantities_abbrev.txt', 'r', 'utf-8') as fq:
                for line in fq:
                    line = line.strip()
                    if len(line) > 0:
                        if line[0] != '#' and ':' in line:
                            dq[line.split(':')[0].strip()] = line.split(':')[1].strip()
        except Exception as e:
            pout = 'quantities_abbrev.txt not found'
            print(pout)
            write_responses(pout)
    
    if os.path.exists(dir_in + 'command.txt'):
        with codecs.open(dir_in + 'command.txt', 'r', 'utf-8') as fcopen:
            for command in fcopen:
                command = command.strip()
                if command != '':
                    put_info(command)
                    print('waiting for new command')
        os.remove(dir_in + 'command.txt')

    if firststart:
        print('waiting for new command')
        firststart = False
    time.sleep(command_wait)

if __name__ == '__main__':
    dmap = {}
    dq = {}
    ds = {}
    search_index = 1
    torange = 0
    fixedterm = None
    prev_command = ''
    firststart = True
    if allow_selenium:
        setbrowser()
        url = "https://www.myfitnesspal.com"
        openurl(url)
        check_login()
    while True:
        try:
            check_commands()
        except Exception as e:
            # next lines depends on imported traceback, they show line number in
            # code where eventual error may occure
            for frame in traceback.extract_tb(sys.exc_info()[2]):
                fname, lineno, fn, text = frame
                print("Error in %s on line %d" % (fname, lineno))
            pout = 'From main error handler: '
            pout += str(e)
            print(pout)
            write_responses(pout)
            try:
                os.remove(dir_in + 'command.txt')
            except Exception as e:
                pass

    if allow_selenium:
        driver.close()
