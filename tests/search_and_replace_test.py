"""
This module contains tests according to some general re-write rules.
Basically, rules that re-write bad code into better code.
"""
import os
import libadalang as lal  # type: ignore
from Haystack import api

# pylint: disable=missing-function-docstring


def test_not_not():
    assert (
        run_test(
            "not (not $S_Cond)",
            lal.GrammarRule.expr_rule,
            "$S_Cond",
            "not (not X)",
            lal.GrammarRule.expr_rule,
        )
        == "X"
    )


def test_not_equal():
    assert (
        run_test(
            "not ($S_Left = $S_Right)",
            lal.GrammarRule.expr_rule,
            "$S_Left/=$S_Right",
            "not(A=B)",
            lal.GrammarRule.expr_rule,
        )
        == "A/=B"
    )


def test_not_different():
    assert (
        run_test(
            "not ($S_Left /= $S_Right)",
            lal.GrammarRule.expr_rule,
            "$S_Left=$S_Right",
            "not(A/=B)",
            lal.GrammarRule.expr_rule,
        )
        == "A=B"
    )


def test_not_greater_than():
    assert (
        run_test(
            "not ($S_Left > $S_Right)",
            lal.GrammarRule.expr_rule,
            "$S_Left<=$S_Right",
            "not(A>B)",
            lal.GrammarRule.expr_rule,
        )
        == "A<=B"
    )


def test_not_greater_equal():
    assert (
        run_test(
            "not ($S_Left >= $S_Right)",
            lal.GrammarRule.expr_rule,
            "$S_Left<$S_Right",
            "not(A>=B)",
            lal.GrammarRule.expr_rule,
        )
        == "A<B"
    )


def test_not_less_than():
    assert (
        run_test(
            "not ($S_Left < $S_Right)",
            lal.GrammarRule.expr_rule,
            "$S_Left>=$S_Right",
            "not(A<B)",
            lal.GrammarRule.expr_rule,
        )
        == "A>=B"
    )


def test_not_less_equal():
    assert (
        run_test(
            "not ($S_Left <= $S_Right)",
            lal.GrammarRule.expr_rule,
            "$S_Left>$S_Right",
            "not(A<=B)",
            lal.GrammarRule.expr_rule,
        )
        == "A>B"
    )


def test_not_in():
    assert (
        run_test(
            "not ($S_Var in $M_Values)",
            lal.GrammarRule.expr_rule,
            "$S_Var not in $M_Values",
            "not(A in 1 .. 5)",
            lal.GrammarRule.expr_rule,
        )
        == "A not in 1 .. 5"
    )


def test_not_not_in():
    assert (
        run_test(
            "not ($S_Var not in $M_Values)",
            lal.GrammarRule.expr_rule,
            "$S_Var in $M_Values",
            "not(A not in 1 .. 5)",
            lal.GrammarRule.expr_rule,
        )
        == "A in 1 .. 5"
    )


def test_equal_true():
    assert (
        run_test(
            "$S_Var = true",
            lal.GrammarRule.expr_rule,
            "$S_Var",
            "A=true",
            lal.GrammarRule.expr_rule,
        )
        == "A"
    )


def test_equal_false():
    assert (
        run_test(
            "$S_Var = false",
            lal.GrammarRule.expr_rule,
            "not $S_Var",
            "A=false",
            lal.GrammarRule.expr_rule,
        )
        == "not A"
    )


def test_different_true():
    assert (
        run_test(
            "$S_Var /= true",
            lal.GrammarRule.expr_rule,
            "not $S_Var",
            "A/=true",
            lal.GrammarRule.expr_rule,
        )
        == "not A"
    )


def test_different_false():
    assert (
        run_test(
            "$S_Var /= false",
            lal.GrammarRule.expr_rule,
            "not $S_Var",
            "A/=false",
            lal.GrammarRule.expr_rule,
        )
        == "not A"
    )


def test_if_different():
    assert (
        run_test(
            """if $S_A /= $S_B then
            $M_Stmts_True;
            else
            $M_Stmts_False;
            end if;""",
            lal.GrammarRule.if_stmt_rule,
            """if $S_A = $S_B then
            $M_Stmts_False;
            else
            $M_Stmts_True;
            end if;""",
            """if A/=B then
            Put ("A /= B");
            else
            Put ("A = B");
            end if;""",
            lal.GrammarRule.if_stmt_rule,
        )
        == """if A = B then
            Put ("A = B");
            else
            Put ("A /= B");
            end if;"""
    )


