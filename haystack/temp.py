import api
import libadalang as lal # type: ignore


def run_test(find_pattern: str, find_pattern_parse_rule: lal.GrammarRule, replace_pattern: str, input: str, input_parse_rule: lal.GrammarRule):
    return api.sub_string(find_pattern, input, replace_pattern, find_pattern_parse_rule, input_parse_rule, False)



print(run_test("not (not $S_Cond)", lal.GrammarRule.expr_rule, "$S_Cond", "not (not X)", lal.GrammarRule.expr_rule))
print(run_test("$S_X + $S_X", lal.GrammarRule.expr_rule, "2*$S_X", "5+6", lal.GrammarRule.expr_rule))