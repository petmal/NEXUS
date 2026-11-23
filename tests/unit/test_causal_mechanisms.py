"""Finite independent science oracle plus live engine and privacy conformance."""

import json
from itertools import product

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from typer.testing import CliRunner

from nexus.cli import app
from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.generator import generate_episode, qualify_episode
from nexus.io import load_private, save_episode
from nexus.models.actions import (
    ConfigureAction,
    DropAction,
    FinishAction,
    OperateAction,
    ProbeAction,
    TakeAction,
)
from nexus.models.domain import DomainArtifact, DomainTruth
from nexus.models.episode import PrivateEpisode
from nexus.models.events import TraceRecord
from nexus.ontology.causal.generation import generate_causal
from nexus.ontology.causal.inference import CausalBelief, initial_mask, partitions, target_set
from nexus.ontology.causal.laws import (
    MISSION,
    POINTS,
    PRIMITIVES,
    WITNESS_EXPERIMENTS,
    WORLDS,
    graphs,
    targets,
)
from nexus.ontology.causal.policy import public_policy
from nexus.ontology.causal.qualification import certificate
from nexus.ontology.causal.runtime import expected
from nexus.ontology.causal.schema import FAMILY, Experiment, Investigation
from nexus.ontology.inference import Measurement
from nexus.protocol.http import create_single_session_app
from nexus.protocol.session import Session


def oracle_step(world, point, mode):
    a, b, _, _, wiring, transition, response = world
    x, y, context = point
    u, v = (y, x) if bool(wiring) != (context == 1) else (x, y)
    next_mode = (mode + a * u + b * v, a * mode + u + b * v, mode + a * (u + v) + b * u * v)[
        transition
    ] % 3
    value = (
        a * u + b * v + mode * (u + context + 1),
        (u + mode) * (v + a) + b * context,
        u * v + a * mode + b * (u + context),
    )[response] % 3
    return next_mode, value


def oracle(world, experiment, sensor=True):
    mode = world.initial
    for point in experiment.history:
        mode, _ = oracle_step(world, point, mode)
    _, value = oracle_step(world, experiment.point, mode)
    if not sensor:
        return value
    offset = world.delta * (experiment.point[2] + 1)
    return ((value if experiment.instrument == "sensor" else 0) + offset) % 3


class Player:
    """Deliberately offers no episode, truth, state, trace or reference-plan access."""

    def __init__(self, session):
        self.act = session.act
        self.observe = session.observe
        self.status = session.status


def act(session, action):
    result = session.act(session.status().turn, action)
    assert result.ok, result.message
    return result


def take(session):
    result = act(session, TakeAction(artifact="stock"))
    return next(e["details"]["artifact"] for e in result.events if e["type"] == "take")


def prepare(session, artifact, experiment):
    for point in experiment.history:
        act(session, ConfigureAction(machine="stage", settings=point))
        act(session, OperateAction(machine="stage", artifact=artifact))
        act(session, OperateAction(machine="pulse", artifact=artifact))
    act(session, ConfigureAction(machine="stage", settings=experiment.point))
    act(session, OperateAction(machine="stage", artifact=artifact))


def test_composed_graphs_match_all_finite_transitions_and_responses():
    # Exhaustive one-step agreement implies agreement for every legal history by induction.
    for a, b, wiring, transition, response in product((1, 2), (1, 2), range(2), range(3), range(3)):
        world = WORLDS[0]._replace(
            a=a, b=b, wiring=wiring, transition=transition, response=response
        )
        tg, rg = graphs(wiring, transition, response)
        for point, mode in product(POINTS, range(3)):
            x, y, e = point
            values = {"x": x, "y": y, "e": e, "p": wiring, "a": a, "b": b, "h": mode, "one": 1}
            assert (
                tg.evaluate(values, PRIMITIVES)[0],
                rg.evaluate(values, PRIMITIVES)[0],
            ) == oracle_step(world, point, mode)


