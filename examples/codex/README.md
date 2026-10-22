# Optional Codex behavior example

This example asks Codex to use the real `merge-pdfs` MCP tool with generated,
one-page blank PDFs. It checks that an existing output is preserved when
`overwrite=false`, followed by a successful two-page merge to a new file.
No personal PDF or folder is read. The launcher restricts allowed roots to the
disposable fixture's working directory.

From the repository root, in a virtual environment:

```console
python -m pip install -r examples/codex/requirements.txt
python -m pytest -c examples/codex/pytest.ini examples/codex --codex-bin=not-installed -q
```

Replay needs only pytest-codex and the pinned PyPDF2 fixture generator/reader.
It needs no MCP SDK, Codex binary, login or model calls. It restores the recorded
PDF and checks it, rather than running today's server. A separate pytest config
and non-default filename keep this example out of ordinary test discovery.
No runtime dependencies or existing CI workflows are changed.

For a fresh observation, install `requirements-live.txt`, activate that
environment so `python` resolves to it, and use a logged-in Codex CLI 0.163.0:

```console
python -m pip install -r examples/codex/requirements-live.txt
python -m pytest -c examples/codex/pytest.ini examples/codex --codex-record -q
```

Recording consumes model quota and uses `gpt-6-luna`. Only `merge-pdfs` is exposed
and approved for this fixture's test process; global Codex settings are untouched.
Review the test before recording. It checks exact relative paths, tool arguments,
refusal text, success text, unchanged existing output, the merged page count and
absence of shell commands or other file changes.

The test copies current server sources with normalized line endings. Source
changes invalidate the recording; update the CLI pin and re-record intentionally
when upgrading. PyPDF2 is pinned because fixture bytes participate in the key.

## Recorded evidence

- Upstream source: `361f409320e3e8608155bc855ac70893c1d77ad1`.
- Recorded on Windows, Python 3.13, Codex CLI 0.163.0, MCP SDK 1.30.0 and
  PyPDF2 3.0.1. One successful observation, not a reliability estimate.
- First setup attempt was denied by tool approval policy; the test failed.
  The committed observation was recorded after scoping approval to this fixture.
- Thread identifier anonymized; nonbehavioral startup stderr omitted. Tool
  arguments, results, usage and generated PDF bytes are retained.
