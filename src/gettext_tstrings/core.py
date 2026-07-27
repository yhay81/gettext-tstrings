"""Safe, low-overhead runtime rendering for translated t-strings."""

from __future__ import annotations

import gettext as _gettext
import logging
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from functools import lru_cache
from string.templatelib import Template, convert
from typing import Any, Literal, Protocol, runtime_checkable

from ._patterns import escape_literal, parse_pattern, require_fields, validate_name
from .errors import InvalidTemplateError, InvalidTranslationError

type Conversion = Literal["a", "r", "s"] | None
type FieldMetadata = tuple[str, Conversion, str]

_LOGGER = logging.getLogger("gettext_tstrings")

# The translations to use when a call omits an explicit ``translations`` object.
# Web frameworks bind this per request (per-context, concurrency-safe); when
# unset the module functions fall back to the process-global gettext catalog.
_current: ContextVar[Translations | None] = ContextVar(
    "gettext_tstrings_translations",
    default=None,
)


def get_translations() -> Translations | None:
    """Return the translations bound to the current context, if any."""
    return _current.get()


def set_translations(translations: Translations | None) -> None:
    """Bind translations to the current context (e.g. at the start of a request)."""
    _current.set(translations)


@contextmanager
def use_translations(translations: Translations | None) -> Iterator[None]:
    """Bind translations for the duration of a ``with`` block, then restore."""
    token = _current.set(translations)
    try:
        yield
    finally:
        _current.reset(token)


def _active(translations: Translations | None) -> Translations | None:
    """Resolve the effective translations: explicit argument, else the context."""
    return translations if translations is not None else _current.get()


@runtime_checkable
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


def _render_source(plan: _TemplatePlan, values: tuple[Any, ...]) -> str:
    """Render the source msgid structure (used for empty msgids and fallback)."""
    return _render_template(plan, values, plan.msgid)


def gettext(
    template: Template,
    /,
    *,
    translations: Translations | None = None,
    strict: bool = False,
) -> str:
    """Translate and render one t-string.

    An empty msgid is reserved by gettext for catalog metadata, so ``t""``
    renders as ``""`` without a catalog lookup. When a translation's
    placeholders do not match the source, a lenient render (the default) falls
    back to the source text; ``strict=True`` re-raises ``InvalidTranslationError``.
    """
    plan, values = _bind_template(template)
    if not plan.msgid:
        return _render_source(plan, values)
    active = _active(translations)
    pattern = active.gettext(plan.msgid) if active is not None else _gettext.gettext(plan.msgid)
    try:
        return _render_template(plan, values, pattern)
    except InvalidTranslationError:
        if strict:
            raise
        _LOGGER.warning("invalid translation for msgid %r; using source text", plan.msgid)
        return _render_source(plan, values)


def pgettext(
    context: str,
    template: Template,
    /,
    *,
    translations: Translations | None = None,
    strict: bool = False,
) -> str:
    """Translate and render one contextual t-string."""
    plan, values = _bind_template(template)
    if not plan.msgid:
        return _render_source(plan, values)
    active = _active(translations)
    pattern = (
        active.pgettext(context, plan.msgid)
        if active is not None
        else _gettext.pgettext(context, plan.msgid)
    )
    try:
        return _render_template(plan, values, pattern)
    except InvalidTranslationError:
        if strict:
            raise
        _LOGGER.warning(
            "invalid translation for context %r msgid %r; using source text",
            context,
            plan.msgid,
        )
        return _render_source(plan, values)


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


def _render_plural_source(
    singular_plan: _TemplatePlan,
    singular_values: tuple[Any, ...],
    plural_plan: _TemplatePlan,
    plural_values: tuple[Any, ...],
    n: int,
) -> str:
    """Render the source plural branch selected by the source language rule."""
    if n == 1:
        return _render_template(singular_plan, singular_values, singular_plan.msgid)
    return _render_template(plural_plan, plural_values, plural_plan.msgid)


def ngettext(
    singular: Template,
    plural: Template,
    n: int,
    /,
    *,
    translations: Translations | None = None,
    strict: bool = False,
) -> str:
    """Translate and render singular/plural t-strings."""
    singular_plan, singular_values = _bind_template(singular)
    plural_plan, plural_values = _bind_template(plural)
    active = _active(translations)
    pattern = (
        active.ngettext(singular_plan.msgid, plural_plan.msgid, n)
        if active is not None
        else _gettext.ngettext(singular_plan.msgid, plural_plan.msgid, n)
    )
    try:
        return _render_plural(
            singular_plan,
            singular_values,
            plural_plan,
            plural_values,
            pattern,
        )
    except InvalidTranslationError:
        if strict:
            raise
        _LOGGER.warning(
            "invalid plural translation for msgid %r; using source text",
            singular_plan.msgid,
        )
        return _render_plural_source(singular_plan, singular_values, plural_plan, plural_values, n)


def npgettext(
    context: str,
    singular: Template,
    plural: Template,
    n: int,
    /,
    *,
    translations: Translations | None = None,
    strict: bool = False,
) -> str:
    """Translate and render contextual singular/plural t-strings."""
    singular_plan, singular_values = _bind_template(singular)
    plural_plan, plural_values = _bind_template(plural)
    active = _active(translations)
    pattern = (
        active.npgettext(
            context,
            singular_plan.msgid,
            plural_plan.msgid,
            n,
        )
        if active is not None
        else _gettext.npgettext(
            context,
            singular_plan.msgid,
            plural_plan.msgid,
            n,
        )
    )
    try:
        return _render_plural(
            singular_plan,
            singular_values,
            plural_plan,
            plural_values,
            pattern,
        )
    except InvalidTranslationError:
        if strict:
            raise
        _LOGGER.warning(
            "invalid plural translation for context %r msgid %r; using source text",
            context,
            singular_plan.msgid,
        )
        return _render_plural_source(singular_plan, singular_values, plural_plan, plural_values, n)


# Concise aliases retained for applications that prefer them.
tr = gettext
ntr = ngettext


@dataclass(frozen=True, slots=True)
class Translator:
    """Bind a gettext translation object to a t-string processor.

    ``strict`` selects the response to a catalog whose placeholders do not match
    the source. The default (``False``) reproduces the source text so a broken
    translation never crashes a render, mirroring gettext's never-fail contract;
    ``strict=True`` re-raises ``InvalidTranslationError`` and suits tests and CI.
    """

    translations: Translations
    strict: bool = False

    def __call__(self, template: Template, /) -> str:
        return self.gettext(template)

    def gettext(self, template: Template, /) -> str:
        return gettext(template, translations=self.translations, strict=self.strict)

    def ngettext(self, singular: Template, plural: Template, n: int, /) -> str:
        return ngettext(singular, plural, n, translations=self.translations, strict=self.strict)

    def pgettext(self, context: str, template: Template, /) -> str:
        return pgettext(context, template, translations=self.translations, strict=self.strict)

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
            strict=self.strict,
        )

    tr = gettext
    ntr = ngettext
