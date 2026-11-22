"""Scientific semantics, public-information witnesses, and independent posterior checks."""

from collections import defaultdict
from itertools import product

import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from nexus.cli import app
from nexus.engine.canonical import canonical_hash
from nexus.engine.network import response
from nexus.engine.replay import execute_with_trace, replay
from nexus.engine.resonance import RESONANT_BENCH, resonance, settings
from nexus.generator import generate_episode, qualify_episode
from nexus.generator.network import compile_network
from nexus.generator.resonance import ResonantBelief, calibration_prior
from nexus.models.actions import ACTION_ADAPTER
from nexus.models.episode import PrivateEpisode
from nexus.models.network import FIELD, NetworkSample
from nexus.protocol.http import create_single_session_app
from nexus.protocol.session import Session


def episode(d=5, p=0, r=0, seed=7, t=3):
    return generate_episode(
        seed,
        axis_version=2,
        science_family="resonant-network-v1",
        discovery_level=d,
        theory_level=t,
        planning_level=p,
        resource_pressure=r,
        verifier_secret="resonance-test-secret",
    )


def act(session, **action):
    return session.act(session.state.turn, ACTION_ADAPTER.validate_python(action))


def h_oracle(h, x, y):
    return (h.alpha * x + h.beta * y, h.alpha * x * x + h.beta * y, h.alpha * x + h.beta * y * y)[
        h.gate
    ] % 7


def g_oracle(w, x, y):
    a, b, c, d = w.a, w.b, w.c, w.d
    i, j, k = w.gates
    u, v = (x + a, x * a, x * x + a)[i] % 7, (y + b, y * b, y * y + b)[j] % 7
    return (u * v + c * u * u + d * v * v, (u + c) * v * v + d * u, (u * u + c) * v + d * u * v)[
        k
    ] % 7


def test_independent_complete_arithmetic_and_scientific_shortcuts():
    hs, hp = calibration_prior()
    gs, _ = compile_network()
    assert hp.minimum_guaranteed_measurements() == hp.minimum_fixed_measurements() == 2
    for h in hs:
        for x, y in product(range(7), repeat=2):
            assert resonance(h, x, y) == h_oracle(h, x, y)
    for g in gs:
        for x, y in product(range(7), repeat=2):
            assert response(g, x, y) == g_oracle(g, x, y)
    # The obvious unit-axis calibration does not determine structure.
    groups = defaultdict(set)
    for h in hs:
        groups[h_oracle(h, 0, 1), h_oracle(h, 1, 0)].add(tuple(h_oracle(h, *p) for p in FIELD))
    assert any(len(targets) > 1 for targets in groups.values())
    # Even all axis coordinates cannot replace mixed D5 preparations.
    groups = defaultdict(set)
    for g in gs:
        groups[tuple(g_oracle(g, *p) for p in RESONANT_BENCH if 0 in p)].add(
            tuple(g_oracle(g, *p) for p in FIELD)
        )
    assert sum(len(targets) > 1 for targets in groups.values()) == 202


def test_factor_posterior_matches_explicit_joint_oracle_after_wrong_finish_and_experiments():
    e = episode()
    posterior = ResonantBelief(e.public.investigation)
    hs, _ = calibration_prior()
    gs, _ = compile_network()
    h_fields = [tuple(h_oracle(h, *p) for p in FIELD) for h in hs]
    g_fields = [tuple(g_oracle(g, *p) for p in FIELD) for g in gs]
    oracle = {
        (h, g): (0, *((a + b) % 7 for a, b in zip(h_fields[h], g_fields[g], strict=True)))
        for h, g in product(range(27), range(2187))
    }
    assert posterior.counts() == (59049, 2401)
    rejected = (0, 2, 2, 5, 5)
    posterior.excluded.add(rejected)
    oracle = {pair: v for pair, v in oracle.items() if v != rejected}
    assert len(oracle) == 59036
    # The goal exclusion creates correlation despite unchanged marginals.
    assert len({h for h, _ in oracle}) == 27 and len({g for _, g in oracle}) == 2187
    actual_h, actual_g = next(iter(oracle))
    for machine, point, tuned in (
        ("meter", (1, 1), (h_oracle(hs[actual_h], 1, 1) + 1) % 7),
        ("calibrator", (0, 6), None),
        ("meter", (2, 2), h_oracle(hs[actual_h], 2, 2)),
        ("calibrator", (6, 0), None),
        ("meter", (3, 2), h_oracle(hs[actual_h], 3, 2)),
    ):
        x, y = point
        sample = {"x": x, "y": y}
        if machine == "calibrator":
            value = h_oracle(hs[actual_h], x, y)
            sample["reading"] = value
            oracle = {pair: v for pair, v in oracle.items() if h_oracle(hs[pair[0]], x, y) == value}
        else:
            signal = tuned == h_oracle(hs[actual_h], x, y)
            value = g_oracle(gs[actual_g], x, y)
            sample.update(signal=signal, reading=value if signal else None)
            oracle = {
                pair: v
                for pair, v in oracle.items()
                if (h_oracle(hs[pair[0]], x, y) == tuned) == signal
                and (not signal or g_oracle(gs[pair[1]], x, y) == value)
            }
        posterior.measure(machine, sample, tuned)
        assert {(h, g): v for h, g, v in posterior.compatible_pairs()} == oracle
        assert posterior.counts() == (len(oracle), len(set(oracle.values())))


