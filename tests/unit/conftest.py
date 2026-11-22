"""Fresh episode fixtures shared by interface regression contracts."""
import pytest

from nexus.generator import generate_episode
from nexus.presentation.laboratory import REPAIR, REVISION


@pytest.fixture
def boundary_world():
    def build(scientific):
        return generate_episode(17, axis_version=2 if scientific else 1,
            theory_level=0, discovery_level=0, planning_level=0, resource_pressure=0,
            verifier_secret="review-test")
    return build

@pytest.fixture
def hardened_episode():
    return generate_episode(42, verifier_secret="hardening-test")

@pytest.fixture(scope="module", params=(REPAIR, REVISION))
def clarity_laboratory(request):
    return generate_episode(541 if request.param == REPAIR else 2073, axis_version=2,
        science_family=request.param, theory_level=3, discovery_level=5,
        planning_level=0, resource_pressure=1, verifier_secret="clarity-test")

@pytest.fixture(scope="module", params=(REPAIR, REVISION))
def role_laboratory(request):
    return generate_episode(541, axis_version=2, science_family=request.param,
        theory_level=3, discovery_level=5, planning_level=0, resource_pressure=1)
