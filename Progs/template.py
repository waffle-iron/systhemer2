"""Template module fro program definitions"""
import logging
import re
from .common import Rule, Section


class ProgDef(object):
    """
    Template for program definitions:
        program definitions should inherit from this class
        and should define settings in the config dictionary
        (see already written definitions for example implementation)

        if a program definition needs special handling,
        you can override the set method
    """

    def __init__(self, Settings):
        self.name = self.__class__.__name__
        self.Settings = Settings
        self.logger = logging.getLogger('Systhemer.Progs.' + self.name)
        self.filebuff = None
        self.config = {}  # add definitions here
        self.init()

    def init(self):
        """this method must be implemented"""
        raise NotImplementedError()

    def get_setting(self, setting, critical=True, msg=None):
        """Get a setting from self.Settings"""
        value = getattr(self.Settings, setting, None)
        if value is None:
            msg = msg if msg is not None else \
                  'Setting \'%s\' not set!' % setting
            if critical:
                self.logger.critical(msg)
                exit(1)
            else:
                self.logger.error(msg + ' Returning \'None\'.', setting)
                return None
        return value

    def get_file_buffer(self):
        """Checks if filebuffer exists. If not, one is created."""
        # if filebuffer doesn't exist
        if self.filebuff is None:
            # get file path from Settings
            file_path = getattr(self.Settings, self.name + '_file_path', None)
            file_path = self.get_setting(self.name + '_file_path',
                                         msg='File path for: \'%s\' not set!'
                                         ' Please set a value for option: %s'
                                         % (self.name,
                                            self.name + '_file_path'),
                                         critical=True)

            with open(file_path) as configfile:
                self.filebuff = configfile.read()

    def set(self, key, value, section):
        """set a value to a certain key"""
        self.get_file_buffer()
        key_found = False

        # cycle through rules
        for rule in self.config:
            if not isinstance(rule, Rule):
                continue

            # check if key exists in the current rule
            if key in rule.keys:

                key_found = True
                self.logger.debug('Key: \'%s\' Found!', key)

                match = re.search(rule.rule, self.filebuff)
                sub_id = rule.keys[key]
                self.filebuff = self.filebuff[:match.start(sub_id)] \
                    + value \
                    + self.filebuff[match.end(sub_id):]
                self.logger.debug('Value set: %s <- %s', key, value)

        if not key_found:
            self.logger.debug('Key: \'%s\' Not found', key)

    def save(self):
        """this method must be implemented"""
        raise NotImplementedError()
