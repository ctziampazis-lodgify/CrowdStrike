from slack_sdk.errors import SlackApiError

import Custom_IOA
from slack_sdk import WebClient
from Discovery import *
from App_Details_Processing import *
from Custom_IOA import *
from CONFIG import *
from Logging_file import Logging_Class as logger, Logging_Class

class SlackIntergationClass:

    #slack_channel = '#crowdstrike-alerts',
    slack_channel_id = 'C06FRUL76HH' # WAF ALERTS
    slack_user_name = 'crowdstrike-alerts'
    slack_token = slack_token

    #me,marc,ad
    authorized_users = ["U03E7MSPTFD","U04PU9W1XFW","U055XNSS5HB"]

    slack_client = None
    discovery = None
    custom_IOA = None
    app_details_process = None

    LOGGER = None

    def __init__(self):
        try:
            self.LOGGER = Logging_Class()
            self.slack_init()
            self.LOGGER.get_overall_logger().info("Slack Obj init - successfully initialized!")
        except Exception as e:
             self.LOGGER.get_overall_logger().warning(f"Failed at init SlackIntergationClass...{e}")
             raise Exception(f"Failed at init SlackIntergationClass...{e}")

    def slack_init(self):
        try:
            self.slack_client = WebClient(token=self.slack_token)
            api_response = self.slack_client.api_test()
            self.LOGGER.get_overall_logger().info(
               "--------------Initializing Slack API--------------\n" + "Slack API init OK")
            self.LOGGER.get_overall_logger().info("Testing client api_test - response: " + str(api_response))
        except SlackApiError as e:
            self.LOGGER.get_overall_logger().warning(f"Error in slack_init(): {e}")

    def rest_obj_init(self):
        try:
            self.discovery = Discovery(self.LOGGER)
            self.custom_IOA = Custom_IOA(self.LOGGER)
            self.app_details_process = App_Details_Processing(self.LOGGER)
            self.LOGGER.get_overall_logger().info(
               "--------------Init all related objs--------------\n")
        except SlackApiError as e:
            self.LOGGER.get_overall_logger().warning(f"Error in rest_obj_init(): {e}")
            raise Exception(f"Error in rest_obj_init(): {e}")

    def get_conversation_id(self):
        result = self.slack_client.conversations_info(
            channel=self.slack_channel_id
        )
        print(result)

    def sending_alert(self, slack_message):
        """
        Method to be used for sending messages

        :param slack_message: Text Message
        :return: None
        """
        try:

            # Call the conversations.list method using the WebClient
            result = self.slack_client.chat_postMessage(
                channel=self.slack_channel_id,
                text=slack_message,
                #ssl=self.ssl_context
                # You could also use a blocks[] array to send richer content
            )
            self.LOGGER.get_message_logger().info("Sending message - " + str(result))
            # Print result, which includes information about the message (like TS)
            # print(result)
        except SlackApiError as e:
            self.LOGGER.get_overall_logger().warning(f"Error in sending_alert: {e}")

    # def hash_message(self, message):
    #     hash = hashlib.sha256(message.encode('utf-8'))
    #     print(hash.hexdigest())

    def format_message(self, message):

        self.LOGGER.get_message_logger().info("format_message - message to be formatted!")

        allowed_commands = ["block", "search", "detect"]
        app_list = []

        list_of_msg_part = message.split("\n")

        if list_of_msg_part[0] in allowed_commands:
            print("Command found: " + list_of_msg_part[0])

            list_of_apps = list_of_msg_part[1:]

            # TODO in the future check if minimum it has [a-zA-Z]+.[exe|app]
            for app in list_of_apps:
                if app is not None and app != "":
                    app_list.append(app)

            if list_of_apps is not None and len(list_of_apps) > 0:
                print("Final foratted message: " + str(app_list))
                self.LOGGER.get_message_logger().info(f"format_message - Command Found and sending!\n{message}")

                return list_of_msg_part[0], app_list
            else:
                self.LOGGER.get_message_logger().warning(f"format_message - command not recognized!\n{message}")
                return None, list_of_msg_part[0]
        else:
            self.LOGGER.get_message_logger().warning(f"format_message - command not recognized!\n{message}")
            return None, list_of_msg_part[0]

    def process_message(self, message):
        """
        The Logic accepts the following commands [search,block,detect]

        All commands should be in the following form:
            For Search
                search
                steam
            For Block
                block
                app1.app
                app2.app
                app3.exe
            For Detect
                detect
                app1.app

        :param message:
        :return:
        """
        try:

            #Initiating the necessary objs
            self.rest_obj_init()


            # DONE Process the message to find out if command given is allowed
            # Returns <string>, List<Strings>
            command, formatted_msg = self.format_message(message)

            # Look for allowed commands
            if command is not None:
                # If command exist take all the rest parts of the message

                if command == "search":
                    for mess in formatted_msg:
                        self.discovery.fetch_apps_with_filter(mess)
                        self.app_details_process.get_exact_names()
                        res = self.app_details_process.process_dict()
                        # Eg Win: [xx.exe,aa.exe]
                        # Eg Mac: [app.app,app2.app]
                    self.LOGGER.get_message_logger().info(
                        f"Apps found: \n\tMac:" + str(res[0]) + "\n\tWin" + str(res[1]))
                    self.sending_alert("Apps found: \n\tMac:" + str(res[0]) + "\n\tWin" + str(res[1]))

                elif command == "block":
                    # DONE take the rest part of the command and check if its valid and we got what we expected
                    print("Sending Results to Slack...")
                    self.custom_IOA.simple_regex_list(formatted_msg, command)
                    print("Block Rule Created for: " + str(formatted_msg))
                    self.LOGGER.get_message_logger().info(
                        f"Block Rule Created for: " + str(formatted_msg))
                    self.sending_alert("Block Rule Created for: " + str(formatted_msg))

                elif command == "detect":
                    # DONE take the rest part of the command and check if its valid and we got what we expected
                    print("Sending Results to Slack...")
                    self.custom_IOA.simple_regex_list(formatted_msg,command)
                    print("Detect Rule Created for: " + str(formatted_msg))
                    self.LOGGER.get_message_logger().info(
                        f"Detect Rule Created for: " + str(formatted_msg))
                    self.sending_alert("Detect Rule Created for: " + str(formatted_msg))

                elif command == "monitor":
                    # DONE take the rest part of the command and check if its valid and we got what we expected
                    print("Sending Results to Slack...")
                    self.custom_IOA.simple_regex_list(formatted_msg,command)
                    print("Monitor Rule Created for: " + str(formatted_msg))
                    self.LOGGER.get_message_logger().info(
                        f"Monitor Rule Created for: " + str(formatted_msg))
                    self.sending_alert("Monitor Rule Created for: " + str(formatted_msg))
            else:
                print("Command not found: " + formatted_msg)
                self.LOGGER.get_message_logger().info(
                    f"Command not found: " + formatted_msg)
                self.sending_alert("Command not found: " + str(formatted_msg))


            #Cleaning up the now unused objs.
            del self.discovery
            del self.custom_IOA
            del self.app_details_process
            self.LOGGER.get_overall_logger().info(": Rest of Object Created have been Deleted! ")

        except Exception as e:
            self.LOGGER.get_overall_logger().warning(f"Error in process_message: {e}")
            raise Exception(f"Error in process_message: {e}")

    def retrieve_last_message(self):
        """
        Checks last message retrieved from Slack.
        Conditions:
         - User approved: The user is allowed to call this waf integration

        Handling the errors here, we just throw exceptions and their caught by Thread which ultimate prints them to logs. So no special treatment.
            - Something Went Wrong at Threading - worker - 'user'
        :return: is_user_approved: boolean
        """
        # ID of channel that the message exists in
        try:

            # Call the conversations.history method using the WebClient
            # The client passes the token you included in initialization
            result = self.slack_client.conversations_history(
                channel=self.slack_channel_id,
                inclusive=True,
                # oldest="1610144875.000600",
                limit=1,
            )

            if result is not None:
                messages = result.data.get("messages")

                if messages is not None:
                    actor_bot = messages[0].get("bot_id")
                    actor_user = messages[0].get("client_msg_id")
                    # subtype = messages[0].get("subtype") #channel_join, bot_add, bot_message

                    if actor_user is not None: # if subtype is empty it means it's a user sent message
                        message = str(result.data.get("messages")[0].get("blocks")[0].get("elements")[0].get("elements")[0].get("text"))
                        user = str(result.data.get("messages")[0].get("user"))
                        if user in self.authorized_users:
                            self.LOGGER.get_message_logger().info(f"Authorized User : {user}")
                            self.LOGGER.get_message_logger().info(
                                f"retrieve_last_message - retrieved last message!\n{messages}")
                            self.process_message(message)
                        else:
                            self.LOGGER.get_message_logger().warning(f"Unauthorized User : {user} !!!!!")
                            self.sending_alert("Unauthorized User : "+str(user))
                    elif actor_bot is not None: # Otherwise is a bot
                        if messages[0].get("subtype") != "bot_message":
                            # print(str(result.data))
                            # print(str(result.data.get("messages")))
                            # message = str(result.data.get("messages")[0].get("attachments")[0].get("text"))
                            # print(message)
                            # print(str(result.data.get("messages")[0].get("attachments")[0].get("author_name")))
                            # message = str(result.data.get("messages")[0].get("text"))
                            # print(str(result.data.get("messages")[0].get("attachments")[0].get("author_name")))
                            self.LOGGER.get_message_logger().info("retrieve_last_message - bot_message detected: " + str(actor_bot))

                            #self.hash_message(message)
                    else:
                        self.LOGGER.get_overall_logger().warning(
                            f"retrieve_last_message - unknown issue detected - not user AND not bot: {result}")


        except SlackApiError as e:
            self.LOGGER.get_overall_logger().warning(f"Error in retrieve_last_message: {e}")
            raise Exception(f"Error in retrieve_last_message: {e}")

    def clean_app_file(self):
        try:
            # This opens the file and immediately clears it
            with open("filtered_apps.json", "w") as file:
                pass
        except Exception as e:
            self.LOGGER.get_overall_logger().warning(f"Failed at init clean_app_file...{e}")

#
# obj = SlackIntergationClass()
# # #obj.get_conversation_id()
# obj.retrieve_last_message()

# result = client.conversations_list(types="private_channel")
# for channel in result["channels"]:
#     print(f"Name: {channel['name']} - ID: {channel['id']}")

# Use the channel ID (e.g., 'C12345678') or the channel name (e.g., '#general')
# send_slack_message(slack_channel, "test")




"""

EXAMPLE OF BOT AND USERS MESSAGES

if message = {'user': 'U03E7MSPTFD', ==> is USER

if message = {'subtype': 'channel_join', 'user': 'U06FT1F3343', ==> is BOT

if message = {'subtype': 'bot_add', 'text': 'added an integration to this channel... ==> is BOT

if message = {'subtype': 'bot_message', 'text': 'Falcon Alert: Automated Lead' ==> is BOT

"""

