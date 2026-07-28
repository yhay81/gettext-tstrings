"""Safe, low-overhead runtime rendering for translated t-strings.

How the hot path is shaped:

- Allocate nothing per call. A template's static structure is looked up
  directly in a dict keyed by its ``template.strings`` tuple, so no
  metadata tuple is built and no lru_cache key is hashed per call. On a
  hit, each interpolation's expression, conversion, and format spec is
  compared against the recorded values, so a different call site that
  shares the same strings but differs in formatting cannot collide.
- A validated translation pattern (RenderPlan) is kept on its plan in a
  dict keyed by the pattern string. Later renders reach it in one
  dict.get.
- An unvalidated pattern always goes through parse_pattern and
  require_fields. There is no path that skips validation for speed.
"""

from __future__ import annotations

import gettext as _gettext
import logging
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from functools import lru_cache
from string.templatelib import Interpolation, Template, convert
from typing import Any, Literal, Protocol, runtime_checkable

from ._patterns import escape_literal, parse_pattern, require_fields, validate_name
from .errors import InvalidTemplateError, InvalidTranslationError

type Conversion = Literal["a", "r", "s"] | None
type FieldMetadata = tuple[str, Conversion, str]

_LOGGER = logging.getLogger("gettext_tstrings")

# Cache limits. Passing one clears that dimension outright — coarse, but the
# cheapest check and the simplest to reason about. _PLANS is two levels,
# strings then leading expression then sites, and every level is bounded.
_MAX_PLANS = 2048
_MAX_SHAPES_PER_KEY = 512
_MAX_SITES_PER_SHAPE = 8
_MAX_PATTERNS_PER_PLAN = 128


@runtime_checkable
class Translations(Protocol):
    """The standard gettext translation methods used by this package."""

    def gettext(self, message: str, /) -> str: ...

    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...

    def pgettext(self, context: str, message: str, /) -> str: ...

    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...


# The translations a call without an explicit argument uses. A web framework
# binds this per request; being context-scoped, that is safe under
# concurrency. Unbound, calls fall back to the process-global gettext
# catalog.
_current: ContextVar[Translations | None] = ContextVar(
    "gettext_tstrings_translations",
    default=None,
)
_current_get = _current.get

# Bind the standard library functions at import: the function objects are
# stable and resolve the current text domain internally, so behavior is
# unaffected.
_std_gettext = _gettext.gettext
_std_ngettext = _gettext.ngettext
_std_pgettext = _gettext.pgettext
_std_npgettext = _gettext.npgettext


def get_translations() -> Translations | None:
    """Return the translations bound to the current context, if any."""
    return _current_get()


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


class _Field:
    """How one placeholder renders. ``plain`` marks the str-concatenation path."""

    __slots__ = (
        "conversion",
        "format_spec",
        "index",
        "name",
        "plain",
        "plural_value_index",
        "template_index",
        "value_index",
    )

    name: str
    conversion: Conversion
    format_spec: str
    value_index: int
    plural_value_index: int | None
    template_index: int
    index: int
    plain: bool

    def __init__(
        self,
        name: str,
        conversion: Conversion,
        format_spec: str,
        value_index: int,
        template_index: int,
        index: int,
        plural_value_index: int | None = None,
    ) -> None:
        self.name = name
        self.conversion = conversion
        self.format_spec = format_spec
        self.value_index = value_index
        self.plural_value_index = plural_value_index
        self.template_index = template_index
        self.index = index
        self.plain = conversion is None and not format_spec


class _RenderPlan:
    """The render plan for one validated pattern.

    Zero occurrences (a constant), one, and two distinct fields are
    specialized into concatenation chains; anything else renders through
    the general loop over chunks.
    """

    __slots__ = (
        "chunks",
        "constant",
        "first",
        "middle",
        "nfields",
        "prefix",
        "repeats",
        "second",
        "single",
        "suffix",
    )

    constant: str | None
    single: _Field | None
    first: _Field | None
    second: _Field | None
    prefix: str
    middle: str
    suffix: str
    chunks: tuple[tuple[str, _Field | None], ...]
    repeats: bool
    nfields: int

    def __init__(
        self,
        chunks: tuple[tuple[str, _Field | None], ...],
        repeats: bool,
        nfields: int,
    ) -> None:
        self.chunks = chunks
        self.repeats = repeats
        self.nfields = nfields
        self.constant = None
        self.single = None
        self.first = None
        self.second = None
        self.prefix = ""
        self.middle = ""
        self.suffix = ""