def test_if_not_condition():
    assert (
        run_test(
            """if not ($S_Cond) then
             $M_Stmts_True;
            else
             $M_Stmts_False;
            end if;""",
            lal.GrammarRule.if_stmt_rule,
            """if $S_Cond then
             $M_Stmts_False;
            else
             $M_Stmts_True;
            end if;""",
            """if not (A > 15) then
             Put_line ("A <= 15");
            else
             Put_line ("A > 15");
            end if;""",
            lal.GrammarRule.if_stmt_rule,
        )
        == """if A > 15 then
             Put_line ("A > 15");
            else
             Put_line ("A <= 15");
            end if;"""
    )


def test_if_not_in():
    assert (
        run_test(
            """if $S_Expr not in $M_Values then
             $M_Stmts_True;
            else
             $M_Stmts_False;
            end if;""",
            lal.GrammarRule.if_stmt_rule,
            """if $S_Expr in $M_Values then
             $M_Stmts_False;
            else
             $M_Stmts_True;
            end if;""",
            """if A not in 1 .. 5 then
             Put_line ("A not in 1 .. 5");
            else
             Put_line ("A in 1 .. 5");
            end if;""",
            lal.GrammarRule.if_stmt_rule,
        )
        == """if A in 1 .. 5 then
             Put_line ("A in 1 .. 5");
            else
             Put_line ("A not in 1 .. 5");
            end if;"""
    )


def test_return_if_condition():
    assert (
        run_test(
            """if $S_Cond then
             return true;
            else
             return false;
            end if;""",
            lal.GrammarRule.if_stmt_rule,
            """return $S_Cond;""",
            """if A then
             return true;
            else
             return false;
            end if;""",
            lal.GrammarRule.if_stmt_rule,
        )
        == """return A;"""
    )


def test_return_if_not_condition():
    assert (
        run_test(
            """if $S_Cond then
             return false;
            else
             return true;
            end if;""",
            lal.GrammarRule.if_stmt_rule,
            """return not ($S_Cond);""",
            """if A then
             return false;
            else
             return true;
            end if;""",
            lal.GrammarRule.if_stmt_rule,
        )
        == """return not (A);"""
    )


def test_null_then_branch_hard():
    assert (
        run_test(
            """if $S_Cond then
             null;
            else
             $S_Stmt; $M_Stmts;
            end if;""",
            lal.GrammarRule.if_stmt_rule,
            """if not ($S_Cond) then
             $S_Stmt; $M_Stmts;
            end if;""",
            """if A then
             null;
            else
             Put ("not A");
            end if;""",
            lal.GrammarRule.if_stmt_rule,
        )
        == """if not (A) then
             Put ("not A"); 
            end if;"""
    )


def test_null_then_branch_easy():
    assert (
        run_test(
            """if $S_Cond then
             null;
            else
             $S_Stmt; $M_Stmts;
            end if;""",
            lal.GrammarRule.if_stmt_rule,
            """if not ($S_Cond) then
             $S_Stmt; $M_Stmts;
            end if;""",
            """if A then
             null;
            else
             Put ("not A"); Put ("test");
            end if;""",
            lal.GrammarRule.if_stmt_rule,
        )
        == """if not (A) then
             Put ("not A"); Put ("test");
            end if;"""
    )


def test_null_else_branch():
    assert (
        run_test(
            """if $S_Cond then
             $M_Stmts;
            else
             null;
            end if;""",
            lal.GrammarRule.if_stmt_rule,
            """if $S_Cond then
             $M_Stmts;
            end if;""",
            """if A then
             Put ("A");
            else
             null;
            end if;""",
            lal.GrammarRule.if_stmt_rule,
        )
        == """if A then
             Put ("A");
            end if;"""
    )


def test_identical_branches():
    assert (
        run_test(
            """if $S_Cond then
             $M_Stmts;
            else
             $M_Stmts;
            end if;""",
            lal.GrammarRule.if_stmt_rule,
            """Boolean := $S_Cond;
            begin
             $M_Stmts;
            end;""",
            """if A then
             Put ("cool");
             Put ("cool");
            else
             Put ("cool");
             Put ("cool");
            end if;""",
            lal.GrammarRule.if_stmt_rule,
        )
        == """Boolean := A;
            begin
             Put ("cool");
             Put ("cool");
            end;"""
    )


