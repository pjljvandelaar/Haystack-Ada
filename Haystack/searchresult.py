"""
This module contains the methods used to search for pattern matches.
The only function used from outside this module is execute_search, which searches for one
Ada parse tree in another.
"""
from typing import List, Dict, Union
import libadalang as lal  # type: ignore
from Haystack.location import Location
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
    wildcards: Dict[str, Union[lal.AdaNode, None, List[lal.AdaNode]]]

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
            return True  # the leaf is a singular wildcard and it passes the comparison
        if (
            root2.text
            and _is_plural_wildcard(root2.text)
            and self._wild_comparison(root1, root2)
        ):
            return True  # the leaf is a plural wildcard and it passes the comparison
        if (
            not root1.children
            and not root2.children
            and not _text_comparison(root1.text, root2.text, self.case_insensitive)
        ):
            return (
                False  # the leaf is a regular text node it doesn't pass the comparison
            )

        # beforehand, we count the number of plural wildcards in the current subtree
        filter_children1 = [i for i in root1.children if i is not None]
        filter_children2 = [i for i in root2.children if i is not None]
        plural_wildcards_no = sum(
            _is_plural_wildcard(child.text) for child in filter_children2
        )

        if len(filter_children1) == len(filter_children2):
            # "standard" case, where the number of children is equal and we can iterate in parallel
            for i in range(len(root1.children)):
                if not self._are_identical(root1.children[i], root2.children[i]):
                    return False
            self.last_location = root1.sloc_range
            return True
        elif plural_wildcards_no:
            # if the no of children is different, we can only match if there are plural wildcards
            return self.wildcard_list_matching(root1, root2, plural_wildcards_no)
        return False

    def wildcard_list_matching(
        self, root1: lal.AdaNode, root2: lal.AdaNode, plural_wildcards_no: int
    ):
        regular_children = len(root2.children) - plural_wildcards_no
        to_compare = [i for i in root1.children if i is not None]

        # if there is the same number of children disregarding the wildcards,
        # we can still compare by iterating in parallel, provided we strip the wildcards first
        if len(to_compare) == regular_children:
            new_children = _strip_from_wildcards(root2)
            # this loop is analogous to the standard case
            for i in range(len(root1.children)):
                if not self._are_identical(root1.children[i], new_children[i]):
                    return False
            # loop below must be added so that we set our wildcards to None
            # (or check in the dictionary, if they already exist)
            for child in list(set(root2.children) - set(new_children)):
                if not self._wild_comparison(None, child):
                    return False
            self.last_location = root1.sloc_range
            return True
        # a more complex case arises if the numbers don't match
        # we preliminarily check the lower bound of the number of children in root1
        elif len(to_compare) > regular_children:
            # we keep track of which children of root2 are wildcards
            wildcard_indexes = [
                i
                for i in range(len(root2.children))
                if _is_plural_wildcard(root2.children[i].text)
            ]
            # if we are sure that elements of root2 have to belong to the current wildcard
            # in order for it to match, we store their values in the below list
            multi_wildcard_value: List[List[lal.AdaNode]] = []
            i = 0  # root1 iterator
            j = 0  # root2 iterator
            # we now try to check if it's possible to match both lists
            while i < len(root1.children) and j < len(root2.children):
                if (
                    j in wildcard_indexes
                ):  # if the current element of root2 is a wildcard
                    # here, our best assumption is that the wildcard matches to 0 nodes
                    # but, if either there already are elements on the multi_wildcard_value list
                    # or we've reached the end of root1, then the current root1 element
                    # has to belong to the current wildcard
                    if multi_wildcard_value or i == len(root1.children) - 1:
                        multi_wildcard_value.append(root1.children[i])
                        i += 1
                    j += 1
                else:  # if the current element of root2 is not a wildcard
                    # if current elements of root1 and root2 are not the same it means that
                    # current root1 element has to still belong to the last wildcard that appeared on root1
                    # so we add it to the list
                    if root2.children and not self._are_identical(
                        root1.children[i], root2.children[j]
                    ):
                        multi_wildcard_value.append(root1.children[i])
                    # but if they are identical, then we have to check if the current multi_wildcard_value list
                    # indeed matches the last wildcard that appeared on root2
                    else:
                        if wildcard_indexes and [
                            index for index in wildcard_indexes if index < j
                        ]:
                            last_wildcard = max(
                                [index for index in wildcard_indexes if index < j]
                            )
                            # if this the last wildcard on on root2, then we add a modifier
                            # which informs _wild_comparison_multi function that it should not add a new key yet
                            ignore_nonexistant = (
                                True if last_wildcard == wildcard_indexes[-1] else False
                            )
                            if not self._wild_comparison_multi(
                                multi_wildcard_value,
                                root2.children[last_wildcard],
                                ignore_nonexistant=ignore_nonexistant,
                            ):
                                # if we didn't reach the end of root1 yet, we move on and gather remaining elements
                                if i < len(root1.children) - 1:
                                    i += 1
                                    continue
                                return False
                        multi_wildcard_value = []
                        j += 1
                    i += 1
            if wildcard_indexes:
                # after going through all of root1 we can add/check the last wildcard
                last_wildcard = max([j for j in wildcard_indexes if j <= i])
                if not self._wild_comparison_multi(
                    multi_wildcard_value, root2.children[last_wildcard]
                ):
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

    def _wild_comparison(
        self, root1: Union[lal.AdaNode, None], root2: lal.AdaNode
    ) -> bool:
        for key in self.wildcards.keys():
            if _ignore_semicolon_comparison(key, root2.text):
                if self._are_identical(self.wildcards[key], root1):
                    return True
                return False
        self.wildcards[root2.text] = root1
        return True

    def _wild_comparison_multi(
        self, multi: List, root2: lal.AdaNode, ignore_nonexistant=False
    ) -> bool:
        for key, value in self.wildcards.items():
            if _ignore_semicolon_comparison(key, root2.text):
                if isinstance(value, List) and len(value) == len(multi):
                    if all(
                        self._are_identical(value[i], multi[i])
                        for i in range(len(multi))
                    ):
                        return True
                return False
        if not ignore_nonexistant:
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
    return text1.rstrip(";") == text2.rstrip(";")


def _is_singular_wildcard(text: str) -> bool:
    """
    Checks whether a string is a singular wildcard
    """
    return bool(re.search("^\$S_[A-Za-z_]+[0-9]*(;)?$", text))


def _is_plural_wildcard(text: str) -> bool:
    """
    Checks whether a string is a plural wildcard
    """
    return bool(re.search("^\$M_[A-Za-z_]+[0-9]*(;)?$", text))


def _strip_from_wildcards(root):
    new_children = [
        i for i in root.children if not i.text or not _is_plural_wildcard(i.text)
    ]
    return new_children
