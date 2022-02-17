import json
import logging


class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the LogRecord.

    @param dict fmt_dict: Key: logging format attribute pairs.
        Defaults to {"message": "message"}.
    @param str time_format: time.strftime() format string.
        Default: "%Y-%m-%dT%H:%M:%S"
    @param str msec_format: Microsecond formatting. Appended at the end.
        Default: "%s.%03dZ"
    """

    def __init__(self, fmt_dict: dict = None,
                 time_format: str = "%Y-%m-%dT%H:%M:%S",
                 msec_format: str = "%s.%03dZ"):
        self.fmt_dict = fmt_dict if fmt_dict is not None else {
            "message": "message", "extra": "extra"}
        self.default_time_format = time_format
        self.default_msec_format = msec_format
        self.datefmt = None

    def usesTime(self) -> bool:
        """
        Look for the attribute in the format dict instead of the fmt string.

        This overwrites the original function.

        :return: True for when time is used. False otherwise.
        :rtype: bool
        """
        return "asctime" in self.fmt_dict.values()

    def formatMessage(self, record) -> dict:
        """
        Return a dict of the relevant LogRecord attribute instead of a string.

        _extended_summary_

        :param record: ??
        :type record: ??
        :return: The dict of the LogRecord
        :rtype: dict
        :raises KeyError: if an unknown attribute is provided in the fmt_dict.
        """
        return {fmt_key: record.__dict__[fmt_val] for fmt_key, fmt_val in
                self.fmt_dict.items()}

    def format(self, record) -> str:
        """
        Format record and dump as JSON.

        Mostly the same as the parent's class method, the difference being
        that a dict is manipulated and dumped as JSON instead of a string.

        :param record: The record to be formated
        :type record: ??
        :return: JSON formatted
        :rtype: str
        """
        record.message = record.getMessage()

        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        message_dict = self.formatMessage(record)

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            message_dict["exc_info"] = record.exc_text

        if record.stack_info:
            message_dict["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(message_dict, default=str)


class JakobsJsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the LogRecord.

    @param dict fmt_dict: Key: logging format attribute pairs.
        Defaults to {"message": "message"}.
    @param str time_format: time.strftime() format string.
        Default: "%Y-%m-%dT%H:%M:%S"
    @param str msec_format: Microsecond formatting. Appended at the end.
        Default: "%s.%03dZ"
    """

    def __init__(self, fmt_dict: dict = None,
                 time_format: str = "%Y-%m-%dT%H:%M:%S",
                 msec_format: str = "%s.%03dZ"):
        super().__init__()
        self.fmt_dict = fmt_dict if fmt_dict is not None else {
            "message": "message", "extra": "extra"}
        self.default_time_format = time_format
        self.default_msec_format = msec_format
        self.datefmt = None

    def usesTime(self) -> bool:
        """
        Overwritten to look for attribute in the format dict values.

        This is instead of the default fmt string.
        """
        return 'asctime' in self.fmt_dict.values()

    def formatMessage(self, record) -> dict:
        """
        Overwrite to return dict of relevant attributes instead of string.

        Overwritten to return a dictionary of the relevant LogRecord attributes
        instead of a string. KeyError is raised if an unknown
        attribute is provided in the fmt_dict.

        :param record: ??
        :type record: ??
        :return: The formated dict
        :rtype: dict
        """
        return {fmt_key: record.__dict__[fmt_val] for fmt_key, fmt_val in
                self.fmt_dict.items()}

    def format(self, record) -> str:
        """
        Overriden function, that manipulates dict and dump as JSON and not str.

        :param record: The record to be formated
        :type record: ??
        :return: json
        :rtype: str
        """
        record.message = record.getMessage()

        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        message_dict = self.formatMessage(record)

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            message_dict["exc_info"] = record.exc_text

        if record.stack_info:
            message_dict["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(message_dict, default=str)


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())

logger = logging.getLogger(__name__)
logger.addHandler(handler)
