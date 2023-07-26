"""
Module for experiment configuration structures.

This module provides data structures to capture configurations required to run an
experiment.
"""

from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

from .common_structures import InputData
from .dataset_config import DatasetConfig
from .evaluator_config import (
    ComparisonEvaluatorConfig,
    EvaluatorConfig,
    EvaluatorOutput,
)
from .wrapper_configs import BaseWrapperConfig

# Registry for supported custom classes
CLASS_REGISTRY: Dict[str, Type] = {
    # "ClassA": ClassA
}


@dataclass
class WrapperVariation:
    """
    Represents a variation within a wrapper.
    The value can be any type, but typical usages might include strings, 
    numbers, configuration dictionaries, or even custom class configurations.
    """

    value_type: str  # e.g., "string", "int", "float", "ClassA", ...
    value: Any  # The actual value or parameters to initialize a value
    instantiated_value: Any = field(init=False)
    variation_id: Optional[str] = None

    def asdict(self):
        return asdict(self)

    def __post_init__(self):
        self.instantiated_value = self.instantiate()

    def instantiate(self) -> Any:
        """
        Returns an instantiated value based on value_type and params.
        """
        if self.value_type in ["str", "int", "float", "bool"]:
            return eval(self.value_type)(
                self.value
            )  # Use eval to convert string type to actual type
        elif self.value_type in CLASS_REGISTRY:
            return CLASS_REGISTRY[self.value_type](**self.value)
        else:
            raise ValueError(f"Unsupported value_type: {self.value_type}")


@dataclass
class WrapperConfig:
    """
    Configuration for each individual wrapper used in the experiment.

    Attributes:
    - name (str): Name of the wrapper.
    - variations (List[WrapperVariation]): Variations for this wrapper.
    """

    name: str
    variations: List[WrapperVariation]

    def asdict(self):
        return asdict(self)


@dataclass
class OutputConfig:
    """
    Configuration for experiment output.

    Attributes:
    - path (str): Path where the experiment output should be saved.
    - formatter (Callable): Function to format the output.
    """

    path: str
    formatter: Callable


@dataclass
class ComparisonOutput:
    """
    Result of a comparison evaluation.

    Attributes:
    - better_output (str): Name of the wrapper that produced the better output.
    - reason (str): Reason or metric based on which the decision was made.
    """

    better_output: str
    reason: str


@dataclass
class HumanRating:
    """
    Human rating for an output.

    Attributes:
    - aspect (str): Aspect being rated.
    - rating (float): Rating value.
    - scale (Tuple[float, float]): Minimum and maximum value of the rating scale.
    """

    aspect: str
    rating: float
    scale: Tuple[float, float] = (1.0, 5.0)  # Default scale from 1 to 5

    def asdict(self):
        return asdict(self)


@dataclass
class HumanRatingConfig:
    """
    Configuration for human rating.

    Attributes:
    - aspects (List[str]): List of aspects to rate.
    - scale (Tuple[float, float]): Minimum and maximum value of the rating scale.
    """

    aspects: List[str]
    scale: Tuple[float, float] = (1.0, 5.0)

    def asdict(self):
        return asdict(self)


@dataclass
class ExperimentResult:
    """
    Result for a single example based on a specific combination of active variations
    across wrappers.

    Attributes:
    - combination (Dict[str, str]): The combination of wrapper names and their active
      variation_ids for this example.
    - raw_output (str): Raw output for this example.
    - latency (float): Latency for producing the output for this example
      (in milliseconds or appropriate unit).
    - token_usage (int): Number of tokens used for this example.
    - evaluator_outputs (List[EvaluatorOutput]): Evaluator outputs for this example.
    - human_rating (Optional[HumanRating]): Human rating for this example.
    - intermediate_logs (List[str]): Logs captured during the experiment.
    """

    input_data: InputData
    combination: Dict[str, str]
    raw_output: str
    latency: float
    token_usage: int
    evaluator_outputs: List[EvaluatorOutput]
    human_rating: Optional[HumanRating] = None
    intermediate_logs: List[str] = field(default_factory=list)

    def asdict(self):
        return asdict(self)


@dataclass
class ExperimentConfig:
    """
    Configuration for running an experiment.

    Attributes:
    - description (str): Description of the experiment.
    - variations (List[WrapperConfig]): List of variations configurations.
    - dataset (DatasetConfig): Dataset configuration.
    - wrapper_configs (List[BaseWrapperConfig]): List of wrapper configurations.
    - combinations_to_run (Optional[List[Tuple[str, Any]]]): List of combinations to
      run.
      Each tuple represents a (group_name, variation) pair.
    - evaluators (Optional[List[Union[EvaluatorConfig, ComparisonEvaluatorConfig]]]):
      List of evaluator configurations.
    - output (Optional[OutputConfig]): Output configuration.

    - existing_experiment_path (Optional[str]): Path to an existing experiment for
      incremental experiments or comparisons.
    - version (Optional[str]): Version or timestamp for the experiment.
    - output_parser (Optional[str]): Class name of the std output parser to use.
    - metadata (Dict[str, Any]): Additional metadata related to the experiment.
    - variactions (Dict[str, List[Any]]): Variations for each wrapper.
    """

    # Required configurations
    description: str
    variations: List[WrapperConfig]
    dataset: DatasetConfig
    # Optional configurations with default values
    wrapper_configs: Optional[List[BaseWrapperConfig]] = None
    combinations_to_run: Optional[List[Tuple[str, Any]]] = None
    evaluators: Optional[List[Union[EvaluatorConfig,
                                    ComparisonEvaluatorConfig]]] = None
    output: Optional[OutputConfig] = None
    human_rating_configs: List[HumanRatingConfig] = field(default_factory=list)
    existing_experiment_path: Optional[str] = None
    version: Optional[str] = None
    output_parser: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Metric:
    """
    Represents a metric calculated from evaluator outputs.

    Attributes:
    - name (str): Name of the metric (e.g., "accuracy").
    - value (float): Calculated value of the metric.
    - description (Optional[str]): Description or details about the metric.
    """
    name: str
    value: float
    description: Optional[str] = None

    def asdict(self):
        return asdict(self)


@dataclass
class ExperimentSummary:
    """
    Represents the summary of an entire experiment.

    Attributes:
    - aggregated_metrics (Dict[str, Dict[str, Metric]]): 
      A dictionary where keys are evaluator names and values are dictionaries mapping metric names to their values.
    - ... (other summary attributes)
    """
    aggregated_metrics: Dict[str, Dict[str, Metric]]

    def asdict(self):
        return asdict(self)


@dataclass
class Experiment:
    """
    Represents an entire experiment.

    Attributes:
    - results (List[ExperimentResult]): List of results for each input example.
    - aggregated_metrics (Dict[str, Dict[str, Metric]]): 
      A dictionary where keys are evaluator names and values are dictionaries mapping metric names to their values.
    - ... (other experiment attributes)
    """
    results: List[ExperimentResult]
    aggregated_metrics: Dict[str, Dict[str, Metric]]

    def asdict(self):
        return asdict(self)