class _TemplatePlan:
    """The translation plan for one t-string structure.

    Plans are shared through the cache, so the same structure yields the same
    object and identity is enough for equality and hashing.
    """

    __slots__ = ("allowed", "fields", "invalid", "msgid", "names", "patterns", "required")

    msgid: str
    fields: tuple[_Field, ...]
    names: tuple[str, ...]
    allowed: frozenset[str]
    required: frozenset[str]
    patterns: dict[str, _RenderPlan]
    invalid: set[str]

    def __init__(self, msgid: str, fields: tuple[_Field, ...]) -> None:
        self.msgid = msgid
        self.fields = fields
        self.names = tuple(field.name for field in fields)
        self.allowed = frozenset(self.names)
        self.required = self.allowed
        self.patterns = {}
        self.invalid = set()


class _PluralPlan:
    """A plan merging the singular and plural branches.

    ``required`` is the intersection of the two branches' placeholders.
    """

    __slots__ = ("allowed", "fields", "invalid", "names", "patterns", "required")

    fields: tuple[_Field, ...]
    names: tuple[str, ...]
    allowed: frozenset[str]
    required: frozenset[str]
    patterns: dict[str, _RenderPlan]
    invalid: set[str]

    def __init__(
        self,
        fields: tuple[_Field, ...],
        required: frozenset[str],
    ) -> None:
        self.fields = fields
        self.names = tuple(field.name for field in fields)
        self.allowed = frozenset(self.names)
        self.required = required
        self.patterns = {}
        self.invalid = set()


class _Site:
    """One call site under a shared strings key, with the metadata to match it."""

    __slots__ = ("conversions", "expressions", "plan", "specs")

    expressions: tuple[str, ...]
    conversions: tuple[Conversion, ...]
    specs: tuple[str, ...]
    plan: _TemplatePlan

    def __init__(self, metadata: tuple[FieldMetadata, ...], plan: _TemplatePlan) -> None:
        self.expressions = tuple(item[0] for item in metadata)
        self.conversions = tuple(item[1] for item in metadata)
        self.specs = tuple(item[2] for item in metadata)
        self.plan = plan


# strings maps to a single _Site (the common case) or, once two sites collide,
# to {leading expression: sites}. An ordinary message with distinctive literal
# text stays a single _Site; only bare-placeholder shapes (t"{name}" against
# t"{count}") pay for the dict.
_PLANS: dict[tuple[str, ...], _Site | dict[str, list[_Site]]] = {}


@lru_cache(maxsize=_MAX_PLANS)
def _compile_plan(
    strings: tuple[str, ...],
    metadata: tuple[FieldMetadata, ...],
) -> _TemplatePlan:
    pieces: list[str] = []
    fields: list[_Field] = []
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
                _Field(
                    name,
                    conversion,
                    format_spec,
                    index,
                    0,
                    len(fields),
                ),
            )
        pieces.append(f"{{{name}}}")

    return _TemplatePlan("".join(pieces), tuple(fields))


def _site_matches(site: _Site, interpolations: tuple[Interpolation[Any], ...]) -> bool:
    """Match a site's recorded metadata against each interpolation.

    This is what keeps two sites that share strings but differ in formatting
    (``t"{x:.2f}"`` against ``t"{x:.3f}"``) from being confused. It cannot be
    skipped.
    """
    expressions = site.expressions
    conversions = site.conversions
    specs = site.specs
    index = 0
    # enumerate() builds a tuple per iteration and measured +57ns per field, so
    # the hottest paths index by hand.
    for interp in interpolations:
        if (
            interp.expression != expressions[index]
            or interp.conversion != conversions[index]
            or interp.format_spec != specs[index]
        ):
            return False
        index += 1  # noqa: SIM113  # enumerate() measured +57ns per field
    return True


