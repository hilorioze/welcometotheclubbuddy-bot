from typing import Any

from pydantic import BaseModel
from pydantic.fields import FieldInfo

ALLOWED_MODEL_KWARGS_FOR_PROPAGATION = {
    "_case_sensitive",
    "_env_file",
    "_env_file_encoding",
    "_env_ignore_empty",
    "_env_parse_none_str",
    "_secrets_dir",
}


def get_sub_models_for_model_fields(
    model_fields: dict[str, FieldInfo],
) -> dict[str, type[BaseModel]]:
    return {
        field_name: field_info.annotation
        for field_name, field_info in model_fields.items()
        if isinstance(field_info.annotation, type) and issubclass(field_info.annotation, BaseModel)
    }


def propagate_model_kwargs_to_sub_models(
    self: BaseModel,
    *,
    init_kwargs: dict[str, Any],
    allowed_kwargs_to_propagate: set[str] | None = None,
):
    # Use predefined set of allowed kwargs if not provided
    if allowed_kwargs_to_propagate is None:
        allowed_kwargs_to_propagate = ALLOWED_MODEL_KWARGS_FOR_PROPAGATION

    # Filter out kwargs that are not in the allowed set
    sub_model_init_kwargs = {
        key: value for key, value in init_kwargs.items() if key in allowed_kwargs_to_propagate
    }

    # If no relevant kwargs to propagate, return early
    if not sub_model_init_kwargs:
        return

    # Get sub-models associated with model fields
    sub_models = get_sub_models_for_model_fields(self.__fields__)

    # Iterate over sub-models and update init_kwargs with propagated kwargs
    for field_name, sub_model_class in sub_models.items():
        if field_name in init_kwargs:
            model_kwarg = init_kwargs[field_name]

            # Check if the existing kwarg is a sub-model instance
            if issubclass(model_kwarg.__class__, sub_model_class):
                # Update sub-model kwargs and reassign to init_kwargs
                init_kwargs[field_name] = sub_model_class(
                    **dict(model_kwarg),
                    **sub_model_init_kwargs,
                )
                continue

        # Create new sub-model instance with propagated kwargs
        init_kwargs[field_name] = sub_model_class(**sub_model_init_kwargs)