def test_identical_branches_wrong1():
    assert (
        run_test(
            """if $S_Cond then
             $M_Stmts;
            else
             $M_Stmts;
            end if;""",
            lal.GrammarRule.if_stmt_rule,
            """Boolean := $S_Cond;
            begin
             $M_Stmts;
            end;""",
            """if A then
             Put ("cool");
             Put ("cool");
            else
             Put ("cool");
            end if;""",
            lal.GrammarRule.if_stmt_rule,
        )
        == """if A then
             Put ("cool");
             Put ("cool");
            else
             Put ("cool");
            end if;"""
    )


def test_identical_branches_wrong2():
    assert (
        run_test(
            """if $S_Cond then
             $M_Stmts;
            else
             $M_Stmts;
            end if;""",
            lal.GrammarRule.if_stmt_rule,
            """Boolean := $S_Cond;
            begin
             $M_Stmts;
            end;""",
            """if A then
             Put ("cool");
             Put ("cool");
            else
             Put ("stupid");
            end if;""",
            lal.GrammarRule.if_stmt_rule,
        )
        == """if A then
             Put ("cool");
             Put ("cool");
            else
             Put ("stupid");
            end if;"""
    )


def test_identical_branches_wrong3():
    assert (
        run_test(
            """if $S_Cond then
             $M_Stmts;
            else
             $M_Stmts;
            end if;""",
            lal.GrammarRule.if_stmt_rule,
            """Boolean := $S_Cond;
            begin
             $M_Stmts;
            end;""",
            """if A then
             Put ("cool");
             Put ("cool");
            else
             Put ("stupid");
             Put ("cool");
            end if;""",
            lal.GrammarRule.if_stmt_rule,
        )
        == """if A then
             Put ("cool");
             Put ("cool");
            else
             Put ("stupid");
             Put ("cool");
            end if;"""
    )


def test_identical_branches_still_wrong():
    assert (
        run_test(
            """if $S_Cond then
             $M_Stmts;
            else
             $M_Stmts;
            end if;""",
            lal.GrammarRule.if_stmt_rule,
            """Boolean := $S_Cond;
            begin
             $M_Stmts;
            end;""",
            """if A then
             Put ("cool");
             Put ("cool");
            else
             Put_line ("stupid");
            end if;""",
            lal.GrammarRule.if_stmt_rule,
        )
        == """if A then
             Put ("cool");
             Put ("cool");
            else
             Put_line ("stupid");
            end if;"""
    )


def test_binary_case_others():
    assert (
        run_test(
            """case $S_Expr is
             when $M_Values => $M_Stmts_In;
             when others => $M_Stmts_Out;
            end case;""",
            lal.GrammarRule.stmt_rule,
            """if ($S_Expr) in $M_Values then
             $M_Stmts_In;
            else
             $M_Stmts_Out;
            end if;""",
            """case A is
             when 1 .. 5 => Put ("A in 1 .. 5");
             when others => Put ("A not in 1 .. 5");
            end case;""",
            lal.GrammarRule.stmt_rule,
        )
        == """if (A) in 1 .. 5 then
             Put ("A in 1 .. 5");
            else
             Put ("A not in 1 .. 5");
            end if;"""
    )


def test_double():
    assert (
        run_test(
            "$S_X + $S_X",
            lal.GrammarRule.expr_rule,
            "2*$S_X",
            "5+5",
            lal.GrammarRule.expr_rule,
        )
        == "2*5"
    )


def test_double_wrong():
    assert (
        run_test(
            "$S_X + $S_X",
            lal.GrammarRule.expr_rule,
            "2*$S_X",
            "5+6",
            lal.GrammarRule.expr_rule,
        )
        == "5+6"
    )


def test_equals_to_range():
    assert (
        run_test(
            "$S_Var = $S_Val1 or else $S_Var = $S_Val2",
            lal.GrammarRule.expr_rule,
            "$S_Var in $S_Val1 | $S_Val2",
            "A = 0 or else A = 1",
            lal.GrammarRule.expr_rule,
        )
        == "A in 0 | 1"
    )