def test_witness_and_transfer_predictions_match_independent_oracle():
    for experiment in (*WITNESS_EXPERIMENTS, *MISSION):
        masks = partitions(experiment)
        for i, world in enumerate(WORLDS):
            assert masks[oracle(world, experiment)] >> i & 1
    assert targets() == tuple(tuple(oracle(w, e, False) for e in MISSION) for w in WORLDS)
    proof = certificate((1 << len(WORLDS)) - 1, 1)
    assert proof["prior_worlds"] == 648
    assert proof["target_classes"] == 113
    assert proof["untreated_observation_classes"] == 126
    assert proof["untreated_ambiguous_classes"] == 120
    assert proof["reference_reading_bound"] == 6
    assert proof["reference_action_bound"] == 40
    # History order has real causal significance for at least one admitted mechanism.
    assert any(oracle(w, MISSION[2], False) != oracle(w, MISSION[3], False) for w in WORLDS)


@pytest.mark.slow
def test_every_admitted_truth_wins_in_live_engine_and_json_replays():
    base = generate_causal(7, resource_pressure=2, verifier_secret="proof-secret")
    for world in WORLDS:
        episode = base.model_copy(deep=True)
        episode.investigation_truth = DomainTruth(ontology=FAMILY, payload=world._asdict())
        episode = PrivateEpisode.model_validate_json(episode.model_dump_json())
        session = Session(episode)
        result = public_policy(Player(session), episode.public.evidence_files)
        assert result.victory_code
        metrics = result.performance
        assert metrics.target_classes_before_first_submission == 1
        assert metrics.first_submission_correct
        assert metrics.actions_used <= 40 and metrics.measurements_used <= 6
        records = [TraceRecord.model_validate_json(r.model_dump_json()) for r in session.trace]
        assert canonical_hash(replay(episode, records)) == canonical_hash(session.state)


@pytest.mark.parametrize(
    "theory,discovery", [(0, 0), (1, 0), (2, 0), (3, 0), (1, 1), (2, 2), (3, 5)]
)
@pytest.mark.parametrize("planning,resources", tuple(product(range(2), range(3))))
def test_supported_profiles_qualify_and_preserve_seed_truth(theory, discovery, planning, resources):
    episode = generate_episode(
        7,
        axis_version=2,
        science_family=FAMILY,
        theory_level=theory,
        discovery_level=discovery,
        planning_level=planning,
        resource_pressure=resources,
        verifier_secret="test",
    )
    assert qualify_episode(episode).passed
    if (theory, discovery) != (2, 2):
        assert episode.investigation_truth == generate_causal(7).investigation_truth
    assert (episode.public.initial_state.resources.actions_remaining is None) == (resources == 0)
    if discovery == 0:
        assert len(target_set(initial_mask(episode.public.investigation.data()))) == 1


def test_known_law_and_known_shape_disclosures_for_every_truth():
    from nexus.ontology.causal.schema import LAW_FIELDS, STRUCTURE_FIELDS

    for world in WORLDS:
        for theory, discovery, fields in ((1, 1, LAW_FIELDS), (2, 2, STRUCTURE_FIELDS)):
            if theory == 2 and world.response == 2:
                continue
            spec = Investigation(
                theory=theory,
                discovery=discovery,
                stock_room="lab",
                mission_room="lab",
                known={k: getattr(world, k) for k in fields},
            )
            proof = certificate(initial_mask(spec), 0, discovery != 2)
            if theory == 1:
                assert proof["reference_reading_bound"] == 1
            else:
                assert (
                    proof["target_classes"] > 9
                )  # At least three ternary readings for a guarantee.
                assert not proof["untreated_readings_insufficient_for_identification"]
                assert proof["reference_reading_bound"] <= 4


@pytest.mark.parametrize("theory,discovery", [(0, 0), (3, 5)])
def test_prefilled_initial_board_cannot_claim_the_empty_board_optimum(theory, discovery):
    from nexus.solver import solve

    episode = generate_causal(17, theory_level=theory, discovery_level=discovery, planning_level=0)
    assert solve(episode).optimal_action_count == 2
    assert not Session(episode).act(0, FinishAction()).victory_code
    normal = Session(episode)
    assert normal.act(0, ConfigureAction(machine="board", settings=expected(episode))).ok
    assert normal.act(1, FinishAction()).victory_code
    assert normal.status().turn == 2
    episode.public.initial_state.machines["board"].settings = expected(episode)
    assert not qualify_episode(episode).passed
    with pytest.raises(ValueError, match="invalid initial causal apparatus"):
        PrivateEpisode.model_validate_json(episode.model_dump_json())


