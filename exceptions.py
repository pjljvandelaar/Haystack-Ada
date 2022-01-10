"""Module defining some useful custom exceptions."""
class OperandParseError(Exception):
    """Exception raised when an operand (string or file) could not be parsed to an AST"""

class PatternParseException(Exception):
    """Exception raised when a search pattern could not be parsed to an AST"""
