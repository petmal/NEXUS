"""Complete scientific observation audits, separate from reference-policy costs."""

from dataclasses import asdict
from functools import lru_cache

from nexus.ontology.dynamics import laws
from nexus.solver.observation_audit import ObservationAudit, labels


@lru_cache(maxsize=1)
def dynamics_audit() -> ObservationAudit:
    return ObservationAudit(
        labels(laws.targets()),
        tuple(bytes(laws.reading(w, e) for w in laws.WORLDS) for e in laws.experiments()),
    )


@lru_cache(maxsize=4)
def history_groups(maximum: int) -> tuple[int, ...]:
    selected = tuple(
        j
        for j, e in enumerate(laws.experiments())
        if e.instrument == "reference" or len(e.history) <= maximum
    )
    return dynamics_audit().all_data_groups(selected)


@lru_cache(maxsize=1)
def population():
    audit = dynamics_audit()
    result = audit.population_summary()
    result["history_restrictions"] = {
        str(n): {
            "observation_classes": len(history_groups(n)),
            "ambiguous_worlds": sum(
                g.bit_count() for g in history_groups(n) if audit.target_count(g) > 1
            ),
            "best_correct_mass": audit.best_guess_mass(history_groups(n)),
        }
        for n in range(3)
    }
    result["complete_scope"] = (
        "all bit points and sensor histories0..3, excluding eight declared mission protocols; two reference signatures cover every reference history/point; insensitive and free responses carry no additional scientific information"
    )
    result["limited_reading_win_upper_bounds"] = {
        "scope": "uniform FULL disclosed prior, T3/D5/P1/R1 with 73 actions; not the selected matrix; permits interleaved rejected finishes",
        "cost_argument": "take seal + move costs at least 2; each distinct applied dose and finish costs at least 3 (configure + operate + finish); at most floor((73-2)/3)=23 guesses; all measurement/preparation costs ignored as a relaxation",
        "channel_argument": "each scientific reading has at most three outcomes; finish has one absorbing success or one generic continuing failure; other responses reveal no hidden scientific state",
        "bounds": [
            audit.guess_success_upper(maximum_guesses=23, maximum_readings=k) for k in range(4)
        ],
    }
    return result


def inspect_dynamics(episode, *, max_seconds: float = 30):
    spec = episode.public.investigation.data()
    index = laws.WORLDS.index(laws.World(**episode.investigation_truth.payload))
    if spec.resolved is not None:
        return {
            "band": "execution-control",
            "certificate": {"lower_bound": 0, "exact_minimum": 0},
            "world_index": index,
        }
    audit = dynamics_audit()
    bound = audit.certificate(index, max_seconds=max_seconds)
    target = laws.targets()[index]
    world = laws.WORLDS[index]
    return {
        "band": "structural-transfer-candidate"
        if bound.lower_bound >= 4
        else "below-challenge-gate",
        "certificate": asdict(bound),
        "world_index": index,
        "structure": {
            "wiring": world.wiring,
            "transition": world.transition,
            "response": world.response,
        },
        "untreated_target_classes": audit.target_count(
            next(g for g in history_groups(0) if g >> index & 1)
        ),
        "one_pulse_target_classes": audit.target_count(
            next(g for g in history_groups(1) if g >> index & 1)
        ),
        "order_sensitive": any(target[a] != target[b] for a, b in ((0, 1), (2, 3), (4, 5))),
        "target_distinct_values": len(set(target)),
        "scope": "minimum sufficient positive measurements under the FULL disclosed prior; not feedback rounds, probability of victory, or empirical difficulty; guesses and rejected finishes excluded",
    }


def inspect_repair(episode):
    from nexus.ontology.repair.laws import solution

    truth = episode.investigation_truth.data()
    dose = solution(truth.a, truth.b, truth.c, truth.degree)
    return {
        "band": "compact-adaptive-control",
        "law_degree": truth.degree,
        "universal_shortcut": "reference a; choose x=a to reveal b; choose y=b to reveal c,d; triangular substitution; r need never be identified",
        "zero_dose_terms": sum(v == 0 for v in dose),
        "selected_zero_coupling": truth.r == 0,
        "deep_admission": False,
    }
