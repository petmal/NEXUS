"""Typed, public-only device help. Examples describe single actions, never experiments."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

from nexus.models.actions import Action, ConfigureAction, ProbeAction
from nexus.presentation.laboratory import REPAIR, REVISION


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Settings(Record):
    description: str
    order: tuple[str, ...]
    parameters: dict[str, str]
    value_schema: dict = Field(alias="schema")


class Operation(Record):
    effect: str
    returns: str
    action_cost: int = 1


class Example(Record):
    requires: str
    action: Action
    effect: str


class Device(Record):
    description: str
    settings: Settings | None
    targets: str
    actions: dict[Literal["configure", "probe", "operate"], Operation]
    # One independent action, no measured result or multi-step tutorial field.
    examples: tuple[Example] = Field(min_length=1, max_length=1)


def settings(annotation, description, parameters):
    return Settings(description=description, order=tuple(parameters), parameters=parameters,
                    schema=TypeAdapter(annotation).json_schema())


def configuration(effect):
    return Operation(effect=effect + " Artifacts are unchanged.", returns="Confirmation of the stored machine settings.")


def configure_example(machine, values, effect):
    return (Example(requires=f"Be in the room containing {machine}. These values illustrate syntax only.",
                    action=ConfigureAction(machine=machine, settings=values), effect=effect),)


def catalog(family):
    """No episode, seed, world state, measurements, solver or selected truth is accepted."""
    if family == REPAIR:
        from nexus.ontology.compositional.schema import Dose, Settings as Preparation

        return {
            "stage": Device(
                description="Prepares a reusable survey specimen with your chosen laboratory inputs and treatment settings.",
                settings=settings(Preparation, "Eight integers in the listed parameter order.", {
                    "context": "Selects operating context 0 or 1, not the facility phase.",
                    "x": "First excitation input.", "y": "Second excitation input.", "z": "Third excitation input.",
                    "a": "Added after f.", "b": "Added after g.",
                    "c": "Added to the final response in both contexts.",
                    "d": "Added to the final response in context 1 only; does not disable its function replacement.",
                }),
                targets="Probe/operate require a carried survey in array. The seal cannot be prepared here. Configure needs no artifact.",
                actions={
                    "configure": configuration("Stores the preparation on stage."),
                    "probe": Operation(effect="Previews preparation without applying it. No measurement is taken.", returns="The proposed preparation; the survey is unchanged."),
                    "operate": Operation(effect="Applies the preparation to the survey and clears its stored reading. No measurement is taken.", returns="The prepared survey state."),
                },
                examples=configure_example("stage", (0,) * 8, "Stores eight zero settings on stage. No survey changes and no response is measured."),
            ),
            "sensor": Device(
                description="Measures the response of an already prepared survey specimen.",
                settings=None,
                targets="Carry a survey specimen in array. The seal has no sensor reading.",
                actions={
                    "probe": Operation(effect="Measures the survey's actual preparation without storing the reading or changing the survey.", returns="One response in {0,1,2}, with the measured preparation."),
                    "operate": Operation(effect="Measures the same preparation and stores the reading on the survey.", returns="One response in {0,1,2}, with the measured preparation."),
                },
                examples=(Example(requires="Carry a prepared survey in array; replace <survey-id> with its actual ID.",
                                  action=ProbeAction(machine="sensor", artifact="<survey-id>"),
                                  effect="Returns a response for that preparation. The survey and its stored reading remain unchanged. No example response value is supplied."),),
            ),
            "doser": Device(
                description="Applies your chosen four-setting treatment to the portable seal.",
                settings=settings(Dose, "Four integers in order a,b,c,d.", {
                    "a": "Added after f.", "b": "Added after g.", "c": "Output offset in both contexts.",
                    "d": "Additional output offset in context 1.",
                }),
                targets="Probe/operate require carried seal in array. Surveys do not accept this treatment. Configure needs no artifact.",
                actions={
                    "configure": configuration("Stores the treatment on doser."),
                    "probe": Operation(effect="Previews the treatment without applying or validating it.", returns="The proposed treatment; seal is unchanged."),
                    "operate": Operation(effect="Applies or replaces the seal's treatment. It does not check the exit conditions.", returns="The seal with its applied treatment."),
                },
                examples=configure_example("doser", (0, 1, 2, 0), "Stores a=0,b=1,c=2,d=0 on doser. The seal is unchanged; no exit check is performed."),
            ),
        }
    if family == REVISION:
        from nexus.ontology.revision.schema import Program, Reading

        return {
            "reader": Device(
                description="Runs a mode sequence on the facility's reference device and reports its final display.",
                settings=settings(Reading.model_fields["query"].rebuild_annotation(),
                                  "A sequence of 1 to 8 mode numbers, in execution order; no length prefix.",
                                  {"mode": "Each entry is 0 or 1. Repeated entries are allowed."}),
                targets="Probe/operate require carried carrier or a survey copy in workshop. The artifact identifies where an operated reading is stored; it is not the device being tested. Configure needs no artifact.",
                actions={
                    "configure": configuration("Stores the mode sequence on reader. No measurement is taken."),
                    "probe": Operation(effect="Runs the selected sequence on a reference fixture starting at the stated initial inventory. The carried artifact is unchanged.", returns="One final q0 % 3 display in {0,1,2}; no intermediate inventories or readings."),
                    "operate": Operation(effect="Makes the same reference measurement and stores its sequence and reading on the artifact. Its installed cartridge is unchanged and is not tested.", returns="One final q0 % 3 display in {0,1,2}, stored with the sequence."),
                },
                examples=(Example(requires="Carry carrier in workshop. Reader is already configured with the sequence you want to measure.",
                                  action=ProbeAction(machine="reader", artifact="carrier"),
                                  effect="Returns the reference's final display for the configured sequence, starting afresh. Carrier is unchanged. No example display value is supplied."),),
            ),
            "assembler": Device(
                description="Builds and installs a routing cartridge using your four selected links.",
                settings=settings(Program, "Four link indices in the listed parameter order; indices 0..11 refer to the public link table.", {
                    "mode0_first_link": "First transfer when mode 0 runs.",
                    "mode0_second_link": "Second transfer when mode 0 runs, using the inventory left by the first.",
                    "mode1_first_link": "First transfer when mode 1 runs.",
                    "mode1_second_link": "Second transfer when mode 1 runs, using the inventory left by the first.",
                }),
                targets="Probe/operate require a carried artifact in workshop. Only the actual carrier can satisfy the exit requirement; survey copies cannot replace it. Configure needs no artifact.",
                actions={
                    "configure": configuration("Stores four link indices on assembler."),
                    "probe": Operation(effect="Previews installation without changing the artifact or testing the proposed cartridge.", returns="The proposed four link indices."),
                    "operate": Operation(effect="Installs or replaces the cartridge and clears the artifact's stored reading. It does not test the cartridge.", returns="The artifact with its installed cartridge."),
                },
                examples=configure_example("assembler", (0, 1, 2, 3), "Stores links 0,1 for mode 0 and links 2,3 for mode 1 on assembler. No cartridge is installed or checked."),
            ),
        }
    return {}


def public_catalog(family):
    return {name: device.model_dump(mode="json", by_alias=True) for name, device in catalog(family).items()}