def test_original_certificate_is_readable_but_new_qualification_has_explicit_scope():
    from nexus.ontology.causal.evidence import files

    episode = generate_causal(17)
    theory = json.loads(episode.public.evidence_files["theory.json"])
    assert theory["evidence_version"] == 2
    assert "before the first eligible submission" in theory["profile"]
    assert "before the first eligible submission" in Session(episode).evidence("theory.json")
    episode.public.evidence_files = files(episode.public.investigation.data(), version=1)
    proof = dict(episode.generation_metadata.investigation_certificate)
    assert proof.pop("certificate_version") == 2
    proof["construction_required_for_guarantee"] = proof.pop("untreated_readings_insufficient_for_identification")
    proof["construction_scope"] = "untreated readings cannot guarantee identification; not a per-truth or optimality claim"
    episode.generation_metadata.investigation_certificate = proof
    restored = PrivateEpisode.model_validate_json(episode.model_dump_json())
    result = qualify_episode(restored)
    assert result.passed
    assert result.metrics["certificate_version"] == 2
    assert "construction_required_for_guarantee" not in result.metrics
    proof["certificate_version"] = 999
    episode.generation_metadata.investigation_certificate = proof
    assert not qualify_episode(episode).passed


@pytest.mark.slow
def test_untreated_policy_can_win_every_law_with_rejection_feedback():
    """Independent arithmetic, public action replies and no selected-law access."""
    from collections import defaultdict
    from functools import cache
    from itertools import count

    from nexus.generator.randomness import rng_for
    from nexus.models.actions import MoveAction

    boards = [tuple(oracle(w, e, sensor=False) for e in MISSION) for w in WORLDS]
    queries = (Experiment(instrument="reference"), *(Experiment(point=p) for p in POINTS))
    readings = [[oracle(w, query) for w in WORLDS] for query in queries]

    @cache
    def choose(group):
        candidates = tuple(sorted({boards[i] for i in group}))
        best = (2 * len(candidates), None, candidates)
        partitions = []
        for index, row in enumerate(readings):
            buckets = defaultdict(list)
            for i in group:
                buckets[row[i]].append(i)
            if len(buckets) == 1:
                continue
            parts = {v: tuple(g) for v, g in buckets.items()}
            rank = (max(len({boards[i] for i in g}) for g in parts.values()),
                    sum(len(g) ** 2 for g in parts.values()), index)
            partitions.append((rank, index, parts))
        for _, index, parts in sorted(partitions)[:2]:
            cost = 3 + max(choose(g)[0] for g in parts.values())
            if cost < best[0]:
                best = (cost, index, parts)
        return best

    def play(send, planning):
        reply = send(TakeAction(artifact="stock"))
        sample = next(e["details"]["artifact"] for e in reply.events if e["type"] == "take")
        if planning:
            send(MoveAction(target="lab"))
        group = tuple(range(len(WORLDS)))
        while True:
            _, index, options = choose(group)
            if index is None:
                for board in options:
                    send(ConfigureAction(machine="board", settings=board))
                    if send(FinishAction()).victory_code:
                        return
                raise AssertionError("No candidate board won")
            query = queries[index]
            send(ConfigureAction(machine="stage", settings=query.point))
            send(OperateAction(machine="stage", artifact=sample))
            reply = send(ProbeAction(machine=query.instrument, artifact=sample))
            value = next(e["details"]["result"]["payload"]["reading"]
                         for e in reply.events if "result" in e["details"])
            group = options[value]

    seeds = {}
    for seed in count():
        seeds.setdefault(rng_for(seed, FAMILY, "mechanism").randrange(len(WORLDS)), seed)
        if len(seeds) == len(WORLDS):
            break
    for planning in (0, 1):
        costs = []
        for seed in seeds.values():
            episode = generate_causal(seed, planning_level=planning, resource_pressure=2)
            session = Session(episode)

            def send(action):
                assert getattr(action, "machine", None) != "pulse"
                reply = session.act(session.status().turn, action, player_only=True)
                assert reply.ok
                return reply

            play(send, planning)
            assert session.status().status == "won"
            costs.append(session.status().turn)
        assert len(costs) == 648 and max(costs) == 28 + planning