def _plan_for(
    strings: tuple[str, ...], interpolations: tuple[Interpolation[Any], ...]
) -> _TemplatePlan:
    """Look a plan up from the template's static structure.

    The common case — distinctive literal text, so a single site — returns
    after one comparison. Only shapes whose strings collide (bare
    placeholders like ``t"{name}"`` against ``t"{count}"``, or a nested
    format spec that varies at runtime) get promoted to a bounded dict keyed
    by the leading expression.
    """
    entry = _PLANS.get(strings)
    if entry is not None:
        if type(entry) is _Site:
            # A single site, the common case: run the comparison inline, once.
            expressions = entry.expressions
            conversions = entry.conversions
            specs = entry.specs
            index = 0
            for interp in interpolations:
                if (
                    interp.expression != expressions[index]
                    or interp.conversion != conversions[index]
                    or interp.format_spec != specs[index]
                ):
                    break
                index += 1  # noqa: SIM113  # enumerate() measured +57ns per field
            else:
                return entry.plan
        else:
            assert type(entry) is dict
            head = interpolations[0].expression if interpolations else ""
            sites = entry.get(head)
            if sites is not None:
                for site in sites:
                    if _site_matches(site, interpolations):
                        return site.plan

    metadata = tuple(
        (interp.expression, interp.conversion, interp.format_spec) for interp in interpolations
    )
    plan = _compile_plan(strings, metadata)
    site = _Site(metadata, plan)
    # Bound every dimension explicitly. A shape whose format spec varies at
    # runtime (a nested spec such as t"{x:{width}}") can produce a new site
    # each call, so reaching a limit clears it and falls back to recompiling.
    # The result is correct either way.
    head = interpolations[0].expression if interpolations else ""
    if entry is None:
        if len(_PLANS) >= _MAX_PLANS:
            _PLANS.clear()
        _PLANS[strings] = site
    elif type(entry) is _Site:
        # A collision: promote the single site into a dict keyed by the
        # leading expression.
        old_head = entry.expressions[0] if entry.expressions else ""
        shapes: dict[str, list[_Site]] = {old_head: [entry]}
        shapes.setdefault(head, []).append(site)
        _PLANS[strings] = shapes
    else:
        assert type(entry) is dict
        sites = entry.get(head)
        if sites is None:
            if len(entry) >= _MAX_SHAPES_PER_KEY:
                entry.clear()
            entry[head] = [site]
        else:
            if len(sites) >= _MAX_SITES_PER_SHAPE:
                sites.clear()
            sites.append(site)
    return plan


def _compile_pattern(plan: _TemplatePlan | _PluralPlan, pattern: str) -> _RenderPlan:
    """Validate a translation pattern, turn it into a render plan, and cache it."""
    parsed = parse_pattern(pattern)
    require_fields(required=plan.required, allowed=plan.allowed, actual=parsed.fields)

    by_name = {field.name: field for field in plan.fields}
    chunks = tuple(
        (literal, by_name[name] if name is not None else None) for literal, name in parsed.chunks
    )

    # Collect the text between fields, then specialize on how many fields occur.
    segments = [""]
    field_sequence: list[_Field] = []
    for literal, field in chunks:
        segments[-1] += literal
        if field is not None:
            field_sequence.append(field)
            segments.append("")
    occurrences = len(field_sequence)

    render_plan = _RenderPlan(chunks, occurrences > len(parsed.fields), len(plan.fields))
    if occurrences == 0:
        render_plan.constant = segments[0]
    elif occurrences == 1:
        render_plan.single = field_sequence[0]
        render_plan.prefix = segments[0]
        render_plan.suffix = segments[1]
    elif occurrences == 2 and field_sequence[0] is not field_sequence[1]:
        # Two distinct fields only. A repeated field is left to the general
        # loop, whose memo is what keeps "formatted at most once" true.
        render_plan.first = field_sequence[0]
        render_plan.second = field_sequence[1]
        render_plan.prefix = segments[0]
        render_plan.middle = segments[1]
        render_plan.suffix = segments[2]

    patterns = plan.patterns
    if len(patterns) >= _MAX_PATTERNS_PER_PLAN:
        patterns.clear()
    patterns[pattern] = render_plan
    return render_plan


def _format_value(value: Any, conversion: Conversion, format_spec: str) -> str:
    if conversion is not None:
        value = convert(value, conversion)
    return format(value, format_spec)


def _render_chunks(render_plan: _RenderPlan, values: tuple[Any, ...]) -> str:
    """The general multi-field render. Each field's value is formatted once."""
    rendered: list[str] = []
    formatted: list[str | None] | None = (
        [None] * render_plan.nfields if render_plan.repeats else None
    )
    for literal, field in render_plan.chunks:
        rendered.append(literal)
        if field is not None:
            value = formatted[field.index] if formatted is not None else None
            if value is None:
                raw = values[field.value_index]
                if field.plain and type(raw) is str:
                    value = raw
                else:
                    value = _format_value(raw, field.conversion, field.format_spec)
                if formatted is not None:
                    formatted[field.index] = value
            rendered.append(value)
    return "".join(rendered)


