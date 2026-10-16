"""Named diagnostic allowance; never an arbitrary override of qualification."""


def allowance(profile, theory, discovery, planning, resource):
    if profile == "standard":
        return 3
    if profile == "diagnostic-plus6" and (theory, discovery, planning, resource) == (3, 5, 1, 1):
        return 9
    raise ValueError("diagnostic-plus6 requires compositional T3/D5/P1/R1")


def profile_certificate(proof, profile, extra):
    if profile == "standard":
        return proof
    return {
        **proof,
        "budget_profile": profile,
        "actual_action_budget": proof["reference_action_upper"] + extra,
        "diagnostic_additional_actions": 6,
        "budget_scope": "paired budget diagnostic, not the standard R1 score",
    }