def test_off_witness_measurement_and_failed_joint_target_exclusion():
    spec = Investigation(theory=3, discovery=5, mission_room="lab", stock_room="lab")
    experiment = Experiment(history=((2, 2, 2), (2, 0, 1)), point=(2, 2, 0))
    assert experiment not in WITNESS_EXPERIMENTS and experiment not in MISSION
    for value in range(3):
        belief = CausalBelief(spec)
        belief.observe(
            Measurement(
                "sensor",
                {"history": experiment.history, "point": experiment.point, "reading": value},
            )
        )
        admitted = {i for i, w in enumerate(WORLDS) if oracle(w, experiment) == value}
        assert belief.mask == sum(1 << i for i in admitted)
        rejected = targets()[0]
        belief.exclude_target(rejected)
        assert belief.mask == sum(1 << i for i in admitted if targets()[i] != rejected)


def test_history_is_immutable_under_preview_reconfiguration_and_drop_take():
    episode = generate_causal(7, planning_level=0, resource_pressure=0)
    session = Session(episode)
    a, b = take(session), take(session)
    prepare(session, a, Experiment(history=((1, 2, 0),), point=(2, 1, 1)))
    old = session.state.artifacts[a].model_copy(deep=True)
    preview = act(session, ProbeAction(machine="pulse", artifact=a))
    assert preview.events[0]["details"]["result"]["payload"]["history"] == [[1, 2, 0], [2, 1, 1]]
    assert session.state.artifacts[a] == old
    assert session.state.artifacts[b].data().history == ()
    act(session, ConfigureAction(machine="stage", settings=(0, 0, 2)))
    act(session, DropAction(artifact=a))
    act(session, TakeAction(artifact=a))
    assert session.state.artifacts[a] == old
    act(session, OperateAction(machine="pulse", artifact=a))
    before = canonical_hash(session.state)
    for kind in (ProbeAction, OperateAction):
        result = session.act(session.status().turn, kind(machine="pulse", artifact=a))
        assert not result.ok and canonical_hash(session.state) == before
    assert not episode.public.initial_state.artifacts
    assert Session(episode).state.artifacts == {}


def test_mission_sensor_exclusion_cannot_be_bypassed_by_operate_or_preview():
    session = Session(generate_causal(7, planning_level=0, resource_pressure=0))
    a = take(session)
    prepare(session, a, MISSION[0])
    for kind in (ProbeAction, OperateAction):
        before = canonical_hash(session.state)
        assert not session.act(session.status().turn, kind(machine="sensor", artifact=a)).ok
        assert canonical_hash(session.state) == before
    assert act(session, ProbeAction(machine="reference", artifact=a)).ok
    assert not session.act(session.status().turn, ProbeAction(machine="board", artifact=a)).ok


def test_http_boundary_privacy_terminal_metrics_and_duplicate_idempotence():
    episode = generate_causal(
        7, planning_level=0, resource_pressure=0, verifier_secret="PRIVATE_SENTINEL"
    )
    client = TestClient(create_single_session_app(episode))
    outputs = [client.get("/manifest").json(), client.get("/observe").json()]
    request = {"expected_turn": 0, "action": {"type": "take", "artifact": "stock"}}
    first = client.post("/action", json=request).json()
    duplicate = client.post("/action", json=request).json()
    assert duplicate == first | {"duplicate": True}
    assert "performance" not in first and "victory_code" not in first
    outputs += [first, client.get("/events").json()]
    text = json.dumps(outputs)
    for private in (
        "PRIVATE_SENTINEL",
        "construction_seed",
        "investigation_truth",
        'initial"',
        "reference_action_bound",
    ):
        assert private not in text
    payload = first["observation"]["carried_artifacts"][0]["payload"]
    assert set(payload) == {"history", "point", "reading", "instrument"}
    assert client.post("/finalize").json()["performance"]["duplicate_requests"] == 1


def test_wrong_finish_is_joint_evidence_and_diagnostics_remain_terminal_only():
    session = Session(generate_causal(7, planning_level=0, resource_pressure=0))
    correct = expected(session.episode)
    wrong = ((correct[0] + 1) % 3, *correct[1:])
    act(session, ConfigureAction(machine="board", settings=wrong))
    failed = act(session, FinishAction())
    assert failed.victory_code is None and failed.performance is None
    act(session, ConfigureAction(machine="board", settings=correct))
    result = act(session, FinishAction())
    assert result.victory_code and result.performance.failed_finishes == 1
    assert result.performance.measurements_used == 0
    assert result.performance.target_classes_before_first_submission == 113


