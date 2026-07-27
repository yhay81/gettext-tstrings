"""Safe, cached runtime rendering for translated t-strings."""

from __future__ import annotations

import gettext as _gettext
from dataclasses import dataclass
from functools import lru_cache
from string.templatelib import Template, convert
from typing import Any, Literal, Protocol

from ._patterns import escape_literal, parse_pattern, require_fields, validate_name
from .errors import InvalidTemplateError, InvalidTranslationError

type Conversion = Literal["a", "r", "s"] | None
type FieldMetadata = tuple[str, Conversion, str]


class Translations(Protocol):
    """The standard gettext translation methods used by this package."""

    def gettext(self, message: str, /) -> str: ...

    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...

    def pgettext(self, context: str, message: str, /) -> str: ...

    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...


@dataclass(frozen=True, slots=True)
class _FieldPlan:
    name: str
    conversion: Conversion
    format_spec: str
    value_index: int


@dataclass(frozen=True, slots=True)
class _TemplatePlan:
    msgid: str
    fields: tuple[_FieldPlan, ...]
    names: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class _PluralFieldPlan:
    name: str
    conversion: Conversion
    format_spec: str
    template_index: int
    value_index: int


@dataclass(frozen=True, slots=True)
class _PluralPlan:
    fields: tuple[_PluralFieldPlan, ...]
    names: tuple[str, ...]
    required_names: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class _RenderPlan:
    chunks: tuple[tuple[str, int | None], ...]
    repeats_fields: bool
    constant: str | None
    single_field: tuple[str, int, str] | None


@lru_cache(maxsize=2048)
def _compile_plan(
    strings: tuple[str, ...],
    metadata: tuple[FieldMetadata, ...],
) -> _TemplatePlan:
    pieces: list[str] = []
    fields: list[_FieldPlan] = []
    field_indices: dict[str, int] = {}

    for index, literal in enumerate(strings):
        pieces.append(escape_literal(literal))
        if index >= len(metadata):
            continue

        expression, conversion, format_spec = metadata[index]
        try:
            name = validate_name(expression)
        except InvalidTranslationError as exc:
            raise InvalidTemplateError(
                f"t-string interpolations must be simple variable names; got {expression!r}",
            ) from exc

        previous_index = field_indices.get(name)
        if previous_index is not None:
            previous = fields[previous_index]
            if previous.conversion != conversion or previous.format_spec != format_spec:
                raise InvalidTemplateError(
                    f"placeholder {name!r} is repeated with different formatting",
                )
        else:
            field_indices[name] = len(fields)
            fields.append(
                _FieldPlan(
                    name=name,
                    conversion=conversion,
                    format_spec=format_spec,
                    value_index=index,
                ),
            )
        pieces.append(f"{{{name}}}")

    return _TemplatePlan(
        msgid="".join(pieces),
        fields=tuple(fields),
        names=tuple(field.name for field in fields),
    )


@lru_cache(maxsize=4096)
def _compile_render_plan(
    pattern: str,
    names: tuple[str, ...],
    required_names: tuple[str, ...],
) -> _RenderPlan:
    parsed = parse_pattern(pattern)
    allowed = frozenset(names)
    require_fields(
        required=frozenset(required_names),
        allowed=allowed,
        actual=parsed.fields,
    )
    field_indices = {name: index for index, name in enumerate(names)}
    chunks = tuple(
        (literal, field_indices[name] if name is not None else None)
        for literal, name in parsed.chunks
    )
    field_occurrences = sum(index is not None for _, index in chunks)
    constant = "".join(literal for literal, _ in chunks) if field_occurrences == 0 else None
    single_field: tuple[str, int, str] | None = None
    if field_occurrences == 1:
        field_position = next(
            position for position, (_, index) in enumerate(chunks) if index is not None
        )
        literal, field_index = chunks[field_position]
        assert field_index is not None
        single_field = (
            "".join(chunk_literal for chunk_literal, _ in chunks[:field_position]) + literal,
            field_index,
            "".join(chunk_literal for chunk_literal, _ in chunks[field_position + 1 :]),
        )
    return _RenderPlan(
        chunks=chunks,
        repeats_fields=field_occurrences > len(parsed.fields),
        constant=constant,
        single_field=single_field,
    )