def _render_with_values(
    render_plan: _RenderPlan,
    values: tuple[Any, ...],
) -> str:
    """The shared render tail that reads a values tuple.

    Used by CompiledTemplate and by the source-text fallback. Only for plans
    from a single template: a render plan from a _PluralPlan has to pick its
    values by field.template_index, and the single/pair paths here never look
    at it, so passing one breaks silently.
    """
    constant = render_plan.constant
    if constant is not None:
        return constant
    field = render_plan.single
    if field is not None:
        value = values[field.value_index]
        if field.plain and type(value) is str:
            return render_plan.prefix + value + render_plan.suffix
        return (
            render_plan.prefix
            + _format_value(value, field.conversion, field.format_spec)
            + render_plan.suffix
        )
    first = render_plan.first
    if first is not None:
        second = render_plan.second
        assert second is not None
        left_raw = values[first.value_index]
        if first.plain and type(left_raw) is str:
            left = left_raw
        else:
            left = _format_value(left_raw, first.conversion, first.format_spec)
        right_raw = values[second.value_index]
        if second.plain and type(right_raw) is str:
            right = right_raw
        else:
            right = _format_value(right_raw, second.conversion, second.format_spec)
        return render_plan.prefix + left + render_plan.middle + right + render_plan.suffix
    return _render_chunks(render_plan, values)


def _source_render_plan(plan: _TemplatePlan) -> _RenderPlan:
    """The render plan for the source msgid, which cannot fail validation."""
    render_plan = plan.patterns.get(plan.msgid)
    if render_plan is None:
        render_plan = _compile_pattern(plan, plan.msgid)
    return render_plan


def _remember_invalid(plan: _TemplatePlan | _PluralPlan, pattern: str) -> None:
    """Record a pattern that failed validation.

    Kept apart from the valid ones so a ``strict=True`` call still revalidates
    and raises. Without the record, one broken catalog entry revalidates and
    warns on every single render.
    """
    invalid = plan.invalid
    if len(invalid) >= _MAX_PATTERNS_PER_PLAN:
        invalid.clear()
    invalid.add(pattern)


class CompiledTemplate:
    """A cached gettext message plan bound to one t-string's runtime values."""

    # A plain class: a frozen dataclass initializes through object.__setattr__,
    # which is measurably slower to construct.
    __slots__ = ("_plan", "_values")

    _plan: _TemplatePlan
    _values: tuple[Any, ...]

    def __init__(self, plan: _TemplatePlan, values: tuple[Any, ...]) -> None:
        self._plan = plan
        self._values = values

    def __repr__(self) -> str:
        return f"CompiledTemplate(msgid={self._plan.msgid!r})"

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
        plan = self._plan
        render_plan = plan.patterns.get(pattern)
        if render_plan is None:
            render_plan = _compile_pattern(plan, pattern)
        return _render_with_values(render_plan, self._values)


def _bind_template(template: Template) -> _TemplatePlan:
    if type(template) is not Template:
        raise TypeError(f"expected string.templatelib.Template, got {type(template).__name__}")
    return _plan_for(template.strings, template.interpolations)


def compile_template(template: Template, /) -> CompiledTemplate:
    """Compile a Python t-string, reusing its cached static plan."""
    plan = _bind_template(template)
    return CompiledTemplate(plan, template.values)


