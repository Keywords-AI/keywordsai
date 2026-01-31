from typing import Dict, List, Union, Literal
from typing_extensions import TypedDict
from .mixin_types.filter_mixin import (
    BaseFilterMixinTypedDict,
    MetricFilterParamPydantic,
    FilterBundlePydantic,
    FilterParamDictPydantic,
)


# TypedDict versions (existing/legacy)
class MetricFilterParam(BaseFilterMixinTypedDict, total=False):
    """
    Represents a filter parameter for a specific metric.

    Attributes:
        operator: The comparison operator (e.g., 'gt', 'contains', 'in')
        operator_function: The function to apply to the operator
        operator_args: Arguments for the operator function
        connector: How this filter connects with others ('AND' or 'OR')
        value: The value(s) to filter by - can be a single value or a list
    """

    operator_function: Literal["mapContainsKey"]
    operator_args: List[str]


# This is legacy filter_bundle
class FilterBundle(TypedDict, total=False):
    """
    Represents a bundle of filter parameters that can be applied together.

    Attributes:
        connector: How the bundle is connected to the previous conditions('AND' or 'OR')
        filter_params: The filter parameters in this bundle
    """

    connector: Literal["AND", "OR"]  # AND is "all" and OR is "any"
    filter_params: "FilterParamDict"  # This is a recursive type


# The final type that allows both metric parameters and filter_bundles
FilterParamDict = Dict[
    str, Union[MetricFilterParam, List[MetricFilterParam], FilterBundle]
]


# Pydantic versions (new/preferred for validation)
# These are imported from filter_mixin and aliased here for convenience
MetricFilterParamModel = MetricFilterParamPydantic
FilterBundleModel = FilterBundlePydantic
FilterParamDictModel = FilterParamDictPydantic


# Export both versions
__all__ = [
    # TypedDict versions (backward compatibility)
    "MetricFilterParam",
    "FilterBundle",
    "FilterParamDict",
    # Pydantic versions (preferred for validation)
    "MetricFilterParamModel",
    "FilterBundleModel",
    "FilterParamDictModel",
    # Re-exports from mixin
    "MetricFilterParamPydantic",
    "FilterBundlePydantic",
    "FilterParamDictPydantic",
]
