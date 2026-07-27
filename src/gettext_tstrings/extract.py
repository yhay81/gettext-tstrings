"""Message extraction plugin for Python t-string translation calls."""

from __future__ import annotations

import ast
import heapq
import io
import tokenize
import warnings
from collections.abc import Collection, Iterator, Mapping
from typing import Any, cast

from babel.messages.extract import extract_python

from ._patterns import MARKER_COMMENT, escape_literal

Extracted = tuple[int, str | None, str | tuple[str, ...], list[str]]

# Truthy strings accepted for boolean extraction options.
_TRUE = frozenset({"1", "true", "yes", "on"})


class ExtractionError(ValueError):
    """A translation call cannot be extracted safely."""


def _option_names(options: Mapping[str, Any], key: str, default: str) -> set[str]:
    value = str(options.get(key, default))
    return {item.strip() for item in value.replace(",", " ").split() if item.strip()}


def _option_bool(options: Mapping[str, Any], key: str, default: bool) -> bool:
    value = options.get(key, default)
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in _TRUE


def _decode_source(data: bytes | str) -> tuple[str, bytes]:
    if isinstance(data, str):
        return data, data.encode()
    encoding, _ = tokenize.detect_encoding(io.BytesIO(data).readline)
    return data.decode(encoding), data


def _call_name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return None


def _matches(name: str | None, configured: set[str]) -> bool:
    if name is None:
        return False
    return name in configured or name.rsplit(".", 1)[-1] in configured


def _fail(filename: str, node: ast.AST, message: str) -> ExtractionError:
    return ExtractionError(f"{filename}:{getattr(node, 'lineno', 0)}: {message}")


def _template_pattern(
    node: ast.expr,
    *,
    filename: str,
) -> tuple[str, dict[str, tuple[int, str]]]:
    if not isinstance(node, ast.TemplateStr):
        raise _fail(filename, node, "translation argument must be a t-string literal")

    pieces: list[str] = []
    formatting: dict[str, tuple[int, str]] = {}

    for value in node.values:
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            pieces.append(escape_literal(value.value))
            continue
        if not isinstance(value, ast.Interpolation) or not isinstance(value.value, ast.Name):
            raise _fail(
                filename,
                value,
                "t-string interpolations must be simple variable names",
            )

        name = value.value.id
        signature = (
            value.conversion,
            (
                ast.dump(value.format_spec, include_attributes=False)
                if value.format_spec is not None
                else ""
            ),
        )
        if name in formatting and formatting[name] != signature:
            raise _fail(
                filename,
                value,
                f"placeholder {name!r} is repeated with different formatting",
            )
        formatting[name] = signature
        pieces.append(f"{{{name}}}")

    return "".join(pieces), formatting


def _translator_comments(
    lines: list[str],
    lineno: int,
    comment_tags: Collection[str],
) -> list[str]:
    preceding: list[str] = []
    index = lineno - 2
    while index >= 0:
        stripped = lines[index].strip()
        if not stripped.startswith("#"):
            break
        preceding.append(stripped[1:].strip())
        index -= 1
    preceding.reverse()

    if not preceding or not any(preceding[0].startswith(tag) for tag in comment_tags):
        return []
    return preceding


def _context(node: ast.expr, *, filename: str) -> str:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    raise _fail(filename, node, "message context must be a string literal")


def _require_compatible_plural_formatting(
    singular: dict[str, tuple[int, str]],
    plural: dict[str, tuple[int, str]],
    *,
    filename: str,
    node: ast.AST,
) -> None:
    for name in singular.keys() & plural.keys():
        if singular[name] != plural[name]:
            raise _fail(
                filename,
                node,
                f"plural source placeholder {name!r} uses different formatting",
            )


def _plural_messages(
    singular_node: ast.expr,
    plural_node: ast.expr,
    *,
    filename: str,
    node: ast.AST,
) -> tuple[str, str]:
    singular, singular_fields = _template_pattern(singular_node, filename=filename)
    plural, plural_fields = _template_pattern(plural_node, filename=filename)
    _require_compatible_plural_formatting(
        singular_fields,
        plural_fields,
        filename=filename,
        node=node,
    )
    return singular, plural


