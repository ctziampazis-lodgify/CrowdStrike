import json

class App_Details_Processing:

    def __init__(self, LOGGER):
        self.LOGGER = LOGGER

    def get_exact_names(self):
        """
        This method takes the list of app details from filtered_apps.json and it collects only necessary info to create the rules.
        Given a list of app details -> [{app_details},{app_details},{app_details},{app_details}]
        Returns:
            Group results based on the OS
            {
                "OS-name": {[app_name], [app_vendor], [app_install_path]}}
            }
            {
                "OS-name": {[app_name], [app_vendor], [app_install_path]}}
            }

        :return: list of lists
        """
        try:
            app_device_os_ls = []
            final_list = {}

            with open('filtered_apps.json', 'r', encoding='utf-8') as fp:
                for host in fp:
                    host_data = json.loads(host.strip())
                    app_name = host_data['name']
                    app_vendor = host_data.get('vendor', 'Unknown')  # 'Unknown' if 'name' missing
                    app_device_os = host_data.get('host', 'Unknown')["platform_name"]
                    if app_device_os == "Windows":
                        app_install_path = host_data.get('last_used_file_name', 'Unknown')  # 'Unknown' if 'name' missing
                    else:
                        app_install_path = host_data.get('installation_paths', 'Unknown')  # 'Unknown' if 'name' missing

                    if app_device_os not in app_device_os_ls:
                        app_device_os_ls.append(app_device_os)
                        # Device Type Mac: [name,vendor,installation_path]
                        # Device Type Win: [name,vendor,last_used_file_name]
                        final_list.update({app_device_os: [[],[],[]]})
                    if app_device_os in final_list.keys():
                        #print(final_list)
                        if app_name not in final_list[app_device_os][0]:
                            final_list[app_device_os][0].append(app_name)
                        if app_vendor not in final_list[app_device_os][1]:
                            final_list[app_device_os][1].append(app_vendor)
                        # print(app_install_path)
                        # print(final_list[app_device_os][2])
                        # print("Comparing " + str(app_install_path[0]) + " to " + str(final_list[app_device_os][2]))
                        # print(app_install_path[0] not in final_list[app_device_os][2])
                        if app_install_path != "Unknown":
                                if type(app_install_path) is list:
                                    app_exec = app_install_path[0]
                                    #final_list[app_device_os][2].append(app_install_path[0])
                                else:
                                    app_exec = app_install_path
                                    #final_list[app_device_os][2].append(app_install_path)
                                if app_exec not in final_list[app_device_os][2]:
                                    final_list[app_device_os][2].append(app_exec)

                #app_paths = exclude_extensions(app_install_paths)
                #print(final_list)

            with open("dict_apps.json", "w") as f:
                json.dump(final_list,f, indent=2)

            return final_list
        except Exception as e:
            self.LOGGER.get_overall_logger().warning(f"Failed at init get_exact_names...{e}")

    def process_dict(self):
        """
        Process all the data received from the detected apps in App_List_Import().get_exact_names()

        It should split the dictionary received and call create_custom_rule() for each distinct app
        :param dict_response:
        :return:
        """
        try:
            with open("dict_apps.json", "r") as f:
                dict_app_details = json.load(f)

                list_comparison_mac = []
                list_comparison_win = []
                for i in dict_app_details:
                    if i == "Mac":
                        #print("Processing apps for: " + str(i))
                        #list_comparison_mac = []
                        for app in dict_app_details[i][0]:
                            lowercase_mac = app.lower()
                            if ".app" in lowercase_mac: # Making sure the name will have the extension
                                if lowercase_mac not in list_comparison_mac:
                                    list_comparison_mac.append(lowercase_mac)
                                #print("Processing app for: " + str(app))
                        for path in dict_app_details[i][2]:
                            # print(path)
                            # print(path.split("/"))
                            ls_words = path.split("/")
                            for word in ls_words:
                                if ".app" in word:
                                    lowercase_mac_word = word.lower()
                                    if ".app" in lowercase_mac_word:  # Making sure the name will have the extension
                                        if lowercase_mac_word not in list_comparison_mac:
                                            list_comparison_mac.append(lowercase_mac_word)

                    elif i == "Windows":
                        #print("Processing apps for: " + str(i))
                        #list_comparison_win = []
                        for app in dict_app_details[i][2]:
                            #print("Processing app for: " + str(app))
                            lowercase_win = app.lower()
                            if lowercase_win not in list_comparison_win:
                                list_comparison_win.append(lowercase_win)
                        #print(list_comparison_win)

                return list_comparison_mac, list_comparison_win

        except Exception as e:
            self.LOGGER.get_overall_logger().warning(f"App_Details_Processing at init process_dict...{e}")