def test_extend_equals_to_range():
    assert (
        run_test(
            "$S_Var in $M_Vals or else $S_Var = $S_Val",
            lal.GrammarRule.expr_rule,
            "$S_Var in $M_Vals | $S_Val",
            "A in 1 .. 5 or else A = 10",
            lal.GrammarRule.expr_rule,
        )
        == "A in 1 .. 5 | 10"
    )


def test_not_equals_to_range():
    assert (
        run_test(
            "$S_Var /= $S_Val1 and then $S_Var /= $S_Val2",
            lal.GrammarRule.expr_rule,
            "$S_Var not in $S_Val1 | $S_Val2",
            "A /= 0 and then A /= 1",
            lal.GrammarRule.expr_rule,
        )
        == "A not in 0 | 1"
    )


def test_list_elements_exact():
    assert (
        run_test(
            "$M_Before; B; C; $M_After;",
            lal.GrammarRule.stmts_rule,
            "$M_Before; X; Y; $M_After;",
            "begin B; C; end;",
            lal.GrammarRule.block_stmt_rule,
        )
        == "begin  X; Y;  end;"
    )


def test_list_elements_exact_repeat_fail():
    assert (
        run_test(
            "$M_Before; B; C; $M_Before;",
            lal.GrammarRule.stmts_rule,
            "$M_Before; X; Y; $M_Before;",
            "begin B; C; Z; end;",
            lal.GrammarRule.block_stmt_rule,
        )
        == "begin B; C; Z; end;"
    )


def test_list_elements_repeat_hard():
    assert (
        run_test(
            "A; $M_Before; B; C; $M_After;",
            lal.GrammarRule.stmts_rule,
            "X; $M_Before; Y; Z; $M_After;",
            "begin A; B; C; D; end;",
            lal.GrammarRule.block_stmt_rule,
        )
        == "begin X;  Y; Z; D; end;"
    )


def test_list_elements_exact_repeat_success():
    assert (
        run_test(
            "$M_Before; B; C; $M_Before;",
            lal.GrammarRule.stmts_rule,
            "$M_Before; X; Y; $M_Before;",
            "begin B; C; end;",
            lal.GrammarRule.block_stmt_rule,
        )
        == "begin  X; Y;  end;"
    )


def test_list_elements_head_tail():
    assert (
        run_test(
            "$M_Before; B; C; $M_After;",
            lal.GrammarRule.stmts_rule,
            "$M_Before; X; Y; $M_After;",
            "begin A; B; C; D; end;",
            lal.GrammarRule.block_stmt_rule,
        )
        == "begin A; X; Y; D; end;"
    )


def test_list_elements_head_tail_repeat_fail():
    assert (
        run_test(
            "$M_Before; B; C; $M_Before;",
            lal.GrammarRule.stmts_rule,
            "$M_Before; X; Y; $M_Before;",
            "begin A; B; C; D; end;",
            lal.GrammarRule.block_stmt_rule,
        )
        == "begin A; B; C; D; end;"
    )


def test_list_elements_head_tail_repeat_success():
    assert (
        run_test(
            "$M_Before; B; C; $M_Before;",
            lal.GrammarRule.stmts_rule,
            "$M_Before; X; Y; $M_Before;",
            "begin A; B; C; A; end;",
            lal.GrammarRule.block_stmt_rule,
        )
        == "begin A; X; Y; A; end;"
    )


def test_list_elements_trails():
    assert (
        run_test(
            "$M_Before; B; C; $M_After;",
            lal.GrammarRule.stmts_rule,
            "$M_Before; X; Y; $M_After;",
            "begin A1; A2; A3; B; C; D1; D2; D3; end;",
            lal.GrammarRule.block_stmt_rule,
        )
        == "begin A1; A2; A3; X; Y; D1; D2; D3; end;"
    )


def test_list_elements_trails_repeat_fail():
    assert (
        run_test(
            "$M_Before; B; C; $M_Before;",
            lal.GrammarRule.stmts_rule,
            "$M_Before; X; Y; $M_Before;",
            "begin A1; A2; A3; B; C; D1; D2; D3; end;",
            lal.GrammarRule.block_stmt_rule,
        )
        == "begin A1; A2; A3; B; C; D1; D2; D3; end;"
    )


