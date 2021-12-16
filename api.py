"""
This is the api layer of Haystack. The GUI calls this layer whenever any actions need to be performed.
All the data is passed from the GUI to the functions in this layer.
Any necessary transformations to the data are made here and the data is then passed on to the searchResult and replacer modules.
"""
from typing import List, Tuple
import searchresult as sr
import replacer as rep
from location import Location
import libadalang as lal  # type: ignore


def findall_file(
    search_query: str,
    filepath: str,
    parse_rule: lal.GrammarRule = lal.default_grammar_rule,
    case_insensitive: bool = False,
) -> List[Location]:
    """
    Similar to re.findall; return all matches of search_query in a file at location filepath.

    :param search_query: The pattern to search for
    :param filepath: The filepath for the file to search in
    :param parse_rule: The parse rule used to parse the search query
    :param case_insensitive: Boolean, enables case insensitive searching
    :return: A list of locations where the file matches the search query
    """
    try:
        pattern = _analyze_string(search_query, parse_rule)
        operand = _analyze_file(filepath)
    except ValueError as error:
        raise error
    return _execute_search(pattern.root, operand.root, case_insensitive)


def findall_file_try_rules(
    search_query: str,
    filepath: str,
    parse_rules_to_try: List[lal.GrammarRule],
    case_insensitive: bool,
) -> List[Location]:
    """
    Similar to findall_file, except now we try all parse rules until we find one that parses the search query.

    :param search_query: The pattern to search for
    :param filepath: The filepath for the file to search in
    :param parse_rules_to_try: The list of parse rules that the algorithm should try
    :param case_insensitive: Boolean, enables case insensitive searching
    :return: A list of locations where the file matches the search query
    """
    # If no parse rules are supplied, return a ValueError
    if not parse_rules_to_try:
        raise ValueError

    try:
        # Try to parse the search query
        pattern, tried_rules = _analyze_string_try_rules(
            search_query, parse_rules_to_try
        )
        operand = _analyze_file(filepath)
    except ValueError as error:
        raise error

    # Parsing succeeded, look for any matches
    matches = _execute_search(pattern.root, operand.root, case_insensitive)

    if not matches:
        # If no matches were found, we might have selected the wrong parse rule, define a new list of rules to try and try again
        parse_rules_to_try = [
            rule for rule in parse_rules_to_try if rule not in tried_rules
        ]
        return findall_file_try_rules(
            search_query, filepath, parse_rules_to_try, case_insensitive
        )

    return matches


def findall_string(
    search_query: str,
    to_search: str,
    search_query_parse_rule: lal.GrammarRule = lal.default_grammar_rule,
    to_search_parse_rule: lal.GrammarRule = lal.default_grammar_rule,
    case_insensitive: bool = False,
) -> List[Location]:
    """
    Similar to re.findall; return all matches of seach_query in the string to_search.

    :param search_query: The pattern to search for
    :param to_search: The string on which the search operation is performed
    :param search_query_parse_rule: The parse rule used to parse the search query
    :param to_search_parse_rule: The parse rule used to parse the string on which the search operation is performed
    :param case_insensitive: Boolean, enables case insensitive searching
    :return: A list of locations where the string matches the search query
    """
    try:
        pattern = _analyze_string(search_query, search_query_parse_rule)
        operand = _analyze_string(to_search, to_search_parse_rule)
    except ValueError as error:
        raise error
    return _execute_search(pattern.root, operand.root, case_insensitive)


def sub_file(
    search_query: str,
    filepath: str,
    replacement: str,
    parse_rule: lal.GrammarRule = lal.default_grammar_rule,
    case_insensitive: bool = False,
):
    """
    Similar to re.sub; search for the search query in a file located by filepath, replace all matches with the replacement.

    :param search_query: The pattern to search for
    :param filepath: The filepath for the file to search in
    :param replacement: The string to replace the matched text with
    :param parse_rule: The parse rule used to parse the search query
    :param case_insensitive: Boolean, enables case insensitive searching
    """
    locations = findall_file(search_query, filepath, parse_rule, case_insensitive)
    replace_file(filepath, locations, replacement)


