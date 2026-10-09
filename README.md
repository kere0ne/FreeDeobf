# FreeDeobf

FreeDeobf is an offline, open-source framework for source-code deobfuscation. It has no website, telemetry, remote API, or runtime execution of input.

> **Scope:** no tool can fully deobfuscate every program. VM-based protectors, encrypted payloads, custom interpreters, and missing runtime keys require protector-specific analysis. FreeDeobf is designed to grow through isolated transforms and regression fixtures.

## Current implementation

- Python 3.10+, standard library only.
- CLI reads a file or standard input and writes a file or standard output.
- Conservative Lua decimal string escape decoding.
- Conservative literal concatenation folding.
- Decodes explicit `base64.decode('...')` / `b64decode('...')` wrappers when output is printable UTF-8.
- Normalizes whitespace.
- Transformation report with `--report`.
- Does not execute or evaluate input source.

## Install

```bash
python -m pip install -e .
freedeobf sample.lua -o cleaned.lua --language lua --report
cat obfuscated.lua | freedeobf --language auto > cleaned.lua
python -m unittest discover -s tests -v
```

## Architecture

Each transform is a pure function: `str -> (str, detail)`. Add new passes in `freedeobf/engine.py`, and add a fixture-based regression test before enabling a pass by default. Prefer tokenizers/AST parsers over regular expressions when transformations need language grammar.

## Roadmap

1. Lua/Luau lexer and AST-aware constant folding.
2. Protector fingerprints and fixtures for Wynfuscate, IronBrew, MoonSec, and Luraph variants.
3. Control-flow and constant-propagation passes for known Lua VM layouts.
4. JavaScript AST passes and dedicated support for common JavaScript obfuscator families.
5. Differential tests against known unobfuscated fixtures; report confidence and preserve original input.

Wynfuscate support is **not yet implemented** in this starter release. A real devirtualizer must identify and model the protector's exact VM format; a generic regex cannot safely reverse arbitrary versions.

## Security

Treat unknown source as hostile. FreeDeobf never executes input, but decoded output may still contain dangerous code. Review before running it. Only analyze code you are authorized to inspect.

## Sample corpus

Use sample repositories as external test corpora; do not bulk-copy their source into this repository without checking each repository's license and provenance.

- https://github.com/terrorlua/obfuscator-samples
- https://github.com/Xyraniz/Obfuscator-Samples

## License

MIT. See `LICENSE`.
