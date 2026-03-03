import time
import json
from traceback import print_tb
from Application_IOA.Logging_file import Logging_Class as logger, Logging_Class
from CONFIG import *
from falconpy import Discover
from slack_sdk.errors import SlackApiError

class Discovery:

    def __init__(self, LOGGER):
        try:
            self.LOGGER = LOGGER

            # Do not hardcode API credentials!
            self.falcon_discover = Discover(
                client_id= client_id,
                client_secret= client_secret,
                              )
            self.LOGGER.get_overall_logger().info("Discovery Obj init - successfully initialized!")
        except Exception as e:
            self.LOGGER.get_overall_logger().warning(f"Failed at init Discovery...{e}")
            raise Exception(f"Failed at init Discovery...{e}")

    # Choose ONE filter below:

    # 1. ALL Windows apps
    #apps = fetch_apps_with_filter("name:'.*'")

    # 2. Chrome browsers only
    #apps = fetch_apps_with_filter("name:'Chrome'")
    # apps = fetch_apps_with_filter("Slack")


    # 3. Microsoft apps on Windows
    # apps = fetch_apps_with_filter("platform_name:'Windows'+vendor:'Microsoft Corporation'")

    # 4. Recent apps (last 30 days, if first_seen field available)
    # apps = fetch_apps_with_filter("first_seen:>='2026-01-01'")

    # 5. Apps with specific version
    # apps = fetch_apps_with_filter("name:'Google Chrome'+version:'124.*'")

    def fetch_apps_with_filter(self, app_name):
        """
        It accepts an app name and it looks for all instances related to that app name by using regex expression.
        Eg. Given -> Slack, the code will look for *Slack*
        The results will be saved into a file as a list of IDs.
        - name
        - vendor
        - version
        - software_type
        - name_vendor
        - name_vendor_version
        - installation_paths
        - host
            - platform_name
            - os_version
            - tags
            - groups
            - system_manufacturer
            - hostname
        :param apps:
        :param filter_query:
        :return: None
        """
        try:
            apps = "name:*'*"+app_name+"*'"
            print("Fetching apps similar to: "+apps)
            all_app_ids = []
            current_offset = 0
            limit = 100
            page = 0
            flag_first_app = True

            while True:
                print("Page: "+str(page))
                #Fetcing all apps
                response = self.falcon_discover.query_applications(
                    offset=current_offset,
                    limit=limit,
                    filter=apps,
                    sort="name.asc"  # Sorting ensures consistent pagination
                )

                # Check for success
                if response["status_code"] != 200:
                    break

                # Extract only resource IDs
                resources = response["body"].get("resources", [])
                if not resources:
                    break
                print("Got "+str(len(resources))+" resources")

                # Add newly fetched IDs
                all_app_ids.extend(resources)

                # Update offset for the next page
                # Check the total number of entries and add them to the offset value
                current_offset += len(resources)

                # Logic to stop if we've hit the end
                total = response["body"]["meta"]["pagination"]["total"]
                if current_offset >= total:
                    break

                page += 1
            #print(all_app_ids)

            # Save the app IDs as a list in a file
            print("Got {} apps".format(len(all_app_ids)))
            with open("filtered_apps_ids.json", "w") as f:
                 json.dump(all_app_ids, f, indent=2)

            #init_and_finalize_apps_file("start")
            self.get_details_of_apps(flag_first_app)
        except Exception as e:
            self.LOGGER.get_overall_logger().warning(f"Failed at init fetch_apps_with_filter...{e}")

    def falcon_get_applications(self, ids, flag_first_app):
        """
        This method is called by get_details_of_apps() and is responsible for reading the app IDs retrieved before and
        query falcon about the full details of those applications found.
        Eg. the method provides to the falcon API an app ID and the API returns all details about that ID
        Give -> 12345 (app_ID) we get Full App Details -> {'id': '27e71d44ba*****a69c432db772d737c', 'cid': '27e71*****3a2f4', 'name': 'Slack', 'vendor': 'Slack', 'version': '4.47.72 (447000072)', 'software_type': 'application', 'name_vendor': 'Slack-Slack', 'name_vendor_version': 'Slack-Slack-4.47.72 (447000072)', 'versioning_scheme': 'unknown', 'category': 'Collaboration', 'architectures': ['aarch64'], 'installation_paths': ['/System/Volumes/Data/Applications/Slack.app'], 'installation_timestamp': '2025-12-21T04:04:49Z', 'first_seen_timestamp': '2026-01-06T22:09:14Z', 'last_updated_timestamp': '2026-01-06T22:09:14Z', 'last_used_user_sid': 'S-1-5-21-1897749604-2449458078-3130162024-2004', 'last_used_user_name': 'alexis.royne', 'last_used_file_name': 'Slack', 'last_used_file_hash': '3bbf95aa300679ef7e7ed0be3af058afb9b0a16b34de2b30cda722838dd15413', 'last_used_timestamp': '2026-02-11T07:00:00Z', 'is_suspicious': False, 'is_normalized': True, 'host': {'id': '27e71d44baed46b59b6f21d42e83a2f4_ASBFS8ioZ_oHIQIdJH_d05xoJtJr7UA5Q9RLjWBFUoosUh3k7yJV5XnW', 'aid': '0bdfd0bde74a41cb9c8f77304083a373', 'country': 'Spain', 'platform_name': 'Mac', 'os_version': 'Sequoia (15)', 'kernel_version': '24.6.0', 'product_type_desc': 'Workstation', 'tags': ['FalconGroupingTags/Mac-Regular-Employee'], 'groups': ['423c1b4717264cd196f333e87327ee69'], 'system_manufacturer': 'Apple Inc.', 'agent_version': '7.33.20503.0', 'external_ip': '47.63.239.122', 'hostname': 'MAC-AROYNE', 'current_mac_address': '16-87-6A-BB-64-8B', 'current_network_prefix': '169.254', 'internet_exposure': 'No'}}
        This is written in another file filtered_apps.json
        :param flag_first_app:
        :param ids:
        :return:
        """
        try:
            if len(ids) != 0:
                print("Fetching app details for a list of : "+ str(len(ids)))
                details = self.falcon_discover.get_applications(ids=ids)
                #print(details)
                if details["status_code"] == 200:
                    apps = details["body"]["resources"]
                    for app in apps:
                        # print("Adding " + json.dumps(app))
                        # Open the file in append mode ('a')
                        # turn dict into JSON
                        # json_app = json.dumps(app)
                        # if flag_first_app:
                        #     final_str = json.dumps(app)
                        #     flag_first_app = False
                        # else:
                        #     final_str = "," + json.dumps(app)
                        with open("filtered_apps.json", "a", encoding="utf-8") as file:
                            file.write(json.dumps(app)+"\n")
            else:
                print("No apps found")
        except Exception as e:
            self.LOGGER.get_overall_logger().warning(f"Failed at init falcon_get_applications...{e}")

    def get_details_of_apps(self, flag_first_app:bool):
        """
        This method will be called by fetch_apps_with_filter() to read and clean the app IDs in order to pass that info to falcon_get_applications().
        Eg. the methods reads the file ["1234","1234"] and creates a list of raw IDs found in filtered_apps_ids.json
        Looking into the method we are creating list of 50 apps per call in order to reduce memory usage.
        :return: None
        """
        try:
            with open('filtered_apps_ids.json', 'r', encoding='utf-8') as fp:
                #data = json.load(fp)
                #print(data)

                app_entry_ids = []
                all_app_names = []
                # Read the file line by line
                print("Reading app IDs from file...")
                for line in fp.readlines():
                    # print(line.strip())
                    # Add id to list until 50

                    processed_line = line.strip().strip("[]'\",")
                    #print(processed_line)
                    if processed_line != "":
                        app_entry_ids.append(processed_line)
                        # If 50 call get_app
                        if len(app_entry_ids) >= 50:
                            # Results save to list
                            print("Processing " + str(len(app_entry_ids)) + " app IDs...")
                            self.falcon_get_applications(app_entry_ids, flag_first_app)
                            flag_first_app = False
                            # Empty the list
                            app_entry_ids = []
                    # go to next entry
                # if the list of entry ids is not empty it means results were less than 50
                # then execute the rest of ids
                if len(app_entry_ids) > 0:
                    print("Processing residual list of " + str(len(app_entry_ids)))
                    self.falcon_get_applications(app_entry_ids, flag_first_app)
                #init_and_finalize_apps_file("end")
        except Exception as e:
            self.LOGGER.get_overall_logger().warning(f"Failed at init get_details_of_apps...{e}")
