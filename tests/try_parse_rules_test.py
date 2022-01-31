"""
Module containing all tests that tests whether the _try_rules method
is able to find rules to parse various forms of valid ada code.
"""
import libadalang as lal  # type: ignore
from Haystack import api

# pylint: disable=missing-function-docstring
# pylint: disable=protected-access


def test_expr():
    assert not api._analyze_string_try_rules(
        'Put ("Hello World!")', lal.GrammarRule._c_to_py
    )[0].diagnostics


def test_identifier():
    assert not api._analyze_string_try_rules("x", lal.GrammarRule._c_to_py)[
        0
    ].diagnostics


def test_definition():
    assert not api._analyze_string_try_rules("x : Integer", lal.GrammarRule._c_to_py)[
        0
    ].diagnostics


def test_assignment():
    assert not api._analyze_string_try_rules(
        "x : Integer := 10", lal.GrammarRule._c_to_py
    )[0].diagnostics


def test_type():
    assert not api._analyze_string_try_rules(
        """
    type Comparator is
        access function (A, B: Point) return integer;
    """,
        lal.GrammarRule._c_to_py,
    )[0].diagnostics


def test_procedure():
    assert not api._analyze_string_try_rules(
        """
    procedure Print(Arr: Point_Arr) is
    begin
        Put("[");
        for I in Arr'Range loop
            Put("(");
            Put(Arr(I).X);
            Put(",");
            Put(Arr(I).Y);
            Put(")");
        end loop;
        Put_Line("]");
    end Print;
    """,
        lal.GrammarRule._c_to_py,
    )[0].diagnostics


def test_while_loop():
    assert not api._analyze_string_try_rules(
        """
    while A < B loop
        A := A + 1;
    end loop;
    """,
        lal.GrammarRule._c_to_py,
    )[0].diagnostics


def test_if_then_else_statement():
    assert not api._analyze_string_try_rules(
        """
    if A > B then
        Put("A");
    elsif A < B then
        Put("B");
    else
        Put("A = B");
    end if;
    """,
        lal.GrammarRule._c_to_py,
    )[0].diagnostics


def test_requeue_with_abort():
    assert not api._analyze_string_try_rules(
        "requeue T2.E2 with abort;", lal.GrammarRule._c_to_py
    )[0].diagnostics


def test_abs_expr():
    assert not api._analyze_string_try_rules("y := abs x;", lal.GrammarRule._c_to_py)[
        0
    ].diagnostics


def test_abstract_type():
    assert not api._analyze_string_try_rules(
        "function Abstract_Class_Member return Object is abstract;",
        lal.GrammarRule._c_to_py,
    )[0].diagnostics


def test_accept():
    assert not api._analyze_string_try_rules(
        """
    accept Insert (An_Item : in Item) do
        Datum := An_Item;
    end Insert;
    """,
        lal.GrammarRule._c_to_py,
    )[0].diagnostics


def test_access():
    assert not api._analyze_string_try_rules(
        "type Person_Access is access Person;", lal.GrammarRule._c_to_py
    )[0].diagnostics


def test_aliased_declaration():
    assert not api._analyze_string_try_rules(
        "I : aliased Integer := 0;", lal.GrammarRule._c_to_py
    )[0].diagnostics


def test_all_assignment():
    assert not api._analyze_string_try_rules(
        "Obj1.all := Obj2.all;", lal.GrammarRule._c_to_py
    )[0].diagnostics


def test_findall_file_try_rules():
    loc = api.findall_file_try_rules(
        'Put("[")', "tests/test_programs/dosort.adb", lal.GrammarRule._c_to_py, False
    )[0]

    assert (
        loc.start_line == 31
        and loc.start_char == 7
        and loc.end_line == 31
        and loc.end_char == 15
    )
