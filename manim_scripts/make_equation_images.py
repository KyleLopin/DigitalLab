# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"


import matplotlib.pyplot as plt


def spec_latex(
    name="F",
    var_names=("A","B","C"),
    minterms=None,
    maxterms=None,
    dont_cares=None,
    style="sum"  # "sum" -> Σ m(...), "prod" -> Π M(...)
):
    """
    Build a LaTeX mathtext string for Boolean function spec.
    - style="sum":  F = Σ m(...) [+ Σ d(...)]
    - style="prod": F = Π M(...) [+ Π D(...)]
    You can pass either minterms (sum) or maxterms (prod), plus don’t cares.
    """
    minterms = [] if minterms is None else sorted(minterms)
    maxterms = [] if maxterms is None else sorted(maxterms)
    dont_cares = [] if dont_cares is None else sorted(dont_cares)

    vars_str = ",".join(var_names)
    lhs = f"{name}({vars_str})"

    if style == "sum":
        if not minterms and not dont_cares:
            raise ValueError("Provide minterms and/or dont_cares for sum style.")
        parts = []
        if minterms:
            parts.append(r"\sum m(" + ",".join(map(str, minterms)) + ")")
        if dont_cares:
            parts.append(r"\sum d(" + ",".join(map(str, dont_cares)) + ")")
        rhs = " + ".join(parts)
    elif style == "prod":
        if not maxterms and not dont_cares:
            raise ValueError("Provide maxterms and/or dont_cares for prod style.")
        parts = []
        if maxterms:
            parts.append(r"\prod M(" + ",".join(map(str, maxterms)) + ")")
        if dont_cares:
            parts.append(r"\prod D(" + ",".join(map(str, dont_cares)) + ")")
        rhs = " \cdot ".join(parts)
    else:
        raise ValueError('style must be "sum" or "prod"')

    return rf"${lhs} \;=\; {rhs}$"


def show_spec(spec_str, figsize=(7,1.8), save_path=None):
    """Render the LaTeX string in a clean Matplotlib figure."""
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis("off")
    ax.text(0.5, 0.5, spec_str, ha="center", va="center", fontsize=20)
    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=160)
    plt.show()



if __name__ == '__main__':
    # example minterms
    s2 = spec_latex(name="f", var_names=("A", "B", "C", "D"),
                    minterms=[0, 2, 5, 10], dont_cares=[3, 6, 9, 13, 14, 15], style="sum")
    show_spec(s2)

    # example MaxTerms
    s3 = spec_latex(name="f", var_names=("A", "B", "C", "D"),
                    maxterms=[1, 3, 10, 11, 13, 14, 15], dont_cares=[4, 6], style="prod")
    show_spec(s3)
