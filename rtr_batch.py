from falconpy import RealTimeResponse
import json

class RTRBulk:
    def __init__(self):
        # CrowdStrike API credentials
        self.client_id = ""
        self.client_secret = ""
        self.base_url = "https://api.crowdstrike.com"  # Adjust if needed

        # Execute a command on all hosts in the batch; for example, run 'hostname'
        # command = "runscript -Raw hostname"
        # The command you want to execute (e.g., 'ls', 'get', 'put', 'runscript', etc.)
        self.COMMAND_STRING = "ls"  # The actual command line to run
        self.COMMAND_BASE = "pwd"  # The base command used by the API

        # Batch initialize RTR sessions for those hosts with an optional timeout
        self.rtr_obj = self.init_rtr_obj()
        batch_init_response = self.rtr_obj.batch_init_sessions(host_ids=self.get_hosts_ids(), timeout_duration="10m")
        self.batch_id = batch_init_response.get("body", {}).get("batch_id")
        print(f"Batch ID: {self.batch_id}")

    def init_rtr_obj(self):
        """"
            Instantiate the RTR client
            Returns: RTR client object
        """
        try:
            rtr_obj = RealTimeResponse(client_id=self.client_id, client_secret=self.client_secret,
                                        base_url=self.base_url)
            print("Stage - rtr_obj init was successful")
            return rtr_obj
        except Exception as e:
            print(f"Stage - rtr_obj init was successful - {e}")


    @staticmethod
    def get_hosts_ids():
        """
        Configure the list of host ids to act on
        :return: list of host ids
        """
        # List of host IDs where RTR commands will run
        host_ids = [
            "",
        ]
        return host_ids

    def send_command(self):
        """
        "status_code": 201 --> success
        :return:
        """
        if self.batch_id:
            response = self.rtr_obj.batch_active_responder_command(
                batch_id=self.batch_id,
                # command=command,
                base_command = self.COMMAND_BASE,
                command_string = self.COMMAND_STRING,
                host_timeout_duration = "30s",  # Wait up to 30 seconds for immediate response
                # You can also use 'batch_host_ids' instead of 'device_id' for Host Group IDs
                persist_all = True  # Queue for offline hosts
            )
            print(json.dumps(response, indent=4, sort_keys=True))
        else:
            print("Failed to create batch session.")


RTRBulk().send_command()