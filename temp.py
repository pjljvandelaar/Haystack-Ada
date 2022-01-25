import libadalang as lal # type: ignore
from Haystack import replacer, api
from Haystack.location import Location

print(
    replacer._replace(
        [
            "The quick brown fox jumps over the lazy dog\n",
            "But he fell after jumping over the lazy dog"
        ],
        [
            Location(1, 1, 5, 10, {}),
            Location(1, 1, 21, 26, {}),
            Location(2, 2, 8, 12, {}),
            Location(2, 2, 19, 26, {})
        ],
        "test"
    )
)

def run_test(
    find_pattern: str,
    find_pattern_parse_rule: lal.GrammarRule,
    replace_pattern: str,
    input_string: str,
    input_parse_rule: lal.GrammarRule,
) -> str:
    """
    Wrapper around api.sub_string. It does nothing more than re-order
    the function parameters and giving them different names.
    This was done to make writing the tests slightly easier.
    """
    return api.sub_string(
        find_pattern,
        input_string,
        replace_pattern,
        find_pattern_parse_rule,
        input_parse_rule,
        False,
    )

print( run_test(
        "Put ($S_expr);",
        lal.GrammarRule.stmt_rule,
        "Put_Line ($S_expr);",
        'Put ("Hello"); Put ("World"); Put ("!");',
        lal.GrammarRule.stmts_rule,
    ))