@pytest.mark.parametrize("d", [4, 5])
@pytest.mark.parametrize("p,r", list(product(range(4), range(3))))
def test_supported_profiles_win_and_replay_with_public_policy(d, p, r):
    e = episode(d, p, r)
    state, trace = execute_with_trace(
        e, [ACTION_ADAPTER.validate_python(a) for a in e.reference_plan]
    )
    assert state.terminal_status == "won" and trace[-1].victory_code
    assert canonical_hash(replay(e, trace)) == canonical_hash(state)
    assert PrivateEpisode.model_validate_json(e.model_dump_json()) == e
    assert state.turn <= e.generation_metadata.guaranteed_policy_action_count
    assert (e.public.initial_state.resources.actions_remaining is None) == (r == 0)
    if (p, r) == (1, 1):
        assert e.generation_metadata.action_budget < 92


def test_no_signal_is_valid_atomic_probe_and_configuration_is_not_feedback():
    e = episode(d=4)
    s = Session(e)
    out = act(s, type="take", artifact="S1-1")
    artifact = out.events[0]["details"]["artifact"]
    value = resonance(e.investigation_truth.resonance, 1, 1)
    out = act(s, type="configure", machine="meter", settings=[(value + 1) % 7])
    assert out.ok and out.performance is None
    assert s.observe().visible_machines[0] is not None
    specimen_before = s.state.artifacts[artifact].model_dump()
    turn = s.state.turn
    out = act(s, type="probe", machine="meter", artifact=artifact)
    sample = out.events[0]["details"]["result"]["sample"]
    assert out.ok and sample["signal"] is False and sample.get("reading") is None
    assert s.state.turn == turn + 1 and s.state.artifacts[artifact].model_dump() == specimen_before
    out = act(s, type="configure", machine="meter", settings=[value])
    assert out.ok
    out = act(s, type="operate", machine="meter", artifact=artifact)
    assert out.ok and s.state.artifacts[artifact].sample.signal is True
    assert s.state.artifacts[artifact].sample.reading == response(e.investigation_truth, 1, 1)
    out = act(s, type="operate", machine="shift", artifact=artifact)
    assert out.ok and s.state.artifacts[artifact].sample.signal is None
    assert s.state.artifacts[artifact].sample.reading is None
    for settings_ in ([7], [0, 1]):
        before = canonical_hash(s.state)
        assert not act(s, type="configure", machine="meter", settings=settings_).ok
        assert canonical_hash(s.state) == before
    s.state.artifacts[artifact].sample = NetworkSample(x=4, y=1)
    for machine in ("calibrator", "meter", "controller"):
        before = canonical_hash(s.state)
        assert not act(s, type="probe", machine=machine, artifact=artifact).ok
        assert canonical_hash(s.state) == before


def test_no_forced_calibration_stage_and_zero_is_a_valid_signal():
    e = episode()
    s = Session(e)
    out = act(s, type="take", artifact="S0-0")
    artifact = out.events[0]["details"]["artifact"]
    out = act(s, type="probe", machine="meter", artifact=artifact)
    assert out.ok and out.events[0]["details"]["result"]["sample"]["signal"] is True
    # Find an admitted zero-response bench experiment and verify its distinct signal flag.
    gs, _ = compile_network()
    g, point = next((g, p) for g in gs for p in RESONANT_BENCH if response(g, *p) == 0)
    e.investigation_truth = g.model_copy(update={"resonance": e.investigation_truth.resonance})
    s.state.artifacts[artifact].sample = NetworkSample(x=point[0], y=point[1])
    act(
        s,
        type="configure",
        machine="meter",
        settings=[resonance(e.investigation_truth.resonance, *point)],
    )
    out = act(s, type="probe", machine="meter", artifact=artifact)
    sample = out.events[0]["details"]["result"]["sample"]
    assert sample["signal"] is True and sample["reading"] == 0


