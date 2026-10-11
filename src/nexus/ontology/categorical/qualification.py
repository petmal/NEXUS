"""PoC conformance qualification, explicitly not production D-axis calibration."""


def qualify_categorical(episode):
    from nexus.generator.qualify import QualificationReport
    from nexus.ontology.categorical.generation import public_policy
    from nexus.protocol.session import Session

    response = public_policy(Session(episode))
    checks = {"public_policy_wins": response.victory_code is not None}
    return QualificationReport(
        passed=all(checks.values()), checks=checks, errors=(), metrics={"experimental": True}
    )
