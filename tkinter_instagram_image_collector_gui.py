import os
import time

#TKINTER IMPORTS
import tkinter as tk    
from tkinter import ttk    
from tkinter import *
from tkinter import filedialog
from functools import partial #arg in command (button)

#SELENIUM IMPORTS
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

#WebDriverWait IMPORTS
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#REPLACE FOLDER IMPORT
import shutil # to save it locally

#DOWNLOAD IMAGES
import requests

#DB IMPORT
import sqlite3

#CREATE WINDOW
root = Tk()    
root.title("Instagram Image Collector")
root.geometry("320x170")

def error_message_windows(error_message):
    
    #NEW WINDOW
    error_find_images_window = Toplevel(collectorWindow) 
    error_find_images_window.title("Error")
    error_find_images_window.geometry("320x50")

    error_label = Label(error_find_images_window, text=error_message, fg='red', font='Helvetica 9 bold', pady=15)
    error_label.pack()

def open_filedialog(search_word_input):
    collectorWindow.filename = filedialog.askopenfilename( initialdir= os.path.dirname(os.path.realpath(__file__)) + '\\' + search_word_input[1:], title="IMG folder", filetypes=(("jpg files", "*.*"),("all files","*.*")))                           

def search(search_word_input, collectorWindow, collectorWindow_bg_canvas, driver):

    #SEARCHBOX SELECTEREN
    searchbox = WebDriverWait(driver, 10).until( 
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[class='XTCLo x3qfX ']")))

    #SEARCHBOX INVULLEN
    searchbox.clear() #empty input
    keyword = search_word_input
    searchbox.send_keys(keyword) #text in inputfield

    time.sleep(2)

    #CLICK THE FIRST LINK
    searchlink = WebDriverWait(driver, 10).until( 
        EC.presence_of_element_located((By.CSS_SELECTOR, "a[class='-qQT3']"))).click()
    
    time.sleep(3) #wait until images are downloaded on the next page
    
    #GET IMAGES
    driver.execute_script("window.scrollTo(0,4000);") #start scrolling (4 times length of screen )
    images = driver.find_elements_by_tag_name('img') #get images tages
    images = [image for image in images if image.get_attribute('class') == "FFVAD"] #so you don't get the insta logo, etc..
    images = [image.get_attribute('src') for image in images] #turn the img tags into links   #data-src

    #CREATE FOLDER FOR IMAGES
    folder_path = os.path.dirname(os.path.realpath(__file__)) #current path
    folder_path = os.path.join(folder_path, keyword[1:]) # \cat


    if os.path.exists(folder_path): #if exists 
        shutil.rmtree(folder_path)  #replace
        os.makedirs(folder_path)    #create new

    else:
        os.makedirs(folder_path)    #else create


    #CREATE IMAGE SAVENAME
    counter = 0
    
    #SAVE IMAGES
    for image in images:
        name = os.path.join(folder_path, keyword[1:] + str(counter) + '.jpg') #savename
        link = image #src link

        with open(name, 'wb') as f: #create file
            im = requests.get(link)
            f.write(im.content) #response on the .get(), 'content' == bits ('wb') content

        counter += 1

    #OPEN FILE DIALOG BUTTON
    open_filedialog_button = Button(collectorWindow, text="Open Image Folder", width=40, command=lambda: open_filedialog(search_word_input))
    open_filedialog_button_window = collectorWindow_bg_canvas.create_window(15, 90, anchor="nw", window=open_filedialog_button)

    #STOPS WEB DRIVER
    driver.quit()

def save_login_credentials():
    #Create database or connect to one
    conn = sqlite3.connect(os.path.dirname(os.path.realpath(__file__)) + '\login_credentials.db')

    #Create cursor
    c = conn.cursor()

    #Create table
    c.execute(""" CREATE TABLE IF NOT EXISTS credentials (
        username text,
        password text
        ) """)
    
    #Clear DB (only one record/user)
    c.execute("DELETE FROM credentials")

    #Insert into table
    c.execute("INSERT INTO credentials VALUES (:username, :password)",
            {
                'username' : username_input.get(),
                'password' : password_input.get()
            })

    #Commit changes
    conn.commit()

    #Close connection
    conn.close()

def request_used_login_credentials(): #to show credentials inside login inputfields

    #Create database or connect to one
    conn = sqlite3.connect( os.path.dirname(os.path.realpath(__file__)) + '\login_credentials.db')

    #Create cursor
    c = conn.cursor()
    
    #get the count of tables with the name
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='credentials' ''')

    #if the count is 1, then table exists
    if c.fetchone()[0]==1 : 

	    #Request from table
        c.execute("SELECT * FROM credentials LIMIT 1") 
        record = c.fetchall()

        username_record = ''
        password_record = ''

        username_record += str(record[0][0])
        password_record += str(record[0][1])
            
        username_input.insert(0,username_record)
        password_input.insert(0,password_record)

    #Commit changes
    conn.commit()

    #Close connection
    conn.close()

def login():

    #CREATE WEBDRIVER
    PATH = os.path.dirname(os.path.realpath(__file__)) + '\chromedriver.exe'    #Chrome version 88 ChromeDriver 88.0.4324.96
    driver = webdriver.Chrome(PATH)
    driver.set_window_position(-10000,0)   #hide browser window
    driver.get('https://www.instagram.com/') #open browser and tab + visist link

    #ACCEPT COOKIES
    accept_cookies = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "button[class='aOOlW  bIiDR  ']"))).click()

    #LOGIN
    username = WebDriverWait(driver, 10).until(          
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']"))
    )

    password = WebDriverWait(driver, 10).until(          
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']"))
    )

    username.clear()
    password.clear()
    username.send_keys(username_input.get())
    password.send_keys(password_input.get())

    log_in = WebDriverWait(driver, 5).until( #click on inlog button
        EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']"))).click()
        
    time.sleep(3) #wait until page is loaded (button classes are the same on both pages)
    
    try:
        #CHECK IF LOGIN WAS FAILED    (error message on site)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "p[id='slfErrorAlert']")))
    
    except TimeoutException as ex:
    
        #WE ARE LOGGED IN
        save_login_credentials()

        #SAVE LOGIN CREDENTIALS (not now)
        not_now_cookies = WebDriverWait(driver, 5).until( 
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[class='sqdOP yWX7d    y3zKF     ']"))).click()


        #SAVE NOTIFICATIONS (not now)
        not_now_noti = WebDriverWait(driver, 5).until( 
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[class='aOOlW   HoLwm ']"))).click()

        time.sleep(2)

        #NEW WINDOW
        collectorWindow = Toplevel(root)
        collectorWindow.title("Instagram Image Collector")
        collectorWindow.geometry("320x150")

        #ICON
        PATH = os.path.dirname(os.path.realpath(__file__)) + '\instaicon.ico'
        collectorWindow.iconbitmap(PATH)

        #BACKGROUND
        bg = PhotoImage(file= os.path.dirname(os.path.realpath(__file__)) + '\\background.jpg')

        #CANVAS
        collectorWindow_bg_canvas = Canvas(collectorWindow, width=320, height=170)
        collectorWindow_bg_canvas.pack(fill="both", expand=True)
        collectorWindow_bg_canvas.create_image(0,0,image=bg, anchor="nw")

        #SEARCH WORD
        collectorWindow_bg_canvas.create_text(50, 30, text="Search word:", fill='white', font='Helvetica 9 bold')
                
        search_input = Entry(collectorWindow, width=30)
        search_input_window = collectorWindow_bg_canvas.create_window(100, 20, anchor="nw", window=search_input)
        search_input.insert(0, "#")

        #SEARCH BUTTON
        search_button = Button(collectorWindow, text="Search Images", width=25, command=lambda: search(search_input.get(), collectorWindow, collectorWindow_bg_canvas, driver))
        search_button_window = collectorWindow_bg_canvas.create_window(100, 50, anchor="nw", window=search_button)
        
        collectorWindow.mainloop()
    
    else:
        #NEW ERROR WINDOW FOR WRONG LOGIN CREDENTIALS
        error_message_windows("Incorrect Login Credentials")

        #STOPS WEB DRIVER
        driver.quit()

#ICON
PATH = os.path.dirname(os.path.realpath(__file__)) + '\instaicon.ico'
root.iconbitmap(PATH)

#BACKGROUND
bg = PhotoImage(file= os.path.dirname(os.path.realpath(__file__)) + '\\background.jpg')

#CANVAS
bg_canvas = Canvas(root, width=320, height=170)
bg_canvas.pack(fill="both", expand=True)
bg_canvas.create_image(0,0,image=bg, anchor="nw")

#LOGO
bg_canvas.create_text(85, 20, text="Instagram Login:", font='Helvetica 15 bold', fill='white')

#LOGIN CREDENTIAL LABELS
bg_canvas.create_text(40, 60, text="Username:", fill='white', font='Helvetica 9 bold')
bg_canvas.create_text(40, 90, text="Password:", fill='white', font='Helvetica 9 bold')

#LOGIN CREDENTIAL INPUTS
username_input = Entry(root, width=30)
username_input_window = bg_canvas.create_window(80, 50, anchor="nw", window=username_input)
password_input = Entry(root, width=30, show="*")
password_input_window = bg_canvas.create_window(80, 80, anchor="nw", window=password_input)

#USE PASSED LOGIN CREDENTIALS IF THERE ARE ANY
request_used_login_credentials()

#LOGIN BUTTON
login_button = Button(root, text="Login", width=25, command=login)
login_button_window = bg_canvas.create_window(80, 110, anchor="nw", window=login_button)

root.mainloop()