def _format_value(value: Any, conversion: Conversion, format_spec: str) -> str:
    if conversion is not None:
        value = convert(value, conversion)
    return format(value, format_spec)


def _render_template(
    plan: _TemplatePlan,
    values: tuple[Any, ...],
    pattern: str,
    *,
    required_names: tuple[str, ...] | None = None,
) -> str:
    render_plan = _compile_render_plan(pattern, plan.names, required_names or plan.names)
    if render_plan.constant is not None:
        return render_plan.constant
    if render_plan.single_field is not None:
        prefix, single_index, suffix = render_plan.single_field
        field = plan.fields[single_index]
        return (
            prefix
            + _format_value(
                values[field.value_index],
                field.conversion,
                field.format_spec,
            )
            + suffix
        )

    rendered: list[str] = []
    formatted: list[str | None] | None = (
        [None] * len(plan.fields) if render_plan.repeats_fields else None
    )
    for literal, field_index in render_plan.chunks:
        rendered.append(literal)
        if field_index is not None:
            field = plan.fields[field_index]
            value = formatted[field_index] if formatted is not None else None
            if value is None:
                value = _format_value(
                    values[field.value_index],
                    field.conversion,
                    field.format_spec,
                )
                if formatted is not None:
                    formatted[field_index] = value
            rendered.append(value)
    return "".join(rendered)


@dataclass(frozen=True, slots=True)
class CompiledTemplate:
    """A cached gettext message plan bound to one t-string's runtime values."""

    _plan: _TemplatePlan
    _values: tuple[Any, ...]

    @property
    def msgid(self) -> str:
        """The stable gettext message identifier."""
        return self._plan.msgid

    @property
    def placeholders(self) -> tuple[str, ...]:
        """Placeholder names in first-occurrence order."""
        return self._plan.names

    def render(self, pattern: str) -> str:
        """Validate and render one translated brace pattern."""
        return _render_template(self._plan, self._values, pattern)


def _bind_template(template: Template) -> tuple[_TemplatePlan, tuple[Any, ...]]:
    if not isinstance(template, Template):
        raise TypeError(f"expected string.templatelib.Template, got {type(template).__name__}")

    interpolations = template.interpolations
    plan = _compile_plan(
        template.strings,
        tuple(
            (
                interpolation.expression,
                interpolation.conversion,
                interpolation.format_spec,
            )
            for interpolation in interpolations
        ),
    )
    return plan, template.values


def compile_template(template: Template, /) -> CompiledTemplate:
    """Compile a Python t-string, reusing its cached static plan."""
    plan, values = _bind_template(template)
    return CompiledTemplate(plan, values)


def gettext(template: Template, /, *, translations: Translations | None = None) -> str:
    """Translate and render one t-string."""
    plan, values = _bind_template(template)
    pattern = (
        translations.gettext(plan.msgid)
        if translations is not None
        else _gettext.gettext(plan.msgid)
    )
    return _render_template(plan, values, pattern)


def pgettext(
    context: str,
    template: Template,
    /,
    *,
    translations: Translations | None = None,
) -> str:
    """Translate and render one contextual t-string."""
    plan, values = _bind_template(template)
    pattern = (
        translations.pgettext(context, plan.msgid)
        if translations is not None
        else _gettext.pgettext(context, plan.msgid)
    )
    return _render_template(plan, values, pattern)


@lru_cache(maxsize=2048)
def _merge_plural_plans(singular: _TemplatePlan, plural: _TemplatePlan) -> _PluralPlan:
    fields: list[_PluralFieldPlan] = [
        _PluralFieldPlan(
            field.name,
            field.conversion,
            field.format_spec,
            0,
            field.value_index,
        )
        for field in singular.fields
    ]
    field_indices = {field.name: index for index, field in enumerate(fields)}

    for field in plural.fields:
        previous_index = field_indices.get(field.name)
        if previous_index is None:
            field_indices[field.name] = len(fields)
            fields.append(
                _PluralFieldPlan(
                    field.name,
                    field.conversion,
                    field.format_spec,
                    1,
                    field.value_index,
                ),
            )
            continue

        previous = fields[previous_index]
        if previous.conversion != field.conversion or previous.format_spec != field.format_spec:
            raise InvalidTemplateError(
                f"plural source placeholder {field.name!r} uses different formatting",
            )

    plural_names = frozenset(plural.names)
    return _PluralPlan(
        fields=tuple(fields),
        names=tuple(field.name for field in fields),
        required_names=tuple(name for name in singular.names if name in plural_names),
    )


