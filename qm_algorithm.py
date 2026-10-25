
from itertools import combinations


def to_binary(number, n):
    return format(number, f"0{n}b")


def combine_terms(term1, term2):
    """Combine two patterns that differ in exactly one bit."""
    differences = 0
    result = []

    for a, b in zip(term1, term2):
        if a == b:
            result.append(a)
        elif a != "-" and b != "-":
            differences += 1
            result.append("-")
        else:
            return None

    return "".join(result) if differences == 1 else None


def find_prime_implicants(minterms, n):
    """Find prime implicants using the Quine-McCluskey method."""
    current = {to_binary(m, n): {m} for m in minterms}
    prime_implicants = {}

    while current:
        used = set()
        next_round = {}
        groups = {}

        for pattern in current:
            weight = pattern.count("1")
            groups.setdefault(weight, []).append(pattern)

        for weight in sorted(groups):
            for term1 in groups[weight]:
                for term2 in groups.get(weight + 1, []):
                    combined = combine_terms(term1, term2)

                    if combined is not None:
                        used.update([term1, term2])
                        covered = current[term1] | current[term2]
                        next_round.setdefault(
                            combined, set()
                        ).update(covered)

        for pattern in current:
            if pattern not in used:
                prime_implicants.setdefault(
                    pattern, set()
                ).update(current[pattern])

        current = next_round

    return prime_implicants


def select_minimum_cover(prime_implicants, minterms):
    """
    Find a cover with the fewest implicants.
    Break ties by choosing the cover with fewer literals.
    """
    minterms = set(minterms)
    patterns = sorted(prime_implicants)

    coverage = {
        pattern: set(prime_implicants[pattern]) & minterms
        for pattern in patterns
    }

    essential = set()

    # Find essential prime implicants.
    for m in minterms:
        covering = [
            p for p in patterns if m in coverage[p]
        ]
        if len(covering) == 1:
            essential.add(covering[0])

    covered = (
        set().union(*(coverage[p] for p in essential))
        if essential else set()
    )

    remaining = minterms - covered
    others = [p for p in patterns if p not in essential]
    selected_extra = []

    if remaining:
        # Search by increasing number of additional implicants.
        for size in range(1, len(others) + 1):
            valid_covers = []

            for candidate in combinations(others, size):
                candidate_coverage = set().union(
                    *(coverage[p] for p in candidate)
                )

                if remaining <= candidate_coverage:
                    valid_covers.append(candidate)

            if valid_covers:
                # Among equal-sized covers, minimize literal count.
                best = min(
                    valid_covers,
                    key=lambda candidate: (
                        sum(
                            p.count("0") + p.count("1")
                            for p in candidate
                        ),
                        tuple(sorted(candidate)),
                    ),
                )

                selected_extra = list(best)
                break
        else:
            raise ValueError(
                "Could not cover all required minterms."
            )

    selected = essential | set(selected_extra)

    return {
        "coverage": coverage,
        "essential": sorted(essential),
        "selected": sorted(selected),
    }


def _validate_terms(terms, n, term_name):
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError(
            "Number of variables must be a positive integer."
        )

    terms = list(terms)

    if any(
        not isinstance(m, int)
        or isinstance(m, bool)
        or m < 0
        or m >= 2**n
        for m in terms
    ):
        raise ValueError(
            f"{term_name} must be integers between 0 and {2**n - 1}."
        )

    return sorted(set(terms))


def minimize_sop(minterms, n):
    """Minimize a Boolean function in Sum of Products form."""
    minterms = _validate_terms(minterms, n, "Minterms")

    if not minterms:
        return {
            "prime_implicants": {},
            "coverage": {},
            "essential": [],
            "selected": [],
        }

    prime_implicants = find_prime_implicants(minterms, n)
    result = select_minimum_cover(prime_implicants, minterms)

    return {
        "prime_implicants": prime_implicants,
        **result,
    }


def pattern_to_expression(pattern):
    """Convert a binary pattern into an SOP product term."""
    variables = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    terms = []

    for i, bit in enumerate(pattern):
        if bit == "1":
            terms.append(variables[i])
        elif bit == "0":
            terms.append(variables[i] + "'")

    return "".join(terms) if terms else "1"


def minimize_pos(maxterms, n):
    """Minimize a Boolean function in Product of Sums form."""
    maxterms = _validate_terms(maxterms, n, "Maxterms")

    if not maxterms:
        return {
            "prime_implicants": {},
            "coverage": {},
            "essential": [],
            "selected": [],
        }

    prime_implicants = find_prime_implicants(maxterms, n)
    result = select_minimum_cover(prime_implicants, maxterms)

    return {
        "prime_implicants": prime_implicants,
        **result,
    }


def pattern_to_pos_term(pattern):
    """Convert a zero-row pattern into a POS sum term."""
    variables = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    literals = []

    for i, bit in enumerate(pattern):
        if bit == "-":
            continue
        elif bit == "0":
            literals.append(variables[i])
        else:
            literals.append(variables[i] + "'")

    return "(" + " + ".join(literals) + ")" if literals else "0"
