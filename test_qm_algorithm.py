
import pytest
from itertools import product

from qm_algorithm import (
    minimize_sop,
    minimize_pos,
    pattern_to_expression,
    pattern_to_pos_term,
)


def evaluate_pattern(pattern, bits):
    """Check whether an input matches a binary pattern."""
    for symbol, bit in zip(pattern, bits):
        if symbol != "-" and int(symbol) != bit:
            return False
    return True


# Test 1: Simple SOP minimization
def test_sop_simple():
    result = minimize_sop([1, 3, 5, 7], 3)
    expressions = [
        pattern_to_expression(p) for p in result["selected"]
    ]
    assert expressions == ["C"]


# Test 2: SOP with two terms
def test_sop_two_terms():
    result = minimize_sop([0, 1, 6, 7], 3)
    expressions = {
        pattern_to_expression(p) for p in result["selected"]
    }
    assert expressions == {"A'B'", "AB"}


# Test 3: Constant function F = 1
def test_sop_constant_one():
    result = minimize_sop(list(range(4)), 2)
    assert result["selected"] == ["--"]


# Test 4: Single minterm
def test_sop_single_minterm():
    result = minimize_sop([0], 3)
    assert result["selected"] == ["000"]


# Test 5: Duplicate minterms
def test_sop_duplicates():
    result = minimize_sop([1, 1, 3, 3, 5, 5, 7, 7], 3)
    assert result["selected"] == ["--1"]


# Test 6: POS minimization
def test_pos_example():
    result = minimize_pos([0, 2, 5, 7], 3)
    expressions = {
        pattern_to_pos_term(p) for p in result["selected"]
    }
    assert expressions == {"(A + C)", "(A' + C')"}


# Test 7: Constant function F = 0
def test_pos_constant_zero():
    result = minimize_pos(list(range(8)), 3)
    assert result["selected"] == ["---"]


# Test 8: Invalid minterm
def test_invalid_minterm():
    with pytest.raises(ValueError):
        minimize_sop([8], 3)


# Test 9: Invalid maxterm
def test_invalid_maxterm():
    with pytest.raises(ValueError):
        minimize_pos([8], 3)


# Test 10: SOP truth-table verification
def test_sop_truth_table_equivalence():
    cases = [
        ([1, 3, 5, 7], 3),
        ([0, 1, 6, 7], 3),
        ([0, 2, 4, 6], 3),
        ([0], 3),
        ([0, 1, 2, 3], 2),
    ]

    for minterms, n in cases:
        result = minimize_sop(minterms, n)

        for bits in product([0, 1], repeat=n):
            number = int("".join(map(str, bits)), 2)
            expected = number in minterms

            actual = any(
                evaluate_pattern(pattern, bits)
                for pattern in result["selected"]
            )

            assert actual == expected, (
                f"SOP mismatch: minterms={minterms}, input={bits}"
            )


# Test 11: POS truth-table verification
def test_pos_truth_table_equivalence():
    maxterms = [0, 2, 5, 7]
    n = 3

    result = minimize_pos(maxterms, n)

    for bits in product([0, 1], repeat=n):
        number = int("".join(map(str, bits)), 2)

        # POS patterns represent the rows where F = 0.
        expected = number not in maxterms

        zero_row = any(
            evaluate_pattern(pattern, bits)
            for pattern in result["selected"]
        )

        actual = not zero_row

        assert actual == expected, (
            f"POS mismatch: maxterms={maxterms}, input={bits}"
        )

# Test 12: Verify every SOP function up to 4 variables
def test_all_sop_functions_up_to_4_variables():
    for n in range(1, 5):
        total_rows = 2 ** n

        for function_mask in range(2 ** total_rows):
            minterms = [
                row
                for row in range(total_rows)
                if function_mask & (1 << row)
            ]

            result = minimize_sop(minterms, n)

            for row in range(total_rows):
                bits = tuple(
                    int(bit)
                    for bit in format(row, f"0{n}b")
                )

                expected = row in minterms

                actual = any(
                    evaluate_pattern(pattern, bits)
                    for pattern in result["selected"]
                )

                assert actual == expected, (
                    f"SOP failure: n={n}, "
                    f"minterms={minterms}, input={bits}"
                )


# Test 13: Verify every POS function up to 4 variables
def test_all_pos_functions_up_to_4_variables():
    for n in range(1, 5):
        total_rows = 2 ** n

        for function_mask in range(2 ** total_rows):
            maxterms = [
                row
                for row in range(total_rows)
                if function_mask & (1 << row)
            ]

            result = minimize_pos(maxterms, n)

            for row in range(total_rows):
                bits = tuple(
                    int(bit)
                    for bit in format(row, f"0{n}b")
                )

                expected = row not in maxterms

                zero_row = any(
                    evaluate_pattern(pattern, bits)
                    for pattern in result["selected"]
                )

                actual = not zero_row

                assert actual == expected, (
                    f"POS failure: n={n}, "
                    f"maxterms={maxterms}, input={bits}"
                )