def _render_plural(
    singular_plan: _TemplatePlan,
    singular_values: tuple[Any, ...],
    plural_plan: _TemplatePlan,
    plural_values: tuple[Any, ...],
    pattern: str,
) -> str:
    plan = _merge_plural_plans(singular_plan, plural_plan)
    render_plan = _compile_render_plan(pattern, plan.names, plan.required_names)
    if render_plan.constant is not None:
        return render_plan.constant

    values = (singular_values, plural_values)
    if render_plan.single_field is not None:
        prefix, single_index, suffix = render_plan.single_field
        field = plan.fields[single_index]
        return (
            prefix
            + _format_value(
                values[field.template_index][field.value_index],
                field.conversion,
                field.format_spec,
            )
            + suffix
        )

    rendered: list[str] = []
    formatted: list[str | None] | None = (
        [None] * len(plan.fields) if render_plan.repeats_fields else None
    )
    for literal, field_index in render_plan.chunks:
        rendered.append(literal)
        if field_index is not None:
            field = plan.fields[field_index]
            value = formatted[field_index] if formatted is not None else None
            if value is None:
                value = _format_value(
                    values[field.template_index][field.value_index],
                    field.conversion,
                    field.format_spec,
                )
                if formatted is not None:
                    formatted[field_index] = value
            rendered.append(value)
    return "".join(rendered)


def ngettext(
    singular: Template,
    plural: Template,
    n: int,
    /,
    *,
    translations: Translations | None = None,
) -> str:
    """Translate and render singular/plural t-strings."""
    singular_plan, singular_values = _bind_template(singular)
    plural_plan, plural_values = _bind_template(plural)
    pattern = (
        translations.ngettext(singular_plan.msgid, plural_plan.msgid, n)
        if translations is not None
        else _gettext.ngettext(singular_plan.msgid, plural_plan.msgid, n)
    )
    return _render_plural(
        singular_plan,
        singular_values,
        plural_plan,
        plural_values,
        pattern,
    )


def npgettext(
    context: str,
    singular: Template,
    plural: Template,
    n: int,
    /,
    *,
    translations: Translations | None = None,
) -> str:
    """Translate and render contextual singular/plural t-strings."""
    singular_plan, singular_values = _bind_template(singular)
    plural_plan, plural_values = _bind_template(plural)
    pattern = (
        translations.npgettext(
            context,
            singular_plan.msgid,
            plural_plan.msgid,
            n,
        )
        if translations is not None
        else _gettext.npgettext(
            context,
            singular_plan.msgid,
            plural_plan.msgid,
            n,
        )
    )
    return _render_plural(
        singular_plan,
        singular_values,
        plural_plan,
        plural_values,
        pattern,
    )


# Concise aliases retained for applications that prefer them.
tr = gettext
ntr = ngettext


@dataclass(frozen=True, slots=True)
class Translator:
    """Bind a gettext translation object to a t-string processor."""

    translations: Translations

    def __call__(self, template: Template, /) -> str:
        return self.gettext(template)

    def gettext(self, template: Template, /) -> str:
        return gettext(template, translations=self.translations)

    def ngettext(self, singular: Template, plural: Template, n: int, /) -> str:
        return ngettext(singular, plural, n, translations=self.translations)

    def pgettext(self, context: str, template: Template, /) -> str:
        return pgettext(context, template, translations=self.translations)

    def npgettext(
        self,
        context: str,
        singular: Template,
        plural: Template,
        n: int,
        /,
    ) -> str:
        return npgettext(
            context,
            singular,
            plural,
            n,
            translations=self.translations,
        )

    tr = gettext
    ntr = ngettext