def _render_pattern(render_plan: _RenderPlan, template: Template) -> str:
    """Render a validated RenderPlan with a template's interpolated values.

    gettext() inlines this same logic on purpose: it is the one path where
    saving a single function call measures. Any change here must be mirrored
    in that copy; tests/test_render_parity.py pins the two together.
    """
    constant = render_plan.constant
    if constant is not None:
        return constant
    interpolations = template.interpolations
    field = render_plan.single
    if field is not None:
        value = interpolations[field.value_index].value
        if field.plain and type(value) is str:
            return render_plan.prefix + value + render_plan.suffix
        return (
            render_plan.prefix
            + _format_value(value, field.conversion, field.format_spec)
            + render_plan.suffix
        )
    first = render_plan.first
    if first is not None:
        second = render_plan.second
        assert second is not None
        left_raw = interpolations[first.value_index].value
        if first.plain and type(left_raw) is str:
            left = left_raw
        else:
            left = _format_value(left_raw, first.conversion, first.format_spec)
        right_raw = interpolations[second.value_index].value
        if second.plain and type(right_raw) is str:
            right = right_raw
        else:
            right = _format_value(right_raw, second.conversion, second.format_spec)
        return render_plan.prefix + left + render_plan.middle + right + render_plan.suffix
    return _render_chunks(render_plan, template.values)


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
    if type(template) is not Template:
        raise TypeError(f"expected string.templatelib.Template, got {type(template).__name__}")
    interpolations = template.interpolations
    plan = _plan_for(template.strings, interpolations)
    msgid = plan.msgid
    if not msgid:
        return ""

    if translations is None:
        translations = _current_get()
    pattern = translations.gettext(msgid) if translations is not None else _std_gettext(msgid)

    render_plan = plan.patterns.get(pattern)
    if render_plan is None:
        if not strict and pattern in plan.invalid:
            render_plan = _source_render_plan(plan)
        else:
            try:
                render_plan = _compile_pattern(plan, pattern)
            except InvalidTranslationError as exc:
                if strict:
                    raise
                _LOGGER.warning(
                    "invalid translation for msgid %r; using source text: %s",
                    msgid,
                    exc,
                )
                _remember_invalid(plan, pattern)
                render_plan = _source_render_plan(plan)

    # What follows is _render_pattern inlined — duplicated deliberately. Keep
    # it in sync with that function.
    constant = render_plan.constant
    if constant is not None:
        return constant
    field = render_plan.single
    if field is not None:
        value = interpolations[field.value_index].value
        if field.plain and type(value) is str:
            return render_plan.prefix + value + render_plan.suffix
        return (
            render_plan.prefix
            + _format_value(value, field.conversion, field.format_spec)
            + render_plan.suffix
        )
    first = render_plan.first
    if first is not None:
        second = render_plan.second
        assert second is not None
        left_raw = interpolations[first.value_index].value
        if first.plain and type(left_raw) is str:
            left = left_raw
        else:
            left = _format_value(left_raw, first.conversion, first.format_spec)
        right_raw = interpolations[second.value_index].value
        if second.plain and type(right_raw) is str:
            right = right_raw
        else:
            right = _format_value(right_raw, second.conversion, second.format_spec)
        return render_plan.prefix + left + render_plan.middle + right + render_plan.suffix
    return _render_chunks(render_plan, template.values)


def pgettext(
    context: str,
    template: Template,
    /,
    *,
    translations: Translations | None = None,
    strict: bool = False,
) -> str:
    """Translate and render one contextual t-string."""
    if type(template) is not Template:
        raise TypeError(f"expected string.templatelib.Template, got {type(template).__name__}")
    interpolations = template.interpolations
    plan = _plan_for(template.strings, interpolations)
    msgid = plan.msgid
    if not msgid:
        return ""

    if translations is None:
        translations = _current_get()
    pattern = (
        translations.pgettext(context, msgid)
        if translations is not None
        else _std_pgettext(context, msgid)
    )

    render_plan = plan.patterns.get(pattern)
    if render_plan is None:
        if not strict and pattern in plan.invalid:
            render_plan = _source_render_plan(plan)
        else:
            try:
                render_plan = _compile_pattern(plan, pattern)
            except InvalidTranslationError as exc:
                if strict:
                    raise
                _LOGGER.warning(
                    "invalid translation for context %r msgid %r; using source text: %s",
                    context,
                    msgid,
                    exc,
                )
                _remember_invalid(plan, pattern)
                render_plan = _source_render_plan(plan)

    return _render_pattern(render_plan, template)


@lru_cache(maxsize=_MAX_PLANS)
def _merge_plural_plans(singular: _TemplatePlan, plural: _TemplatePlan) -> _PluralPlan:
    """Merge the fields of both plural branches.

    Plans are already interned by the structural cache, so the lru_cache key
    resolves on object identity.
    """
    fields: list[_Field] = [
        _Field(
            field.name,
            field.conversion,
            field.format_spec,
            field.value_index,
            0,
            index,
        )
        for index, field in enumerate(singular.fields)
    ]
    field_indices = {field.name: index for index, field in enumerate(fields)}

    for field in plural.fields:
        previous_index = field_indices.get(field.name)
        if previous_index is None:
            field_indices[field.name] = len(fields)
            fields.append(
                _Field(
                    field.name,
                    field.conversion,
                    field.format_spec,
                    field.value_index,
                    1,
                    len(fields),
                ),
            )
            continue

        previous = fields[previous_index]
        if previous.conversion != field.conversion or previous.format_spec != field.format_spec:
            raise InvalidTemplateError(
                f"plural source placeholder {field.name!r} uses different formatting",
            )
        previous.plural_value_index = field.value_index

    plural_names = frozenset(plural.names)
    required = frozenset(name for name in singular.names if name in plural_names)
    return _PluralPlan(tuple(fields), required)