def test_list_elements_trails_repeat_success():
    assert (
        run_test(
            "$M_Before; B; C; $M_Before;",
            lal.GrammarRule.stmts_rule,
            "$M_Before; X; Y; $M_Before;",
            "begin A1; A2; A3; B; C; A1; A2; A3; end;",
            lal.GrammarRule.block_stmt_rule,
        )
        == "begin A1; A2; A3; X; Y; A1; A2; A3; end;"
    )


def test_list_elements_anti_greedy1():
    """
    Test shows that we don't get the behaviour we expect!
    """
    assert (
        run_test(
            "$M_Before; $M_Before;",
            lal.GrammarRule.stmts_rule,
            "$M_Before; X; Y; $M_Before;",
            "begin A1; A1; end;",
            lal.GrammarRule.block_stmt_rule,
        )
        != "begin A1; X; Y; A1; end;"
    )


def test_list_elements_anti_greedy2():
    """
    Test shows that we don't get the behaviour we expect!
    """
    assert (
        run_test(
            "$M_Before; $M_Before;",
            lal.GrammarRule.stmts_rule,
            "$M_Before; X; Y; $M_Before;",
            "begin A1; A2; A1; A2; end;",
            lal.GrammarRule.block_stmt_rule,
        )
        != "begin A1; A2; X; Y; A1; A2; end;"
    )


def test_extract_statement1():
    """
    Test shows that we don't get the behaviour we expect!
    """
    assert (
        run_test(
            """if $S_Cond then
             $S_Stmt;
             $M_Stmts_True;
            else
             $S_Stmt;
             $M_Stmts_False;
            end if;""",
            lal.GrammarRule.if_stmt_rule,
            """
            $S_Stmt;
            if $S_Cond then
             $M_Stmts_True;
            else
             $M_Stmts_False;
            end if;""",
            """if A then
             Put ("X");
             Put ("1");
             Put ("2");
            else
             Put ("X");
             Put ("3");
             Put ("4");
            end if;""",
            lal.GrammarRule.if_stmt_rule,
        )
        != """Put ("X");
            if A then
             Put ("1");
             Put ("2");
            else
             Put ("3");
             Put ("4");
            end if;"""
    )


def test_extract_statement2():
    """
    Test shows that we don't get the behaviour we expect!
    """
    assert (
        run_test(
            """if $S_Cond then
             $M_Stmts_True;
             $S_Stmt;
            else
             $M_Stmts_False;
             $S_Stmt;
            end if;""",
            lal.GrammarRule.if_stmt_rule,
            """
            if $S_Cond then
             $M_Stmts_True;
            else
             $M_Stmts_False;
            end if;
            $S_Stmt;""",
            """if A then
             Put ("1");
             Put ("2");
             Put ("X");
            else
             Put ("3");
             Put ("4");
             Put ("X");
            end if;""",
            lal.GrammarRule.if_stmt_rule,
        )
        != """if A then
             Put ("1");
             Put ("2");
            else
             Put ("3");
             Put ("4");
            end if;
            Put ("X");"""
    )


def test_assignment():
    """
    Test shows that we don't get the behaviour we expect!
    """
    assert (
        run_test(
            "$S_Var : $S_Type := $M_Expr;",
            lal.GrammarRule.basic_decl_rule,
            "Y : $S_Type;",
            "X : Integer;",
            lal.GrammarRule.basic_decl_rule,
        )
        != "Y : Integer;"
    )


def test_multiple_matches_single_line():
    assert (
        run_test(
            "Put ($S_expr)",
            lal.GrammarRule.expr_rule,
            "Put_Line ($S_expr)",
            'Put ("Hello"); Put ("World"); Put ("!");',
            lal.GrammarRule.stmts_rule,
        )
        == 'Put_Line ("Hello"); Put_Line ("World"); Put_Line ("!");'
    )


def test_file_substitution():
    filepath = "temp.adb"
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(
            """with Text_IO; use Text_IO;
procedure hello is
begin
    Put ("Hello world!");
end hello;"""
        )
    api.sub_file(
        "Put ($S_expr)", filepath, "Put_Line ($S_expr)", lal.GrammarRule.expr_rule
    )
    with open(filepath, "r", encoding="utf-8") as file:
        lines = file.readlines()
    res = "".join(lines)
    assert (
        res
        == """with Text_IO; use Text_IO;
procedure hello is
begin
    Put_Line ("Hello world!");
end hello;"""
    )
    os.remove(filepath)


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