def _extract_call(
    call: ast.Call,
    *,
    filename: str,
    tr_functions: set[str],
    ntr_functions: set[str],
    gettext_functions: set[str],
    ngettext_functions: set[str],
    pgettext_functions: set[str],
    npgettext_functions: set[str],
) -> tuple[str | None, str | tuple[str, ...]] | None:
    """Build ``(funcname, messages)`` for one recognized t-string call.

    Simple messages use a ``None`` funcname so extraction never depends on the
    caller's keyword set; plural and contextual messages keep their canonical
    gettext funcname because Babel needs that keyword's argument spec.
    """
    name = _call_name(call.func)

    if _matches(name, tr_functions):
        if not call.args:
            raise _fail(filename, call, "tr() requires a t-string argument")
        message, _ = _template_pattern(call.args[0], filename=filename)
        return None, message
    if (
        _matches(name, gettext_functions)
        and call.args
        and isinstance(call.args[0], ast.TemplateStr)
    ):
        message, _ = _template_pattern(call.args[0], filename=filename)
        return None, message
    if _matches(name, ntr_functions):
        if len(call.args) < 3:
            raise _fail(filename, call, "ntr() requires singular, plural, and count arguments")
        return "ngettext", _plural_messages(
            call.args[0], call.args[1], filename=filename, node=call
        )
    if (
        _matches(name, ngettext_functions)
        and len(call.args) >= 2
        and isinstance(call.args[0], ast.TemplateStr)
    ):
        if len(call.args) < 3:
            raise _fail(filename, call, "ngettext() requires singular, plural, and count arguments")
        return "ngettext", _plural_messages(
            call.args[0], call.args[1], filename=filename, node=call
        )
    if (
        _matches(name, pgettext_functions)
        and len(call.args) >= 2
        and isinstance(call.args[1], ast.TemplateStr)
    ):
        context = _context(call.args[0], filename=filename)
        message, _ = _template_pattern(call.args[1], filename=filename)
        return "pgettext", (context, message)
    if (
        _matches(name, npgettext_functions)
        and len(call.args) >= 3
        and isinstance(call.args[1], ast.TemplateStr)
    ):
        if len(call.args) < 4:
            raise _fail(
                filename,
                call,
                "npgettext() requires context, singular, plural, and count arguments",
            )
        context = _context(call.args[0], filename=filename)
        singular, plural = _plural_messages(
            call.args[1], call.args[2], filename=filename, node=call
        )
        return "npgettext", (context, singular, plural)
    return None


def _extract_tstring_calls(
    source: str,
    *,
    filename: str,
    keywords: Collection[str],
    comment_tags: Collection[str],
    options: Mapping[str, Any],
) -> Iterator[Extracted]:
    strict = _option_bool(options, "strict", False)
    available = frozenset(keywords)
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as exc:
        # A single unparsable file must not abort extraction of the whole project.
        warnings.warn(f"{filename}: skipped unparsable source ({exc.msg})", stacklevel=2)
        return

    lines = source.splitlines()
    function_sets = {
        "tr_functions": _option_names(options, "tr_functions", "tr"),
        "ntr_functions": _option_names(options, "ntr_functions", "ntr"),
        "gettext_functions": _option_names(options, "gettext_functions", "gettext _ lazy_gettext"),
        "ngettext_functions": _option_names(options, "ngettext_functions", "ngettext"),
        "pgettext_functions": _option_names(
            options, "pgettext_functions", "pgettext lazy_pgettext"
        ),
        "npgettext_functions": _option_names(options, "npgettext_functions", "npgettext"),
    }

    calls = (node for node in ast.walk(tree) if isinstance(node, ast.Call))
    for call in sorted(calls, key=lambda node: (node.lineno, node.col_offset)):
        try:
            extracted = _extract_call(call, filename=filename, **function_sets)
        except ExtractionError as exc:
            # One rejected call warns and is skipped; opt into strict to fail hard.
            if strict:
                raise
            warnings.warn(str(exc), stacklevel=2)
            continue
        if extracted is None:
            continue

        funcname, messages = extracted
        if funcname is not None and funcname not in available:
            warnings.warn(
                f"{filename}:{call.lineno}: skipped {funcname!r} t-string because keyword "
                f"{funcname!r} is not in the extraction keyword set; keep the standard gettext "
                "keywords to extract plural and contextual messages",
                stacklevel=2,
            )
            continue

        comments = _translator_comments(lines, call.lineno, comment_tags)
        comments.append(MARKER_COMMENT)
        yield call.lineno, funcname, messages, comments


def extract_tstrings(
    fileobj: Any,
    keywords: Collection[str],
    comment_tags: Collection[str],
    options: Mapping[str, Any],
) -> Iterator[Extracted]:
    """Extract ordinary Python gettext calls and t-string tr()/ntr() calls."""
    data = fileobj.read()
    source, raw = _decode_source(data)
    filename = getattr(fileobj, "name", None) or "(unknown)"

    standard_messages = extract_python(
        io.BytesIO(raw),
        cast("Any", keywords),
        comment_tags,
        cast("Any", options),
    )
    tstring_messages = _extract_tstring_calls(
        source,
        filename=filename,
        keywords=keywords,
        comment_tags=comment_tags,
        options=options,
    )
    yield from heapq.merge(
        cast("Iterator[Extracted]", standard_messages),
        tstring_messages,
        key=lambda item: item[0],
    )
