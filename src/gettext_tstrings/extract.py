"""Message extraction plugin for Python t-string translation calls."""

from __future__ import annotations

import ast
import codecs
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
PositionedExtracted = tuple[int, int, int, str | None, str | tuple[str, ...], list[str]]
StandardCallPosition = tuple[int, int, bool, str]
TokenEnd = tuple[int, int]

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
    value = str(options.get(key, default))
    return {item.strip() for item in value.replace(",", " ").split() if item.strip()}


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
) -> Iterator[PositionedExtracted]:
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
        yield (
            call.lineno,
            call.lineno,
            call.col_offset,
            funcname,
            messages,
            translator_comments,
        )


def _position_standard_source(
    tree: ast.Module,
    source: str,
    keywords: Collection[str],
    function_sets: _FunctionSets,
) -> tuple[str, dict[str, None], dict[str, StandardCallPosition]]:
    """Babelキーワードを一意名へ置換し、各結果を元の位置へ戻す情報を返す。

    Babelの公開抽出形式は列を持たず、同名呼び出しの一部がネスト構造に
    よって出力されないこともある。関数名ごとの序数では後続結果と位置が
    ずれるため、各NAMEトークンを一意なキーワードへ置換してBabel自身に
    対応を保持させる。置換は改行を変えないのでメッセージ行は維持される。
    """
    available = frozenset(keywords)
    physical_lines = source.split("\n")
    tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    existing_names = {token.string for token in tokens if token.type == tokenize.NAME}

    prefix = "__gettext_tstrings_position_"
    while any(name.startswith(prefix) for name in existing_names):
        prefix = f"_{prefix}"

    replacements: dict[int, list[tuple[int, int, str]]] = {}
    positioned_keywords: dict[str, None] = {}
    positions: dict[str, StandardCallPosition] = {}
    unique_by_end: dict[TokenEnd, tuple[str, str, int, int]] = {}
    counter = 0
    for token in tokens:
        if token.type != tokenize.NAME or token.string not in available:
            continue
        unique = f"{prefix}{counter}"
        counter += 1
        line = physical_lines[token.end[0] - 1]
        end_byte_column = len(line[: token.end[1]].encode())
        unique_by_end[(token.end[0], end_byte_column)] = (
            unique,
            token.string,
            token.start[0],
            len(line[: token.start[1]].encode()),
        )
        replacements.setdefault(token.start[0] - 1, []).append(
            (token.start[1], token.end[1], unique),
        )
        positioned_keywords[unique] = None

    calls = sorted(
        (node for node in ast.walk(tree) if isinstance(node, ast.Call)),
        key=lambda node: (node.lineno, node.col_offset),
    )
    for call in calls:
        name = _call_name(call.func)
        if name is None:
            continue

        end_lineno = call.func.end_lineno
        end_col_offset = call.func.end_col_offset
        if end_lineno is None or end_col_offset is None:
            continue
        positioned = unique_by_end.get((end_lineno, end_col_offset))
        if positioned is None:
            continue
        unique, source_basename, _, _ = positioned
        # astは識別子をNFKC正規化する一方、Babelはソース上のNAMEトークンを
        # そのままキーワードと照合する。Babelが実際に返す呼び出しだけを
        # 一意名へ置換して位置対応へ含める。
        positions[unique] = (
            call.lineno,
            call.col_offset,
            _uses_tstring_argument(call, **function_sets),
            source_basename,
        )

    # AST Callに対応しないキーワードトークンも、Babelが結果を返した場合に
    # 元の関数名と字句位置へ戻せるようフォールバック位置を持たせる。
    for unique, source_basename, lineno, column in unique_by_end.values():
        positions.setdefault(unique, (lineno, column, False, source_basename))

    for line_index, line_replacements in replacements.items():
        line = physical_lines[line_index]
        for start, end, replacement in reversed(line_replacements):
            line = line[:start] + replacement + line[end:]
        physical_lines[line_index] = line
    return "\n".join(physical_lines), positioned_keywords, positions


def _position_standard_messages(
    messages: Collection[Extracted],
    positions: Mapping[str, StandardCallPosition],
) -> list[PositionedExtracted]:
    """Babelの通常抽出結果に位置を補い、t-string側の中間結果を除く。"""
    positioned: list[PositionedExtracted] = []
    for lineno, funcname, message, comments in messages:
        key = funcname or ""
        position = positions.get(key)

        # Babelの通常抽出器は、t-stringを解釈できなくても関数名だけを
        # 認識した中間項目を返す。対応するt-string結果はAST側で出す。
        if position is not None and position[2]:
            continue
        # ネストした通常gettext呼び出しでは、Babelが最終結果にならない
        # lineno=Noneの中間項目を返すことがある。公開extract()も捨てる。
        if lineno is None:
            continue

        sort_line, column = position[:2] if position is not None else (lineno, -1)
        original_funcname = position[3] if position is not None else funcname
        positioned.append((lineno, sort_line, column, original_funcname, message, comments))
    return positioned


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
    positioned_source, positioned_keywords, standard_positions = _position_standard_source(
        tree,
        standard_source,
        keywords,
        configured_functions,
    )
    standard_raw = positioned_source.encode(encoding)
    standard_messages = list(
        cast(
            "Iterator[Extracted]",
            extract_python(
                io.BytesIO(standard_raw),
                cast("Any", positioned_keywords),
                comment_tags,
                cast("Any", options),
            ),
        )
    )
    positioned_standard = _position_standard_messages(
        standard_messages,
        standard_positions,
    )
    combined = sorted(
        (*positioned_standard, *tstring_messages),
        key=lambda item: (item[1], item[2]),
    )
    for lineno, _, _, funcname, message, translator_comments in combined:
        yield lineno, funcname, message, translator_comments