def test_http_contract_has_no_active_diagnostics_and_terminal_metrics_are_exact():
    e = episode(p=1, r=1)
    client = TestClient(create_single_session_app(e))
    manifest = client.get("/manifest").json()
    contract = next(r for r in manifest["action_contract"]["reference"] if r["type"] == "configure")
    assert "meter" in contract["description"]
    for action in e.reference_plan:
        out = client.post(
            "/action",
            json={"expected_turn": client.get("/status").json()["turn"], "action": action},
        ).json()
        assert out["ok"]
        if out["observation"]["terminal_status"] == "active":
            assert "performance" not in out
    assert "performance" not in out
    metrics = client.post("/finalize").json()["performance"]
    assert metrics["first_submission_correct"]
    assert metrics["target_classes_before_first_submission"] == 1
    assert metrics["controller_submissions"] == 1
    assert metrics["measurements_used"] <= 7


def test_failed_submission_then_investigation_preserves_joint_feedback():
    e = episode()
    s = Session(e)
    wrong = list(settings(e.investigation_truth))
    wrong[1] = (wrong[1] + 1) % 7
    act(s, type="configure", machine="controller", settings=wrong)
    out = act(s, type="finish")
    assert out.ok and s.state.terminal_status == "active" and out.performance is None
    for action in e.reference_plan:
        shifted = dict(action)
        artifact = shifted.get("artifact", "")
        if "." in artifact:
            stock, turn = artifact.rsplit(".", 1)
            shifted["artifact"] = f"{stock}.{int(turn) + 2}"
        out = act(s, **shifted)
        assert out.ok
    assert s.state.terminal_status == "won"
    assert out.performance.first_submission_correct is False
    assert out.performance.target_classes_before_first_submission == 2401
    assert out.performance.controller_submissions == 2
    assert out.performance.failed_finishes == 1


@pytest.mark.parametrize(
    "mutation", ["setting", "calibration", "program", "budget", "evidence", "plan", "family"]
)
def test_tampered_compilations_reject_before_expensive_replay(mutation):
    e = episode()
    if mutation == "setting":
        e.public.initial_state.machines["meter"].settings = (2,)
    elif mutation == "calibration":
        e.investigation_truth = e.investigation_truth.model_copy(update={"resonance": None})
    elif mutation == "program":
        e.investigation_truth = e.investigation_truth.model_copy(update={"program": ()})
    elif mutation == "budget":
        e.public.initial_state.resources.actions_remaining = 1
    elif mutation == "evidence":
        e.public.evidence_files["manual.md"] += "altered"
    elif mutation == "plan":
        e.reference_plan = ({"type": "finish"},)
    else:
        e.public.investigation = e.public.investigation.model_copy(
            update={"version": "coupled-network-v1"}
        )
    if mutation == "program":
        with pytest.warns(UserWarning, match="Pydantic serializer"):
            assert not qualify_episode(e).passed
    else:
        assert not qualify_episode(e).passed


@pytest.mark.slow
@pytest.mark.parametrize("d", [4, 5])
def test_all_factor_witnesses_replay_and_compose(d):
    report = qualify_episode(episode(d=d, p=1, r=2))
    assert report.passed, report.errors
    assert report.metrics["factor_witnesses_replayed"] == 2215


def test_seed_pairing_and_cli_environment(monkeypatch):
    import uvicorn

    for seed in (7, 17, 23, 41, 73):
        left, right = episode(d=4, seed=seed), episode(d=5, p=1, r=1, seed=seed)
        assert left.investigation_truth == right.investigation_truth
        old = generate_episode(
            seed,
            axis_version=2,
            science_family="coupled-network-v1",
            discovery_level=4,
            theory_level=3,
            verifier_secret="resonance-test-secret",
        )
        assert old.investigation_truth == left.investigation_truth.model_copy(
            update={"resonance": None}
        )
        assert old.public.episode_id != left.public.episode_id
    captured = {}
    monkeypatch.setattr(uvicorn, "run", lambda app, **kwargs: captured.update(app=app))
    result = CliRunner().invoke(
        app,
        ["serve-session", "--seed", "7"],
        env={
            "NEXUS_AXIS_VERSION": "2",
            "NEXUS_SCIENCE_FAMILY": "resonant-network-v1",
            "NEXUS_THEORY_LEVEL": "3",
            "NEXUS_DISCOVERY_LEVEL": "5",
        },
    )
    assert result.exit_code == 0, result.output
    client = TestClient(captured["app"])
    assert "resonance" in client.get("/manifest").json()["description"]
