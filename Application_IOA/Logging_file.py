import logging


class Logging_Class(object):
        """
            Simple class to call in methods and
            capture INFO logs into multiple files.
        """
        def __init__(self):
                try:
                        self.formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(message)s')
                        self.user_logger = self.create_message_log_object()
                        self.overall_logger = self.create_overall()
                except Exception as e:
                        raise Exception(f"Failed to initiate Logging in __init__ Logging_Class() {e}")


        def extendable_logger(self, log_name, file_name, level=logging.INFO):
                try:
                        handler = logging.FileHandler(file_name)
                        handler.setFormatter(self.formatter)
                        specified_logger = logging.getLogger(log_name)
                        specified_logger.setLevel(level)
                        specified_logger.addHandler(handler)
                        return specified_logger
                except Exception as e:
                        raise Exception(f"Failed to set settings and File Handler for logger in extendable_logger in Logging_Class() {e}")

        def create_message_log_object(self):
                return self.extendable_logger('message_logs', 'message_logs.logger')

        def create_overall(self):
                return self.extendable_logger('overall_objects', 'overall_logs.logger')

        def get_message_logger(self):
                return self.user_logger

        def get_overall_logger(self):
                return self.overall_logger