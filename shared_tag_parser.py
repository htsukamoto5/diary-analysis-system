class TagFormatParser:
    """
    Handles parsing and validating tag format specifications
    """

    def __init__(self, format_string: str, case_sensitive: bool, normalize_to: str):
        """
        Constructor for TagFormatParser
        
        :param format_string: e.g., "{{{TAGNAME_}}}"
        :type format_string: str
        :param case_sensitive: Whether tags are case-sensitive
        :type case_sensitive: bool
        :param normalize_to: 'upper', 'lower', 'first', or 'keep' (only used if case sensitive)
        :type normalize_to: str
        """
        self.format_string = format_string
        self.case_sensitive = case_sensitive
        self.normalize_to = normalize_to
        self.prefix = ""
        self.suffix = ""
        self.parse()

    def parse(self):
        """
        Extract prefix and suffix from format string
        """
        # Find TAGNAME (case-insensitive)
        tag_position = self.format_string.upper().find('TAGNAME')

        if tag_position == -1: # not found
            raise ValueError("Format string must contain 'TAGNAME' placeholder")
        
        self.prefix = self.format_string[:tag_position]
        self.suffix = self.format_string[tag_position + 7:] # 7 = len('TAGNAME')

    def normalize_tag(self, tag_name: str) -> str:
        """
        Normalize tag name based on case sensitivity settings
        
        :param tag_name: Name of the tag
        :type tag_name: str
        :return: the tag name formatted correctly
        :rtype: str
        """
        if self.case_sensitive:
            return tag_name
        
        if self.normalize_to == 'upper':
            return tag_name.upper()
        elif self.normalize_to == 'lower':
            return tag_name.lower()
        elif self.normalize_to == 'first':
            return tag_name.capitalize()
        else:
            return tag_name
        
    def create_full_tag(self, tag_name: str) -> str:
        """
        Create full tag with prefix and suffix

        :param tag_name: name of the tag
        :type tag_name: str
        :return: full tag (prefix, normalized tag name, and suffix concatenated)
        :rtype: str
        """
        normalized_tag = self.normalize_tag(tag_name)
        return f"{self.prefix}{normalized_tag}{self.suffix}"
    
    def validate_tag(self, s: str) -> bool:
        """
        Check if a string matches the tag format
        
        :param s: a string that may be a tag
        :type s: str
        :return: true if s matches the tag format
        :rtype: bool
        """
        return s.startswith(self.prefix) and s.endswith(self.suffix)

    def extract_tag_name(self, s: str):
        """
        Extract tag name from full tag string (if s is in tag format)

        :param s: a string (presumably a tag)
        :type s: str
        """
        if not self.validate_tag(s):
            return None
        
        tag_name = s[len(self.prefix):-len(self.suffix)] if self.suffix else s[len(self.prefix):]
        return self.normalize_tag(tag_name)

    def to_dict(self) -> dict:
        """
        Convert to dictionary for JSON serialization
        
        :return: a dictionary in JSON format
        :rtype: dict
        """
        return {
            'format_string': self.format_string,
            'prefix': self.prefix,
            'suffix': self.suffix,
            'case_sensitive': self.case_sensitive,
            'normalize_to': self.normalize_to
        }