def sub_string(
    search_query: str,
    to_replace: str,
    replacement: str,
    search_query_parse_rule: lal.GrammarRule = lal.default_grammar_rule,
    to_replace_parse_rule: lal.GrammarRule = lal.default_grammar_rule,
    case_insensitive: bool = False,
) -> str:
    """
    Similar to re.sub; search for the search query in the to_replace string, replace all matches with the replacement

    :param search_query: The pattern to search for
    :param to_replace: The string on which the sub operation is performed
    :param replacement: The string to replace the matched text with
    :param search_query_parse_rule: The parse rule used to parse the search query
    :param to_replace_parse_rule: The parse rule used to parse the string on which the sub operation is performed
    :param case_insensitive: Boolean, enables case insensitive searching
    :return: The resulting string after substituting the found matches with the replacement
    """
    locations = findall_string(
        search_query,
        to_replace,
        search_query_parse_rule,
        to_replace_parse_rule,
        case_insensitive,
    )
    return replace_string(to_replace, locations, replacement, None)


def replace_string(
    to_replace: str,
    locations: List[Location],
    replacement: str,
    indexes: List[int] = None,
) -> str:
    """
    Api wrapper around replacer.replace_string()

    :param to_replace: The string to perform a replace operation on
    :param locations: The locations in the string to replace
    :param replacement: The string to replace the specified locations with
    :param indexes: The locations targeted for the replace operations, only replace the locations as specified by the indexes inclued in the indexes list. Replace all locations if indexes is None
    :return: The resulting string after replacing the specified locations with the replacement
    """
    return rep.replace_string(to_replace, locations, replacement, indexes)


def replace_file(
    filepath: str,
    locations: List[Location],
    replacement: str,
    indexes: List[int] = None,
    output: str = None,
):
    """
    Api wrapper around replacer.replace_file()

    :param filepath: The the filepath for the file to replace in
    :param locations: The locations in the string to replace
    :param replacement: The string to replace the specified locations with
    :param indexes: The locations targeted for the replace operations, only replace the locations as specified by the indexes inclued in the indexes list. Replace all locations if indexes is None
    :param output: The filepath for the file to write the output to. If None, write to the same file as filepath
    """
    rep.replace_file(filepath, locations, replacement, indexes, output)


def _execute_search(
    pattern: lal.AdaNode, operand: lal.AdaNode, case_insensitive: bool
) -> List[Location]:
    """
    Api wrapper around searchResult.execute_search()

    :param pattern: The parse tree to search for
    :param operand: The parse tree to search in
    :param case_insensitive: Whether to enable case insensitive searching
    :return: The list of locations where the operand matches the search pattern
    """
    return sr.execute_search(pattern, operand, case_insensitive)


def _analyze_string(string: str, parse_rule: lal.GrammarRule) -> lal.AnalysisUnit:
    """
    Creates a parse tree from a text fragment using the specified rule

    :param string: The string to parse into a parse tree
    :param parse_rule: The parse rule used to parse the string
    :return: The analysis unit containing the created parse tree
    """
    context = lal.AnalysisContext()
    unit = context.get_from_buffer(
        "", string, rule=getattr(lal.GrammarRule, parse_rule)
    )
    if not unit.diagnostics:
        return unit
    else:
        raise ValueError


def _analyze_string_try_rules(
    string: str, rules_to_try: List[lal.GrammarRule]
) -> Tuple[lal.AnalysisUnit, List[lal.GrammarRule]]:
    """
    Creates a tree from text fragment

    :param string: The string to parse into a parse tree
    :param rules_to_try: The parse rules to try to parse the string with
    :return: A tuple with the analysis unit containing the parsed tree and the list of rules that were tried
    """
    tried_rules: List[lal.GrammarRule] = []
    for idx, rule in enumerate(rules_to_try):
        tried_rules.append(rule)
        if idx != 0:
            print(rules_to_try[idx - 1], "failed, retrying with", rule)
        try:
            unit = _analyze_string(string, rule)
            print("Succeeded with", rule)
            return (unit, tried_rules)
        except ValueError:
            pass
    raise ValueError


def _analyze_file(filepath: str) -> lal.AnalysisUnit:
    """
    Creates a tree from ada file

    :param filepath: The the filepath for the file to parse into a tree
    :return: An analysis unit containing the tree
    """
    context = lal.AnalysisContext()
    unit = context.get_from_file(filepath)
    if not unit.diagnostics:
        return unit
    for diagnostic in unit.diagnostics:
        print(diagnostic)
    raise ValueError
