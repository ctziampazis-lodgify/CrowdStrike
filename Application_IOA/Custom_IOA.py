import re

import split
from falconpy import CustomIOA
import json
from Application_IOA.Logging_file import Logging_Class as logger, Logging_Class
from CONFIG import *

class Custom_IOA:

    def __init__(self, LOGGER):
        try:
            self.LOGGER = LOGGER
            # Initialize the API
            self.falcon_customIOA = CustomIOA(
                client_id= client_id,
                client_secret= client_secret,
            )
            self.LOGGER.get_overall_logger().info("Custom_IOA Obj init - successfully initialized!")
        except Exception as e:
            self.LOGGER.get_overall_logger().warning(f"Failed at init Custom_IOA...{e}")
            raise Exception(f"Failed at init Custom_IOA...{e}")

    def get_rules(self, group_id):
        try:
            # response = falcon.query_rule_types(limit=100)
            print("Getting rules for Group ID: " + str(group_id))
            response = self.falcon_customIOA.get_rule_groups(ids=group_id)

            print(json.dumps(response, indent=4, sort_keys=True))

            #Name of the group
            group_resource_name = response.get('body').get('resources')[0]['name']
            #Platform
            group_resource_platform = response.get('body').get('resources')[0]['platform']
            #Get Rule IDs
            group_rule_ids = response.get('body').get('resources')[0]['rule_ids']
            print("Group Name: " + str(group_resource_name) + "\n" + "Platform: " + str(group_resource_platform) +"\n" + "Rule IDs: " + str(group_rule_ids))

            self.get_rules_by_id(group_rule_ids)
        except Exception as e:
            self.LOGGER.get_overall_logger().warning(f"Failed at get_rules...{e}")

    def get_rules_by_id(self, rule_ids):
        try:
            print("Rules to fetch: " + str(rule_ids))
            rules = self.falcon_customIOA.get_rules_get(ids=rule_ids)
            #print(json.dumps(rules, indent=4, sort_keys=True))
            print("------------ Printing Rules ------------")
            for item in rules.get('body').get('resources'):
                print("Rule Name: " + str(item.get('name')))
                print("Description: " + str(item.get('description')))
                print("Action: " + str(item.get('action_label')))
                print("-------------")
        except Exception as e:
            self.LOGGER.get_overall_logger().warning(f"Failed at get_rules_by_id...{e}")

    # Get IOA Groups
    def get_rule_groups(self):
        '''
        This will return a list of group IDs like the example below

        Example:
        IOA Groups found [
            "78ad80d0536e47b4a6dcd91a654c3a8d", --> App Prevention Mac Focus Group
            "af7164458c9f43b783d6567a36be8f8f", --> Mac General
            "d3f25f740baa44b19f2d36026b955bc4", -->  App Prevention Windows Focus Group
            "f6b898fcf80e4fa8a6ebd74cf05acc02" --> Win General
        ]
        :return:
        '''
        try:
            response = self.falcon_customIOA.query_rule_groups(limit=100)
            #print(response)
            group_resource_ids = response.get('body').get('resources')
            print("IOA Groups found " + json.dumps(group_resource_ids, indent=4, sort_keys=True))
            self.get_rules(group_resource_ids[0])
        except Exception as e:
            self.LOGGER.get_overall_logger().warning(f"Failed at get_rule_groups...{e}")

    def create_custom_rule(self, os_tpye:str, regex_str:str, action:str):
        # Create a RULE Group
        # MAYBE JUST CREATE GROUPS MANUALLY SO THAT WE ARE CERTAIN FOR THE PREVENTION POLICIES SET

        # You need a 'rule_group_id' (found in the Falcon URL when viewing a group)


        # ruletype_id,  Rule Type Name,     Description
        #   1           ,Process Creation,  Detects when a specific process starts (Image Filename, Command Line)."
        #   2           ,File Creation,     Detects when a file is created or written to disk.
        #   3           ,Network Connection,Detects network connections to specific IPs, ports, or by specific processes."

        # for Mac
        # ruletype_id,  Rule Type Name,     Description
        #   5,          Process Creation
        #   6,          File Creation


        #10	Monitor	Records the event in the background for telemetry but does not generate an alert in the Activity console.
        #20	Detect	Generates an alert in the console but allows the process to continue. This is the "Audit" mode.
        #30	Block	Generates an alert and terminates the action (kills the process or prevents the file write).

        try:
            ruletype_id = ""
            RULE_GROUP_ID = ""
            RULE_GROUP_WIN_ID = "d3f25f740baa44b19f2d36026b955bc4"
            RULE_GROUP_MAC_ID = "78ad80d0536e47b4a6dcd91a654c3a8d"
            disposition_id = 20 #default value

            if action == "block":
                disposition_id = 30
            elif action == "detect":
                disposition_id = 20
            elif action == "monitor":
                disposition_id = 10

            #Platform assignment and type of rule assigned
            # FOR NOW: all rules are detecting for File Creation
            if os_tpye == "Win":
                RULE_GROUP_ID = RULE_GROUP_WIN_ID
                ruletype_id = "1"
            elif os_tpye == "Mac":
                RULE_GROUP_ID = RULE_GROUP_MAC_ID
                ruletype_id = "5"
            else:
                print("Unsupported OS Type")

            #Regex creation
            # regex_str = regex_str.replace(".", "\.")
            # regex_str = ".*"+regex_str+".*"

            print("App found: " + os_tpye)
            print("Rule ID: " + str(RULE_GROUP_ID))
            print("Adding: " + str(regex_str))

            #Detailed values
            field_val = {
                    "final_value": regex_str,
                    "label": "Image Filename", # The display string for the field (e.g., "Image Filename").
                    "name": "ImageFilename", # The programmatic identifier used by the sensor (e.g., ImageFilename).
                    "type": "excludable", # Defines the behavior. excludable means you can provide both a value to match and a value to exclude.
                    "value": regex_str,
                    "values": [
                        {
                            "label": "include", #or exclude
                            "value": regex_str
                        }
                    ]
            }

            response = self.falcon_customIOA.create_rule(comment="Testing Rule on Test Group",
                                              description="Does not trigger", #Description
                                              disposition_id=disposition_id,
                                              pattern_severity="low",
                                              field_values=field_val,
                                              name="Test Rule", # RuleName
                                              rulegroup_id=RULE_GROUP_ID,
                                              ruletype_id=ruletype_id
                                              )

            if response["status_code"] == 201:
                    print("Successfully created Custom IOA Rule!")
                    self.LOGGER.get_overall_logger().info(f"Successfully created Custom IOA Rule!...{response}")
            else:
                    errors = response["body"].get("errors", [])
                    #errors = response
                    print(f"Failed to create rule: {errors}")
        except Exception as e:
            self.LOGGER.get_overall_logger().warning(f"Failed at create_custom_rule...{e}")
            raise Exception(f"Failed at create_custom_rule...{e}")

    def simple_regex_list(self, list_of_apps, action:str):
        """
        Takes a list of app and checks whether is Mac or Windows and creates a simple regex of the given word

        Eg. Given ['slack.exe', 'Slack.exe']
            it will create .*slack\.exe.* and .*Slack\.exe.*


        :param action:
        :param list_of_apps:
        :return:
        """
        try:
            for app in list_of_apps:
                proc_str = app.rsplit(".",1)
                print(proc_str)
                #If the split creates more than 1 item in the list it means it has extension
                if len(proc_str) > 1:
                    name = proc_str[0]
                    print(name)
                    extension = proc_str[-1:][0]
                    print(extension)
                    if extension is not None:
                        regex = ".*" + name + "\." + extension + ".*"
                        print(regex)
                        if ".app" in app:
                            self.create_custom_rule("Mac", regex, action)
                        elif ".exe" in app:
                            self.create_custom_rule("Win", regex, action)
                        else:
                            print("Unsupported OS Type: " + app)
                            self.LOGGER.get_overall_logger().warning(f"Failed at init simple_regex_list...{app}")

                # For now this sections is commented out since we don't allow single keywords to be processed
                # For now we only allow name.extension to be processed
                # else:
                #     # The section below allows keyword without extensions
                #     # If the split creates 1 item in the list it means it has NO extension
                #     name = proc_str[0]
                #     regex =  ".*" + name + ".*"
                #     self.create_custom_rule("Win", regex, action)
                #     self.create_custom_rule("Mac", regex, action)
        except Exception as e:
            self.LOGGER.get_overall_logger().warning(f"Failed at init simple_regex_list...{e}")
            raise Exception(f"Failed at simple_regex_list...{e}")

    def complex_regex_list(self, list_of_apps, action:str):
        """
           Takes a list of app and checks whether is Mac or Windows and creates a bit more complicate regex of the given word

           Eg. Given ['slack.exe', 'Slack.exe']
               it will create .*slack(\s[a-zA-Z]+(\s\([a-zA-Z]+\))?)?\.\.exe.* and .*Slack(\s[a-zA-Z]+(\s\([a-zA-Z]+\))?)?\.\.exe.*
               which captures Slack testing app2.exe or any other naming convention.

           :param action:
           :param list_of_apps:
           :return:
        """
        try:
            for app in list_of_apps:
                proc_str = app.rsplit(".",1)
                print(proc_str)
                if len(proc_str) > 1:
                    name = proc_str[0]
                    print(name)
                    extension = proc_str[-1:][0]
                    print(extension)
                    regex = ".*" + name + "(\s[a-zA-Z]+(\s\([a-zA-Z]+\))?)?\." + extension + ".*"
                    print(regex)
                    if ".app" in app:
                        self.create_custom_rule("Mac", regex, action)
                    elif ".exe" in app:
                        self.create_custom_rule("Win", regex, action)
                else:
                    name = proc_str[0]
                    regex = ".*" + name + "(\s[a-zA-Z]+(\s\([a-zA-Z]+\))?)?"+".*"
                    self.create_custom_rule("Win", regex, action)
                    self.create_custom_rule("Mac", regex, action)
        except Exception as e:
            self.LOGGER.get_overall_logger().warning(f"Failed at init complex_regex_list...{e}")

