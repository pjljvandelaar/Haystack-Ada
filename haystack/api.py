from typing import List, Tuple
import searchresult as sr
import replacer as rep
from location import Location
import libadalang as lal # type: ignore


def findall_file(
    search_query: str,
    filepath: str,
    parse_rule: lal.GrammarRule = lal.default_grammar_rule,
    case_insensitive: bool = False,
) -> List[Location]:
    """
    Similar to re.findall; return all matches of search_query in a file at location filepath.
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
    """
    if not parse_rules_to_try:
        raise ValueError
    try:
        pattern, tried_rules = _analyze_string_try_rules(
            search_query, parse_rules_to_try
        )
        operand = _analyze_file(filepath)
    except ValueError as error:
        raise error
    matches = _execute_search(pattern.root, operand.root, case_insensitive)
    if not matches:
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
    locations = findall_string(search_query, to_replace, search_query_parse_rule, to_replace_parse_rule, case_insensitive)
    return rep.replace_string(to_replace, locations, replacement, None)


def replace_file(filepath: str, locations: List[Location], replacement: str):
    rep.replace_file(filepath, locations, replacement, None, None)


def _execute_search(
    pattern: lal.AdaNode, operand: lal.AdaNode, case_insensitive: bool
) -> List[Location]:
    search = sr.SearchResult(case_insensitive)
    search.is_subtree(operand, pattern)
    return search.locations


def _analyze_string(string: str, parse_rule: lal.GrammarRule) -> lal.AnalysisUnit:
    """
    Creates a tree from a text fragment using the specified rule

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
    query: str, rules: List[lal.GrammarRule]
) -> Tuple[lal.AnalysisUnit, List[lal.GrammarRule]]:
    """
    Creates a tree from text fragment

    :return: An analysis unit containing the tree
    """
    tried_rules: List[lal.GrammarRule] = []
    for idx, rule in enumerate(rules):
        if idx != 0:
            print(rules[idx - 1], "failed, retrying with", rule)
        try:
            unit = _analyze_string(query, rule)
            print("Succeeded with", rule)
            return (unit, tried_rules)
        except ValueError:
            tried_rules.append(rule)
    raise ValueError


def _analyze_file(filepath: str) -> lal.AnalysisUnit:
    """
    Creates a tree from ada file

    :return: An analysis unit containing the tree
    """
    context = lal.AnalysisContext()
    unit = context.get_from_file(filepath)
    if not unit.diagnostics:
        return unit
    for diagnostic in unit.diagnostics:
        print(diagnostic)
    raise ValueError
