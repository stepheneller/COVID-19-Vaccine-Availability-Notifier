import sqlite3
from selenium import webdriver
import time
import smtplib

# CONSTANTS
chrome_driver_path = "YOUR CHROME DRIVER PATH"

MODERNA_CODE = "779bfe52-0dd8-4023-a183-457eb100fccc"
PFIZER_CODE = "a84fb9ed-deb4-461c-b785-e17c782ef88b"
J_AND_J_CODE = "784db609-dc1f-45a5-bad6-8db02e79d44"

SENDING_EMAIL = "YOUR EMAIL"
PASSWORD = "YOUR EMAIL PASSWORD"

# Accessing Database
con = sqlite3.connect('PATH TO YOUR DATABASE')
cur = con.cursor()

cur.execute('SELECT * FROM search_parameters')
for row in cur:

    medication_list = []

    if row[1] == 1:
        medication_list.append(MODERNA_CODE)
    else:
        medication_list.append('')
    if row[2] == 1:
        medication_list.append(PFIZER_CODE)
    else:
        medication_list.append('')
    if row[3] == 1:
        medication_list.append(J_AND_J_CODE)
    else:
        medication_list.append('')
    # URL is created from preferences indicated by user while signing up
    URL = f"https://vaccinefinder.org/results/?zipcode={row[4]}&medications={medication_list[0]},{medication_list[1]},{medication_list[2]}&radius={row[5]}"

    driver = webdriver.Chrome(executable_path=chrome_driver_path)
    driver.get(URL)
    time.sleep(3)
    results = driver.find_elements_by_css_selector("p.sc-hlTvYk")
    driver.quit()
    in_stock = False
    for result in results:
        if result.text == "In Stock":
            in_stock = True

    if in_stock:
        with smtplib.SMTP("smtp.gmail.com") as connection:
            # NOTE the URLS in the email below will need to be updated once the website structure is determined
            connection.starttls()
            connection.login(user=SENDING_EMAIL, password=PASSWORD)
            connection.sendmail(from_addr=SENDING_EMAIL, to_addrs=row[6],
                                msg=f"Subject: Vaccine Availability Alert\n\n"
                                    f"There are currently vaccines available based on your preferences.\n"
                                    f"Follow the link below for more information.\n"
                                    f"{URL}\n\n"
                                    f"To update your preferences re-enter your information on the sign up page.\n"
                                    f"{URL}\n\n"
                                    f"To no longer receive notifications click the link below.\n"
                                    f"{URL}/{row[6]}/")
