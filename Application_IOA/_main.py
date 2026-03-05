from Slack_CS import *
import time
import gc

"""
Looking for all instances of a name matching with regex

1. Search for Apps from the provided keywords
2. Save JSON in a file
3. Extract necessary fields and create the list with all application names to be used in regex
      1. From App_Details_Processing.py
4. Take App Name, process the names and creates regex for Process Creation like ".*Battle\.net.*"
5. Call the creation of Rules in Custom_IOA.py
"""

slack_obj = SlackIntergationClass()

while True:

    slack_obj.retrieve_last_message()
    slack_obj.clean_app_file()
    #wait 1 min
    time.sleep(60)

#Clean up all unsued objects
# del obj

#Garbage collector
# gc.collect()



