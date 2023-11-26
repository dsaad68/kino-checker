import re

class CallParser:
    """Class for parsing the input string and returning a dictionary of key-value pairs."""

    # Regular expression pattern to match the key-value pairs
    PATTERN = re.compile(r'\[(.*?)\](\w+)')

    @staticmethod
    def parse(input_string) -> dict:
        """Parses the input string and returns a dictionary of key-value pairs, based on the pattern."""

        # Initialize an empty dictionary to store the key-value pairs
        result_dict = {}

        for match in CallParser.PATTERN.finditer(input_string):
            value, key = match.groups()

            # Strip whitespace and handle type conversion
            key = key.strip()
            # Check: check if there is another way to do this without uppercasing
            value = value.strip().upper()  # Lowercase for boolean and zero check

            # Convert 'true' and 'false' to booleans, '0' to skip, and try to convert other values to numbers
            if value == 'TRUE':
                value = True
            elif value == 'FALSE':
                value = False
            elif value == '0':
                continue

            # Add the key-value pair to the dictionary
            result_dict[key] = value

        return result_dict
