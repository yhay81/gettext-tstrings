"""Message extraction plugin for Python t-string translation calls."""

from __future__ import annotations

import ast
import codecs
import heapq
import io
import tokenize
import warnings
from collections.abc import Collection, Iterator, Mapping
from typing import Any, TypedDict, cast

from babel.messages.extract import extract_python
from babel.util import parse_encoding

from ._patterns import MARKER_COMMENT, escape_literal, validate_name
from .errors import InvalidTranslationError

Extracted = tuple[int, str | None, str | tuple[str, ...], list[str]]
# Babel's ordinary pass reports an intermediate entry with no line number for a
# nested call, so what it actually yields is wider than what this plugin emits.
_RawExtracted = tuple[int | None, str | None, str | tuple[str, ...], list[str]]

# Truthy strings accepted for boolean extraction options.
_TRUE = frozenset({"1", "true", "yes", "on"})


class ExtractionError(ValueError):
    """A translation call cannot be extracted safely."""


class _FunctionSets(TypedDict):
    tr_functions: set[str]
    ntr_functions: set[str]
    gettext_functions: set[str]
    ngettext_functions: set[str]
    pgettext_functions: set[str]
    npgettext_functions: set[str]


def _option_names(options: Mapping[str, Any], key: str, default: str) -> set[str]:
    value = options.get(key, default)
    # babel.toml / pyproject.toml の [[mappings]] はオプション値をリストで渡してくる。
    # ini の空白区切り文字列と同じに扱わないと、名前が丸ごと一致しなくなる。
    text = " ".join(str(item) for item in value) if isinstance(value, list | tuple) else str(value)
    return {item.strip() for item in text.replace(",", " ").split() if item.strip()}


def _option_bool(options: Mapping[str, Any], key: str, default: bool) -> bool:
    value = options.get(key, default)
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in _TRUE


def _function_sets(options: Mapping[str, Any]) -> _FunctionSets:
    return {
        "tr_functions": _option_names(options, "tr_functions", "tr"),
        "ntr_functions": _option_names(options, "ntr_functions", "ntr"),
        "gettext_functions": _option_names(options, "gettext_functions", "gettext _ lazy_gettext"),
        "ngettext_functions": _option_names(options, "ngettext_functions", "ngettext"),
        "pgettext_functions": _option_names(
            options,
            "pgettext_functions",
            "pgettext lazy_pgettext",
        ),
        "npgettext_functions": _option_names(options, "npgettext_functions", "npgettext"),
    }


def _decode_source(
    data: bytes | str,
    options: Mapping[str, Any],
) -> tuple[str, str]:
    if isinstance(data, str):
        provisional = data.encode()
        encoding = parse_encoding(io.BytesIO(provisional)) or str(options.get("encoding", "utf-8"))
        return data, encoding

    encoding = parse_encoding(io.BytesIO(data)) or str(options.get("encoding", "utf-8"))
    if data.startswith(codecs.BOM_UTF8):
        encoding = "utf-8-sig"
    return data.decode(encoding), encoding


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

        try:
            name = validate_name(value.str or "")
        except InvalidTranslationError as exc:
            raise _fail(
                filename,
                value,
                "t-string interpolations must be simple variable names",
            ) from exc
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


def _comment_lines(source: str) -> dict[int, tuple[int, str]]:
    """コメントのみの物理行を ``{0始まり行番号: (♯の桁, コメント文字列)}`` で返す。

    行の同定にtokenizeを使うことで、座標系がASTの行番号と厳密に一致する。
    素朴な行走査と違い、文字列リテラル内の「コメントに見える行」を拾わず、
    ``\\f`` やU+2028など ``str.splitlines()`` だけが行区切りに数える文字で
    行番号がずれることもない。
    """
    comments: dict[int, tuple[int, str]] = {}
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    try:
        for token in tokens:
            if token.type == tokenize.COMMENT and not token.line[: token.start[1]].strip():
                comments[token.start[0] - 1] = (token.start[1], token.string)
    except tokenize.TokenError, IndentationError, SyntaxError:
        # ast.parseが通ったソースでは実質発生しない。途中まで集めた
        # コメントは正しいので、そのまま使う。
        pass
    return comments


