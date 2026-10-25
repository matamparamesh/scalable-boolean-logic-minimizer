
import streamlit as st

from qm_algorithm import (
    minimize_sop,
    minimize_pos,
    pattern_to_expression,
    pattern_to_pos_term,
)

MAX_INPUT_TERMS = 256

st.set_page_config(
    page_title="Scalable Boolean Logic Minimizer",
    page_icon="🔢",
    layout="wide",
)

st.title("Scalable Boolean Logic Minimizer")
st.write("Using the Quine–McCluskey Tabular Method")

st.info(
    "Enter minterms for SOP or maxterms for POS. "
    "The variable count is user-defined. Large functions may "
    "require substantial computation."
)

mode = st.radio(
    "Choose minimization mode",
    ["SOP", "POS"],
    horizontal=True,
)

n = st.number_input(
    "Number of variables (n)",
    min_value=1,
    value=3,
    step=1,
)

if mode == "SOP":
    st.write("Enter minterms (where F = 1).")
    placeholder = "Example: 1, 3, 5, 7"
else:
    st.write("Enter maxterms (where F = 0).")
    placeholder = "Example: 0, 2, 5, 7"

terms_text = st.text_input(
    "Enter terms separated by commas",
    placeholder=placeholder,
)

st.caption(
    f"Valid indices: 0 to {2 ** int(n) - 1:,}. "
    f"Maximum unique input terms: {MAX_INPUT_TERMS}."
)

if st.button("Minimize Boolean Function", type="primary"):
    try:
        n = int(n)
        limit = 2 ** n

        # Parse input.
        if not terms_text.strip():
            terms = []
        else:
            parts = terms_text.split(",")

            if any(not part.strip() for part in parts):
                raise ValueError(
                    "Separate terms with commas and remove empty entries."
                )

            try:
                terms = [int(part.strip()) for part in parts]
            except ValueError:
                raise ValueError(
                    "All terms must be integers separated by commas."
                )

        # Validate and remove duplicates.
        if any(term < 0 or term >= limit for term in terms):
            raise ValueError(
                f"For {n} variables, terms must be between "
                f"0 and {limit - 1:,}."
            )

        terms = sorted(set(terms))

        if len(terms) > MAX_INPUT_TERMS:
            raise ValueError(
                f"Enter no more than {MAX_INPUT_TERMS} unique terms."
            )

        # Constant functions.
        if not terms:
            expression = "0" if mode == "SOP" else "1"
            st.success("Minimization completed!")
            st.subheader(f"Minimum {mode} Expression")
            st.code(f"F = {expression}")
            st.stop()

        if len(terms) == limit:
            expression = "1" if mode == "SOP" else "0"
            st.success("Minimization completed!")
            st.subheader(f"Minimum {mode} Expression")
            st.code(f"F = {expression}")
            st.stop()

        # Minimize.
        with st.spinner("Minimizing Boolean function..."):
            if mode == "SOP":
                result = minimize_sop(terms, n)
                convert = pattern_to_expression
            else:
                result = minimize_pos(terms, n)
                convert = pattern_to_pos_term

        selected_terms = [
            convert(pattern) for pattern in result["selected"]
        ]

        expression = (
            " + ".join(selected_terms)
            if mode == "SOP"
            else "".join(selected_terms)
        )

        st.success("Minimization completed!")

        st.subheader(f"Minimum {mode} Expression")
        st.code(f"F = {expression}")

        st.subheader("Prime Implicants")
        if result["prime_implicants"]:
            for pattern in result["prime_implicants"]:
                st.write(f"{pattern} → {convert(pattern)}")
        else:
            st.write("No prime implicants.")

        st.subheader("Essential Prime Implicants")
        if result["essential"]:
            for pattern in result["essential"]:
                st.write(f"{pattern} → {convert(pattern)}")
        else:
            st.write("No essential prime implicants.")

        st.subheader("Prime Implicant Coverage Table")

        coverage = result["coverage"]
        prefix = "m" if mode == "SOP" else "M"
        table_data = {"Prime Implicant": []}

        for term in terms:
            table_data[f"{prefix}({term})"] = []

        for pattern, covered in coverage.items():
            table_data["Prime Implicant"].append(
                f"{pattern} → {convert(pattern)}"
            )

            for term in terms:
                table_data[f"{prefix}({term})"].append(
                    "✓" if term in covered else "—"
                )

        st.dataframe(
            table_data,
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "Quine–McCluskey can require exponential time and memory. "
            "An unrestricted variable count does not guarantee that "
            "every large function can be minimized practically."
        )

    except ValueError as error:
        st.error(f"Invalid input: {error}")

    except Exception as error:
        st.error(
            "Minimization could not be completed. "
            f"Details: {error}"
        )
