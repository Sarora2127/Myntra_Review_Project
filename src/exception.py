# src > exception.py
import os # used to extract just the filename from a full file path.
def error_message_detail(error, error_detail): # error_detail: The traceback object that contains full info about where the error occurred.
    try:
        _,_,exc_tb = error_detail.exc_info()
    # exc_info() returns a tuple of 3 values: (exception_type, exception_value, traceback_object).
    # We only care about the traceback (exc_tb), which tells us:
    # 1. In which file the error occurred.
    # 2. On which line.
    # 3. In which function.
        if exc_tb is not None:
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            # exc_tb.tb_frame.f_code.co_filename gives the full path of the file where the error happened.
            # os.path.split(...)[1] extracts just the file name from that path.
            error_message = "Error occurred Python Script name [{0}] line number [{1}] error message [{2}]".format(
            file_name, exc_tb.tb_lineno, str(error)
        )
        else:
            error_message = f"Error occurred: {str(error)} (No traceback available)"
        return error_message
    except Exception as e:
        return f"Failed to generate error message: {str(e)}"

class CustomException(Exception): # inherit from CustomException
    def __init__(self, error_message, error_detail):
        """
        :param error_message : error message in string format
        """
        super().__init__(error_message)
        self.error_message = error_message_detail(
            error_message, error_detail = error_detail 
        )
    def __str__(self):
        return self.error_message
# Overrides Python’s default __str__() method for this class.
# So, when you print() the exception or log it, it shows the formatted error message.