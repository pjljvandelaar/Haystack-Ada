import libadalang as lal  # type: ignore
from typing import Optional, List, Dict
from location import Location


class SearchResult:
    """Class used for searching a text in a file and storing its location.

    :param filename: Name of the file to be searched
    :type filename: str
    :param fragment: Piece of text to be searched for
    :type fragment: str
    :param rule: Grammar rule used to parse the fragment
    :type rule: class:'libadalang.GrammarRule', optional
    """

    locations: List[Location]
    last_location: str
    case_insensitive: Optional[bool]
    wildcards: Dict[str, lal.AdaNode]

    def __init__(self, case_insensitive):
        """Constructor method"""
        self.locations = []
        self.last_location = ""
        self.case_insensitive = case_insensitive
        self.wildcards = {}

    def are_identical(self, root1: lal.AdaNode, root2: lal.AdaNode) -> bool:
        """
        Checks whether leaves of two tree roots are identical

        :param root1: Root of the first tree to be compared
        :param root2: Root of the second  tree to be compared
        :return: True if the children are identical
        :rtype: bool
        """
        if root1 is None and root2 is None:
            return True
        if root1 is None or root2 is None:
            return False
        if (
            not root2.children
            and root2.text
            and root2.text[:2] == "$S"
            and self.wild_comparison(root1, root2)
        ):
            return True
        if (
            root2.text
            and len(root2.text.split()) == 1
            and root2.text[:2] == "$M"
            and self.wild_comparison(root1, root2)
        ):
            return True
        if len(root1.children) != len(root2.children):
            return False
        if (
            not root1.children
            and not root2.children
            and not _text_comparison(root1.text, root2.text, self.case_insensitive)
        ):
            return False
        for i in range(len(root1.children)):
            if not self.are_identical(root1.children[i], root2.children[i]):
                return False
        self.last_location = root1.sloc_range
        return True

    def is_subtree(self, tree: lal.AdaNode, subtree: lal.AdaNode) -> bool:
        """
        Checks whether one tree is a subtree of another tree

        :param tree: The tree to be searched
        :param subtree: The tree to be searched for
        :return: True if subtree exists in the tree
        :rtype: bool
        """
        if subtree is None:
            return True
        if tree is None or not subtree.children:
            return False
        if self.are_identical(tree, subtree):
            self.locations.append(_parse_sloc(self.last_location, self.wildcards))
            return True
        for child in tree.children:
            if self.is_subtree(child, subtree):
                print("match found:",self.last_location)
                self.locations.append(_parse_sloc(self.last_location, self.wildcards))
        self.wildcards = {}
        return False

    def wild_comparison(self, root1, root2):
        if root2.text in self.wildcards:
            if self.are_identical(self.wildcards[root2.text], root1):
                return True
            return False
        self.wildcards[root2.text] = root1
        return True


def _parse_sloc(sloc: str, wildcards: Dict[str, str]) -> Location:
    """Transforms sloc into Location type element

    :return: Location representing the input sloc
    """
    range_ = str(sloc).split("-")
    [line1, pos1], [line2, pos2] = range_[0].split(":"), range_[1].split(":")
    return Location(int(line1), int(line2), int(pos1), int(pos2), wildcards)


def _text_comparison(text1, text2, case_insensitive):
    """
    Compares two strings.
    Case sensitive if case_insensitive is false, case insensitive otherwise.
    """
    return text1 == text2 if not case_insensitive else text1.lower() == text2.lower()