def test_payload_contract_and_evidence_tampering_rejected():
    episode = generate_causal(7)
    for update in ({"hidden_mode": 1}, {"point": [True, 0, 0]}, {"history": [[0, 0, 0]] * 3}):
        with pytest.raises(ValidationError):
            DomainArtifact(ontology=FAMILY, id="a", location="lab", payload=update)
    for discovery, theory in ((4, 3), (5, 2), (1, 0), (3, 2)):
        with pytest.raises(ValueError):
            generate_causal(7, discovery_level=discovery, theory_level=theory)
    for part in ("truth", "evidence"):
        data = episode.model_dump(mode="json")
        if part == "truth":
            data["investigation_truth"]["payload"]["initial"] = 9
        else:
            data["public"]["evidence_files"]["theory.json"] = "{}"
        with pytest.raises(ValidationError):
            PrivateEpisode.model_validate(data)


def test_persistence_and_cli_action_contract(tmp_path):
    episode = generate_causal(7)
    save_episode(episode, tmp_path)
    assert load_private(tmp_path / "private.json") == episode
    runner = CliRunner()
    result = runner.invoke(app, ["actions", "--axis-version", "2", "--science-family", FAMILY])
    assert result.exit_code == 0, result.output
    assert "board" in result.output and "six" in result.output


def test_metadata_resource_and_mutated_evidence_fail_closed():
    for field, value in (
        ("theory_level", 0),
        ("discovery_level", 0),
        ("planning_level", 0),
        ("resource_pressure", 0),
    ):
        episode = generate_causal(7)
        setattr(episode.generation_metadata, field, value)
        assert not qualify_episode(episode).passed
    episode = generate_causal(7)
    episode.public.evidence_files["theory.json"] = "{}"
    assert not qualify_episode(episode).passed


def test_preparation_hashes_do_not_encode_low_entropy_private_mode():
    base = generate_causal(7, planning_level=0, resource_pressure=0)
    hashes = []
    for initial in range(3):
        episode = base.model_copy(deep=True)
        episode.investigation_truth.payload["initial"] = initial
        session = Session(PrivateEpisode.model_validate_json(episode.model_dump_json()))
        specimen = take(session)
        prepare(session, specimen, Experiment(history=((1, 2, 0), (2, 0, 1)), point=(1, 1, 2)))
        hashes.append(canonical_hash(session.state))
    assert len(set(hashes)) == 1


def test_serve_session_uses_new_family_environment(monkeypatch):
    import uvicorn

    captured = {}
    monkeypatch.setattr(uvicorn, "run", lambda app, **kwargs: captured.update(app=app))
    result = CliRunner().invoke(
        app,
        ["serve-session"],
        env={
            "NEXUS_SEED": "7",
            "NEXUS_AXIS_VERSION": "2",
            "NEXUS_SCIENCE_FAMILY": FAMILY,
            "NEXUS_THEORY_LEVEL": "3",
            "NEXUS_DISCOVERY_LEVEL": "5",
            "NEXUS_PLANNING_LEVEL": "1",
            "NEXUS_RESOURCE_PRESSURE": "1",
        },
    )
    assert result.exit_code == 0, result.output
    manifest = TestClient(captured["app"]).get("/manifest").json()
    assert "family" not in manifest["action_contract"]["apparatus"]
    assert "stage" in manifest["action_contract"]["apparatus"]["configuration"]


@pytest.mark.parametrize("field,bad", [
    ("scenario_family_id", "unrelated-world"), ("room_count", 3), ("machine_count", 4),
    ("guaranteed_policy_action_count", 1), ("required_probe_count", 99),
    ("estimated_reference_actions", 1), ("optimal_action_count", 17), ("action_budget", 1),
    ("recommended_tool_call_limit", 2), ("viable_causal_hypotheses", 1),
])
def test_causal_import_and_qualification_reject_contradictory_metrics(tmp_path, field, bad):
    episode = generate_causal(17, planning_level=0, resource_pressure=2)
    assert getattr(episode.generation_metadata, field) != bad
    setattr(episode.generation_metadata, field, bad)
    path = tmp_path / "private.json"
    path.write_text(episode.model_dump_json())
    with pytest.raises(ValidationError, match=field):
        load_private(path)
    report = qualify_episode(episode)
    assert not report.passed and field in " ".join(report.errors)
    cli = CliRunner().invoke(app, ["qualify", str(path)])
    assert cli.exit_code == 2
    assert json.loads(cli.output)["checks"] == {"compiled_contract": False}
    assert field in cli.output and episode.verifier_secret not in cli.output