def _translator_comment_block(
    comments: dict[int, tuple[int, str]],
    lineno: int,
    comment_tags: Collection[str],
) -> tuple[list[str], tuple[int, ...]]:
    """呼び出し直前の連続コメント行から翻訳者コメントブロックを取り出す。

    戻り値は (コメント本文のリスト, タグ行の0始まり行番号タプル)。
    """
    preceding: list[tuple[int, str]] = []
    index = lineno - 2
    while index >= 0 and index in comments:
        preceding.append((index, comments[index][1][1:].strip()))
        index -= 1
    preceding.reverse()

    start = next(
        (
            position
            for position, (_, comment) in enumerate(preceding)
            if any(comment.startswith(tag) for tag in comment_tags)
        ),
        None,
    )
    if start is None:
        return [], ()

    selected = preceding[start:]
    tag_lines = tuple(
        line_index
        for line_index, comment in selected
        if any(comment.startswith(tag) for tag in comment_tags)
    )
    return [comment for _, comment in selected], tag_lines


def _mask_comment_tags(
    source: str,
    comments: dict[int, tuple[int, str]],
    tag_lines: Collection[int],
) -> str:
    """Hide t-string translator tags from Babel's ordinary Python pass.

    Babel does not recognize a t-string call, so without masking it leaves that
    call's translator comment pending and can attach it to a later ordinary
    gettext message.
    """
    if not tag_lines:
        return source

    # tokenize/astの行番号は\nのみを行区切りに数えるため、splitlinesではなく
    # \nで分割する(\r\nの\rは行末の内容として保たれる)。
    physical_lines = source.split("\n")
    for index in tag_lines:
        column, comment = comments[index]
        line = physical_lines[index]
        physical_lines[index] = (
            line[: column + 1] + " " * (len(comment) - 1) + line[column + len(comment) :]
        )
    return "\n".join(physical_lines)


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
    if _matches(name, ngettext_functions) and any(
        isinstance(arg, ast.TemplateStr) for arg in call.args[:2]
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
    if _matches(name, npgettext_functions) and any(
        isinstance(arg, ast.TemplateStr) for arg in call.args[1:3]
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


def _uses_tstring_argument(
    call: ast.Call,
    *,
    tr_functions: set[str],
    ntr_functions: set[str],
    gettext_functions: set[str],
    ngettext_functions: set[str],
    pgettext_functions: set[str],
    npgettext_functions: set[str],
) -> bool:
    """Return whether a recognized call uses a t-string in a message position."""
    name = _call_name(call.func)
    if _matches(name, tr_functions) or _matches(name, gettext_functions):
        return bool(call.args and isinstance(call.args[0], ast.TemplateStr))
    if _matches(name, ntr_functions) or _matches(name, ngettext_functions):
        return any(isinstance(arg, ast.TemplateStr) for arg in call.args[:2])
    if _matches(name, pgettext_functions):
        return len(call.args) >= 2 and isinstance(call.args[1], ast.TemplateStr)
    if _matches(name, npgettext_functions):
        return any(isinstance(arg, ast.TemplateStr) for arg in call.args[1:3])
    return False


def _matches_configured_function(name: str | None, function_sets: _FunctionSets) -> bool:
    return (
        _matches(name, function_sets["tr_functions"])
        or _matches(name, function_sets["ntr_functions"])
        or _matches(name, function_sets["gettext_functions"])
        or _matches(name, function_sets["ngettext_functions"])
        or _matches(name, function_sets["pgettext_functions"])
        or _matches(name, function_sets["npgettext_functions"])
    )


def _parse_source(source: str, *, filename: str, strict: bool) -> ast.Module | None:
    try:
        return ast.parse(source, filename=filename)
    except SyntaxError as exc:
        error = ExtractionError(
            f"{filename}:{exc.lineno or 0}: skipped unparsable source ({exc.msg})"
        )
        if strict:
            raise error from exc
        warnings.warn(str(error), stacklevel=2)
        return None


def _extract_tstring_calls(
    tree: ast.Module,
    comments: dict[int, tuple[int, str]],
    *,
    filename: str,
    keywords: Collection[str],
    comment_tags: Collection[str],
    options: Mapping[str, Any],
    function_sets: _FunctionSets,
    claimed_comment_tag_lines: set[int],
) -> Iterator[Extracted]:
    strict = _option_bool(options, "strict", False)
    available = frozenset(keywords)

    calls = sorted(
        (node for node in ast.walk(tree) if isinstance(node, ast.Call)),
        key=lambda node: (node.lineno, node.col_offset),
    )
    comment_owner_columns: dict[int, int] = {}
    for call in calls:
        name = _call_name(call.func)
        configured = _matches_configured_function(name, function_sets)
        standard = name is not None and (name in available or name.rsplit(".", 1)[-1] in available)
        if configured or standard:
            comment_owner_columns.setdefault(call.lineno, call.col_offset)

    def translator_comment_block(call: ast.Call) -> tuple[list[str], tuple[int, ...]]:
        if comment_owner_columns.get(call.lineno) != call.col_offset:
            return [], ()
        return _translator_comment_block(comments, call.lineno, comment_tags)

    for call in calls:
        uses_tstring = _uses_tstring_argument(call, **function_sets)
        try:
            extracted = _extract_call(call, filename=filename, **function_sets)
        except ExtractionError as exc:
            # 拒否された翻訳呼び出しのコメントもclaimし、Babel側の通常
            # メッセージへ漏れ着くのを防ぐ。ただしplain string呼び出しが
            # Babelキーワードでもある場合は、通常抽出結果へコメントを残す。
            name = _call_name(call.func)
            standard = name is not None and (
                name in available or name.rsplit(".", 1)[-1] in available
            )
            if uses_tstring or not standard:
                _, claimed = translator_comment_block(call)
                claimed_comment_tag_lines.update(claimed)
            # One rejected call warns and is skipped; opt into strict to fail hard.
            if strict:
                raise
            warnings.warn(str(exc), stacklevel=2)
            continue
        if extracted is None:
            continue

        translator_comments, claimed = translator_comment_block(call)
        claimed_comment_tag_lines.update(claimed)
        funcname, messages = extracted
        if funcname is not None and funcname not in available:
            warnings.warn(
                f"{filename}:{call.lineno}: skipped {funcname!r} t-string because keyword "
                f"{funcname!r} is not in the extraction keyword set; keep the standard gettext "
                "keywords to extract plural and contextual messages",
                stacklevel=2,
            )
            continue

        translator_comments.append(MARKER_COMMENT)
        yield call.lineno, funcname, messages, translator_comments


def _extract_standard_calls(
    standard_source: str,
    encoding: str,
    keywords: Collection[str],
    comment_tags: Collection[str],
    options: Mapping[str, Any],
    *,
    filename: str,
) -> list[Extracted]:
    """Run Babel's ordinary Python pass, degrading like `_parse_source` does.

    ``ast.parse`` accepts a few sources that ``tokenize`` rejects (a form feed
    followed by a bare carriage return, for one), and Babel's extractor is
    tokenize-based. Letting that abort the whole ``pybabel extract`` run would
    contradict this extractor's contract that one bad file is skipped, not fatal.
    """
    try:
        messages = list(
            cast(
                "Iterator[_RawExtracted]",
                extract_python(
                    io.BytesIO(standard_source.encode(encoding)),
                    cast("Any", keywords),
                    comment_tags,
                    cast("Any", options),
                ),
            )
        )
    except tokenize.TokenError as exc:
        error = ExtractionError(f"{filename}: skipped ordinary gettext calls ({exc.args[0]})")
        if _option_bool(options, "strict", False):
            raise error from exc
        warnings.warn(str(error), stacklevel=2)
        return []
    # Babel yields an intermediate entry with no line number for a nested
    # ordinary call; its own public extract() drops those, and so do we.
    return [cast("Extracted", message) for message in messages if message[0] is not None]


def extract_tstrings(
    fileobj: Any,
    keywords: Collection[str],
    comment_tags: Collection[str],
    options: Mapping[str, Any],
) -> Iterator[Extracted]:
    """Extract ordinary Python gettext calls and t-string tr()/ntr() calls."""
    data = fileobj.read()
    filename = getattr(fileobj, "name", None) or "(unknown)"
    source, encoding = _decode_source(data, options)
    tree = _parse_source(
        source,
        filename=filename,
        strict=_option_bool(options, "strict", False),
    )
    if tree is None:
        return

    comments = _comment_lines(source)
    configured_functions = _function_sets(options)
    claimed_comment_tag_lines: set[int] = set()
    tstring_messages = list(
        _extract_tstring_calls(
            tree,
            comments,
            filename=filename,
            keywords=keywords,
            comment_tags=comment_tags,
            options=options,
            function_sets=configured_functions,
            claimed_comment_tag_lines=claimed_comment_tag_lines,
        )
    )
    standard_source = _mask_comment_tags(source, comments, claimed_comment_tag_lines)
    standard_messages = _extract_standard_calls(
        standard_source,
        encoding,
        keywords,
        comment_tags,
        options,
        filename=filename,
    )
    # Messages are merged by line. Two translation calls on one physical line
    # come out in an unspecified order — POT entries are keyed by file and line,
    # and `pybabel extract --sort-output` normalizes the rest.
    yield from heapq.merge(
        standard_messages,
        iter(tstring_messages),
        key=lambda item: item[0],
    )
