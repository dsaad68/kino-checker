#%%
import re

class CallParser:
    """Class for parsing the input string and returning a dictionary of key-value pairs."""

    # Regular expression patterns to match different parts of the input string
    FILM_ID_PATTERN = re.compile(r'^([A-Z0-9]+),fid')
    UPCOMING_FILM_PATTERN = re.compile(r'^([0-9]+),uf')

    DATE_PATTERN = re.compile(r'(\d{4}-\d{2}-\d{2})')
    TIME_PATTERN = re.compile(r'(\d{2}:\d{2})')

    DATE_PATTERN_ENDING = re.compile(r'(\d{4}-\d{2}-\d{2})$')
    TIME_PATTERN_ENDING = re.compile(r'(\d{2}:\d{2})$')

    FLAG_PATTERN = re.compile(r'([1,2,0]),(\w+)')
    FLAG_VALUES = {'1': True, '0': False, '2': None}

    @staticmethod
    def parse(input_string) -> dict:
        """Parses the input string and returns a dictionary of key-value pairs."""

        result_dict = {}

        if film_id_match := CallParser.FILM_ID_PATTERN.search(input_string):
            result_dict['film_id'] = film_id_match.group(1)
        elif film_id_match := CallParser.UPCOMING_FILM_PATTERN.search(input_string):
            result_dict['uf'] = int(film_id_match.group(1))

        # Extracting flags
        for flag_match in CallParser.FLAG_PATTERN.finditer(input_string):
            value, flag = flag_match.groups()

            # Strip whitespace and handle type conversion
            flag = flag.strip()
            value = value.strip().upper()  # Lowercase for boolean and zero check

            # Convert 'true' and 'false' to booleans, '0' to skip, and try to convert other values to numbers
            if value == '1':
                value = True
            elif value == '0':
                value = False
            elif value == '2':
                continue

            result_dict[f'is_{flag}'] = value

        if date_match := CallParser.DATE_PATTERN.search(input_string):
            result_dict['date'] = date_match.group(1)

        if time_match := CallParser.TIME_PATTERN.search(input_string):
            result_dict['time'] = time_match.group(1)

        return result_dict

    @staticmethod
    def parse_for_input(input_string) -> dict:
        """Parses the input string and returns a dictionary of key-value pairs."""

        result_dict = {}

        if film_id_match := CallParser.UPCOMING_FILM_PATTERN.search(input_string):
            result_dict['uf'] = int(film_id_match.group(1))

        result_dict['flags'] = input_string.partition('|')[2]

        return result_dict