def _render_plural_chunks(
    render_plan: _RenderPlan,
    values: tuple[tuple[Any, ...], tuple[Any, ...]],
    use_plural_values: bool,
) -> str:
    rendered: list[str] = []
    formatted: list[str | None] | None = (
        [None] * render_plan.nfields if render_plan.repeats else None
    )
    for literal, field in render_plan.chunks:
        rendered.append(literal)
        if field is not None:
            value = formatted[field.index] if formatted is not None else None
            if value is None:
                if use_plural_values and field.plural_value_index is not None:
                    raw = values[1][field.plural_value_index]
                else:
                    raw = values[field.template_index][field.value_index]
                if field.plain and type(raw) is str:
                    value = raw
                else:
                    value = _format_value(raw, field.conversion, field.format_spec)
                if formatted is not None:
                    formatted[field.index] = value
            rendered.append(value)
    return "".join(rendered)


def _render_plural_pattern(
    render_plan: _RenderPlan,
    singular_template: Template,
    plural_template: Template,
    n: int,
) -> str:
    constant = render_plan.constant
    if constant is not None:
        return constant
    field = render_plan.single
    if field is not None:
        if n != 1 and field.plural_value_index is not None:
            value = plural_template.interpolations[field.plural_value_index].value
        else:
            source = singular_template if field.template_index == 0 else plural_template
            value = source.interpolations[field.value_index].value
        if field.plain and type(value) is str:
            return render_plan.prefix + value + render_plan.suffix
        return (
            render_plan.prefix
            + _format_value(value, field.conversion, field.format_spec)
            + render_plan.suffix
        )
    return _render_plural_chunks(
        render_plan,
        (singular_template.values, plural_template.values),
        n != 1,
    )


def _render_plural_source(
    singular_plan: _TemplatePlan,
    singular_template: Template,
    plural_plan: _TemplatePlan,
    plural_template: Template,
    n: int,
) -> str:
    """Pick a branch by the source language's rule and render the source."""
    if n == 1:
        return _render_with_values(
            _source_render_plan(singular_plan),
            singular_template.values,
        )
    return _render_with_values(
        _source_render_plan(plural_plan),
        plural_template.values,
    )


def _ngettext_impl(
    context: str | None,
    singular: Template,
    plural: Template,
    n: int,
    translations: Translations | None,
    strict: bool,
) -> str:
    """The body shared by ngettext and npgettext; only the context differs."""
    singular_plan = _bind_template(singular)
    plural_plan = _bind_template(plural)
    # An empty msgid is reserved for the catalog's metadata (SPEC §2). If either
    # branch is empty no translation entry can exist, so render the source.
    if not singular_plan.msgid or not plural_plan.msgid:
        return _render_plural_source(singular_plan, singular, plural_plan, plural, n)
    merged = _merge_plural_plans(singular_plan, plural_plan)

    if translations is None:
        translations = _current_get()
    if context is None:
        pattern = (
            translations.ngettext(singular_plan.msgid, plural_plan.msgid, n)
            if translations is not None
            else _std_ngettext(singular_plan.msgid, plural_plan.msgid, n)
        )
    else:
        pattern = (
            translations.npgettext(context, singular_plan.msgid, plural_plan.msgid, n)
            if translations is not None
            else _std_npgettext(context, singular_plan.msgid, plural_plan.msgid, n)
        )

    render_plan = merged.patterns.get(pattern)
    if render_plan is None:
        if not strict and pattern in merged.invalid:
            return _render_plural_source(singular_plan, singular, plural_plan, plural, n)
        try:
            render_plan = _compile_pattern(merged, pattern)
        except InvalidTranslationError as exc:
            if strict:
                raise
            if context is None:
                _LOGGER.warning(
                    "invalid plural translation for msgid %r; using source text: %s",
                    singular_plan.msgid,
                    exc,
                )
            else:
                _LOGGER.warning(
                    "invalid plural translation for context %r msgid %r; using source text: %s",
                    context,
                    singular_plan.msgid,
                    exc,
                )
            _remember_invalid(merged, pattern)
            return _render_plural_source(singular_plan, singular, plural_plan, plural, n)
    return _render_plural_pattern(render_plan, singular, plural, n)


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
    return _ngettext_impl(None, singular, plural, n, translations, strict)


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
    return _ngettext_impl(context, singular, plural, n, translations, strict)


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
        return gettext(template, translations=self.translations, strict=self.strict)

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
