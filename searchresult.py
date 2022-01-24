"""
This module contains the methods used to search for pattern matches.
The only function used from outside this module is execute_search, which searches for one
Ada parse tree in another.
"""
import libadalang as lal  # type: ignore
from typing import List, Dict
from location import Location
import re


def execute_search(
        pattern: lal.AdaNode, operand: lal.AdaNode, case_insensitive: bool
) -> List[Location]:
    """
    Executes a search operation

    :param pattern: The parse tree to search for
    :param operand: The parse tree to search in
    :param case_insensitive: Whether to enable case insensitive searching
    """
    search = SearchResult(case_insensitive)
    search.is_subtree(operand, pattern)
    return search.locations


class SearchResult:
    """Class used for searching a text in a file and storing its location.

    :param case_insensitive: Flag conveying whether the search should be case insensitive
    :type case_insensitive: bool, optional
    """

    locations: List[Location]
    last_location: str
    case_insensitive: bool
    wildcards: Dict[str, lal.AdaNode]

    def __init__(self, case_insensitive: bool):
        """Constructor method"""
        self.locations = []
        self.last_location = ""
        self.case_insensitive = case_insensitive
        self.wildcards = {}

    def _are_identical(self, root1: lal.AdaNode, root2: lal.AdaNode) -> bool:
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
                and _is_singular_wildcard(root2.text)
                and self._wild_comparison(root1, root2)
        ):
            return True
        if (
                root2.text
                and _is_plural_wildcard(root2.text)
                and self._wild_comparison(root1, root2)
        ):
            return True
        '''
        if len(root1.children) != len(root2.children):
            return False
        '''
        '''
        if not _compare_children(root1, root2):
            return False
        '''
        '''
        new_children = root2.children
        if len(root1.children) < len(root2.children):
            new_children = _strip_from_wildcards(root2)
            for child in list(set(root2.children) - set(new_children)):
                self.wildcards[child.text] = None
        '''
        if (
                not root1.children
                and not root2.children
                and not _text_comparison(root1.text, root2.text, self.case_insensitive)
        ):
            return False
        if len(root1.children) == len(root2.children):  # "standard" case

            for i in range(len(root1.children)):
                if not self._are_identical(root1.children[i], root2.children[i]):
                    return False  # handle corner case!!
            self.last_location = root1.sloc_range
            return True
        else:  # number of children different, check if because of wildcards
            filter_children = [i for i in root2.children if i is not None]
            test = [i for i in root2.children if i is not None]
            plural_wildcards_no = sum(_is_plural_wildcard(child.text) for child in filter_children)
            regular_children = len(root2.children) - plural_wildcards_no
            to_compare = [i for i in root1.children if i is not None]
            if len(to_compare) == regular_children:
                # possibly all $Ms match to zero nodes, let's try to ignore them
                new_children = _strip_from_wildcards(root2)
                for i in range(len(root1.children)):
                    if not self._are_identical(root1.children[i], new_children[i]):
                        return False
                for child in list(set(root2.children) - set(new_children)):
                    # self.wildcards[child.text] = None
                    if not self._wild_comparison(None, child):
                        return False
                self.last_location = root1.sloc_range
                return True
            elif len(root1.children) > regular_children and plural_wildcards_no:
                wildcard_indexes = [i for i in range(len(root2.children)) if _is_plural_wildcard(root2.children[i].text)]
                root2_iterator = 0
                multi_wildcard_value = []
                for i in range(len(root1.children)):
                    root2_iterator = min(root2_iterator, len(root2.children) - 1)
                    if root2_iterator in wildcard_indexes:
                        multi_wildcard_value.append(root1.children[i])
                        root2_iterator += 1
                    else:
                        if root2.children and not self._are_identical(root1.children[i], root2.children[root2_iterator]):
                            multi_wildcard_value.append(root1.children[i])
                        else:
                            if wildcard_indexes:
                                last_wildcard = max([j for j in wildcard_indexes if j < i])
                                # self.wildcards[root2.children[last_wildcard].text] = multi_wildcard_value
                                if not self._wild_comparison_multi(multi_wildcard_value, root2.children[last_wildcard]):
                                    return False
                            multi_wildcard_value = []
                            root2_iterator += 1
                if wildcard_indexes:
                    last_wildcard = max([j for j in wildcard_indexes if j <= i])
                    if isinstance(self.wildcards[root2.children[last_wildcard].text], list):
                        self.wildcards[root2.children[last_wildcard].text] = multi_wildcard_value
                    else:
                        return False
                self.last_location = root1.sloc_range
                return True
            return False

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
        if self._are_identical(tree, subtree):
            self.locations.append(_parse_sloc(self.last_location, self.wildcards))
            return True
        for child in tree.children:
            self.is_subtree(child, subtree)
        self.wildcards = {}
        return False

    def _wild_comparison(self, root1: lal.AdaNode, root2: lal.AdaNode) -> bool:
        for key in self.wildcards.keys():
            if _ignore_semicolon_comparison(key, root2.text):
                if self._are_identical(self.wildcards[key], root1):
                    return True
                return False
        self.wildcards[root2.text] = root1
        return True

    def _wild_comparison_multi(self, multi: list, root2: lal.AdaNode) -> bool:
        for key in self.wildcards.keys():
            if _ignore_semicolon_comparison(key, root2.text):
                if isinstance(self.wildcards[key], list) and len(self.wildcards[key]) == len(multi):
                    if all(self._are_identical(self.wildcards[key][i], multi[i]) for i in range(len(multi))):
                        return True
                # print([i.text for i in multi], root2.text, self.wildcards["$M_After"])
                return False
        self.wildcards[root2.text] = multi
        return True


def _parse_sloc(sloc: str, wildcards: Dict[str, lal.AdaNode]) -> Location:
    """Transforms sloc into Location type element

    :return: Location representing the input sloc
    """
    range_ = str(sloc).split("-")
    [line1, pos1], [line2, pos2] = range_[0].split(":"), range_[1].split(":")
    return Location(int(line1), int(line2), int(pos1), int(pos2), wildcards)


def _text_comparison(text1: str, text2: str, case_insensitive: bool) -> bool:
    """
    Compares two strings.
    Case sensitive if case_insensitive is false, case insensitive otherwise.
    """
    return text1 == text2 if not case_insensitive else text1.lower() == text2.lower()


def _ignore_semicolon_comparison(text1: str, text2: str) -> bool:
    """
    Compares two strings, ignoring the trailing semicolon
    """
    return text1.rstrip(';') == text2.rstrip(';')


def _is_singular_wildcard(text: str) -> bool:
    """
    Checks whether a string is a singular wildcard
    """
    return bool(re.search("^\$S_[A-Z][A-Za-z_]*[0-9]*(;)?$", text))


def _is_plural_wildcard(text: str) -> bool:
    """
    Checks whether a string is a plural wildcard
    """
    return bool(re.search("^\$M_[A-Z][A-Za-z_]*[0-9]*(;)?$", text))


def _compare_children(root1, root2) -> bool:
    all_children = len(root2.children)
    to_compare = len(root1.children)
    wildcards = sum(_is_plural_wildcard(child.text) for child in root2.children)
    # return to_compare >= (all_children - wildcards)
    return wildcards > 0


def _strip_from_wildcards(root):
    new_children = [i for i in root.children if not i.text or not _is_plural_wildcard(i.text)]
    return new_children
