"""Declarative theory dependencies for research fixtures; not a runtime difficulty flag."""
from pydantic import BaseModel, ConfigDict, Field, model_validator


class TheoryStage(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: str = Field(min_length=1)
    theory_level: int = Field(ge=1, le=3)
    requires: tuple[str, ...] = ()
    description: str


class TheoryProgression(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    stages: tuple[TheoryStage, ...]
    prediction_stage: str

    @model_validator(mode="after")
    def validate_dependencies(self) -> "TheoryProgression":
        stages = {stage.id: stage for stage in self.stages}
        if len(stages) != len(self.stages) or self.prediction_stage not in stages:
            raise ValueError("progression requires unique stages and a declared prediction stage")
        visiting, visited = set(), set()
        def visit(name: str) -> None:
            if name not in stages or name in visiting:
                raise ValueError("progression has a missing prerequisite or a dependency cycle")
            if name in visited:
                return
            visiting.add(name)
            dependencies = stages[name].requires
            if len(set(dependencies)) != len(dependencies):
                raise ValueError("duplicate theory prerequisite")
            for parent in dependencies:
                visit(parent)
            visiting.remove(name)
            visited.add(name)
        for name in stages:
            visit(name)
        return self
