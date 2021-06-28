from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from email.message import EmailMessage
import time
import ast
import smtplib
from getpass import getpass

url = 'https://www.facebook.com'

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--log-level=3')
chrome_options.add_argument('--start-maximized')

while True:
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        print('Entered the FB Login Page\n')
        break
    except:
        print('Error occured while opening webdriver\nTrying again in 2 minutes...')
        time.sleep(120)

time.sleep(2)

email = driver.find_element_by_name("email")
pswrd = driver.find_element_by_name("pass")

while True:
    try:
        # FACEBOOK EMAIL ID INPUT
        print("MAKE SURE TO ENTER CORRECTLY AS IT'LL CRASH IF WRONG INFO GIVEN\n")
        print('Enter your facebook email')
        fb_email = input('Email: ')
        email.send_keys(fb_email)
        print("The email is", fb_email)
        print('Typing Email')
        time.sleep(1)
        # FACEBOOK PASSWORD ID INPUT
        print("\nTo ensure privacy you won't we able to see your password while typin\nSo, type cautiously")
        pswrd.send_keys(getpass())
        print('Typing Password')
        time.sleep(1)
        email.submit()
        print('Submitting')
        time.sleep(2)
        break
    except:
        print('Error occured while submitting\nTrying Again in 2 mins...')
        time.sleep(120)

# HERE INSERT YOUR GROUP PAGE URL
print('\nEnter mbasic URL of the facebook group')
print('Example: https://mbasic.facebook.com/groups/[GROUP_ID]')
print("Make sure you're a member of this group!!")

fb_group_url = input('URL: ')
print("The fb group url is", fb_group_url)

print("\nMAKE SURE TO ENTER CORRECTLY AS IT'LL CRASH IF WRONG INFO GIVEN")
print("Enter the email (has to be gmail) using which you want to send the post updates")
sender_email = input('Email: ')
print("The sender email is", sender_email)

print("\nTo ensure privacy you won't we able to see your password while typin\nSo, type cautiously")
print(
    f"\nPlease enter the password of '{sender_email}' email to send the new post: ")
sender_pass = getpass()

print("\nEnter the email where you'll receive the post updates")
receiver_email = input('Email: ')

first = False
with open("fb_grp_post_ids.txt", mode='r') as old_ids_file:
    if len(old_ids_file.readlines()) == 0:
        first = True
    else:
        print("\nPost ids are already generated\nWill send an email whenever any new posts arrive from now on\n")

while True:

    print('Looking for updates\n')

    try:
        driver.get(fb_group_url)
    except:
        print("Could not enter the FB Group Page\nTrying again in 2 mins...")
        time.sleep(120)
        continue
    print('Entered the FB Group page\n')

    soup = BeautifulSoup(driver.page_source, 'lxml')

    all_group_posts = soup.find('div', id='m_group_stories_container')
    all_articles = all_group_posts.find_all('article')

    new_ids = []
    #ss_ids = []

    for article in all_articles:
        article_data_dict = ast.literal_eval(article['data-ft'])
        new_ids.append(article_data_dict['top_level_post_id'])
        # ss_ids.append(article['id'])

    if first:
        # this means this code is running for the
        # so wrtie the ids in the empty file
        print("\nRunning for the first time.")
        print("So, generating the current posts ids.\nWill send an email whenever any new posts arrive from now on\n")
        with open('fb_grp_post_ids.txt', mode='w', encoding='utf-8') as write_file:
            for article in all_articles:
                write_file.write(f"====POST_ID====\n")
                article_info = ast.literal_eval(article['data-ft'])
                write_file.write(article_info['top_level_post_id'])
                write_file.write("\n")

        print('Will wait for 30 mins then check again')
        print("\n30 mins left...")
        time.sleep(300)
        print("\n25 mins left...")
        time.sleep(300)
        print("\n20 mins left...")
        time.sleep(300)
        print("\n15 mins left...")
        time.sleep(300)
        print("10 mins left...")
        time.sleep(300)
        print("5 mins left...\n")
        time.sleep(300)
        continue

    else:
        with open("fb_grp_post_ids.txt", mode='r') as old_ids_file:
            old_ids = [id[:-1]
                       for i, id in enumerate(old_ids_file.readlines()) if i % 2 == 1]

    new_post = False
    # Iterating through the new ids
    new_post_count = 1
    for idx, id in enumerate(new_ids):
        if id not in old_ids:
            new_post = True
            ######################
            print("NEW POST ALERT!!!\n")

            whole_email = EmailMessage()
            whole_email['From'] = sender_email
            whole_email['To'] = receiver_email
            whole_email['Subject'] = 'New Post from ECO101 Facebook Group'
            #######################

            print(f"Trying to Enter the new post#{new_post_count} link\n")
            driver.get(fb_group_url + '/permalink/' + str(id))
            time.sleep(3)
            print(f"Entered the new post#{new_post_count} link")
            whole_email.add_alternative(driver.page_source, subtype='html')

            # Preparing to take the exact screenshot of the new post
            def S(X): return driver.execute_script(
                'return document.body.parentNode.scroll' + X)
            driver.set_window_size(S('Width'), S('Height'))

            element = driver.find_element_by_id('m_story_permalink_view')
            print(f'Taking the Screenshot of post#{new_post_count}')
            ss_name = "new_post#" + str(new_post_count) + ".png"
            element.screenshot(ss_name)
            print(f'Screenshot of the post#{new_post_count} taken\n')

            # Reading the image file and attaching it with the email
            with open(ss_name, mode='rb') as pic:
                data = pic.read()
                data_name = pic.name
                data_type = 'png'
                whole_email.add_attachment(data, maintype='image',
                                           subtype='png', filename=data_name)
            new_post_count += 1

            if new_post:
                try:
                    print('Trying to send the email')
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                        smtp.login(sender_email, sender_pass)
                        smtp.send_message(whole_email)
                        print('Email sent :D\n')

                    # Now that the email has been sent
                    # we can surely update the old_ids
                    with open('fb_grp_post_ids.txt', mode='a', encoding='utf-8') as write_file:
                        write_file.write(f"====POST_ID====\n")
                        write_file.write(id)
                        write_file.write("\n")
                except:
                    print(
                        "Couldn't send the email for some reason :').. Trying again in 2 mins")
                    time.sleep(120)
                    # starting from the beginning to check ids and send the email
                    break

    if not new_post:
        print('\nNo updates...')

    print('Will wait for 30 mins then check again')
    print("\n30 mins left...")
    time.sleep(300)
    print("\n25 mins left...")
    time.sleep(300)
    print("\n20 mins left...")
    time.sleep(300)
    print("\n15 mins left...")
    time.sleep(300)
    print("10 mins left...")
    time.sleep(300)
    print("5 mins left...\n")
    time.sleep(300)

driver.quit()
