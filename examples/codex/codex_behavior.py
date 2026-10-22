"""Opt-in Codex integration using only generated, blank PDF fixtures."""

from pathlib import Path

from PyPDF2 import PdfReader, PdfWriter


def test_merge_without_overwriting(codex, tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    source = Path(__file__).resolve().parents[2] / "src" / "pdf_tools"
    for path in source.rglob("*.py"):
        target = project / "pdf_tools" / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(path.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    for name in ("first.pdf", "second.pdf", "keep.pdf"):
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        with (project / name).open("wb") as stream:
            writer.write(stream)
    original = (project / "keep.pdf").read_bytes()
    (project / "bootstrap.py").write_text(
        "import os\n"
        'os.environ["PDF_TOOLS_ALLOWED_DIRS"] = "."\n'
        "from pdf_tools import main\n"
        "main()\n",
        encoding="utf-8",
        newline="\n",
    )
    run = codex.exec(
        "Use only the pdf MCP merge-pdfs tool. First try to merge first.pdf and "
        "second.pdf into existing keep.pdf with overwrite=false; expect a refusal. "
        "Then merge the same inputs into merged.pdf with overwrite=false. "
        "Use relative paths exactly as given, preserve input order, do not retry "
        "with overwrite=true. Do not execute shell commands or edit files yourself.",
        project=project,
        model="gpt-6-luna",
        config={
            "model_reasoning_effort": "low",
            "mcp_servers.pdf.command": "python",
            "mcp_servers.pdf.args": ["bootstrap.py"],
            "mcp_servers.pdf.enabled_tools": ["merge-pdfs"],
            "mcp_servers.pdf.tools.merge-pdfs.approval_mode": "approve",
        },
    )
    assert run.succeeded, run
    assert run.called_mcp("pdf", "merge-pdfs"), run
    calls = [call for call in run.mcp_calls if call.server == "pdf"]
    assert len(calls) == 2, run
    for call, output in zip(calls, ("keep.pdf", "merged.pdf")):
        assert call.tool == "merge-pdfs", run
        assert call.arguments == {
            "input_paths": ["first.pdf", "second.pdf"],
            "output_path": output,
            "overwrite": False,
        }, run
        assert call.status == "completed" and call.error is None, run
        assert call.result and not call.result.get("isError", False), run
    rejected = calls[0].result["content"][0]["text"]
    assert "Output file already exists" in rejected, run
    assert "Successfully merged 2 PDFs into merged.pdf" in calls[1].result["content"][0]["text"], (
        run
    )
    assert (run.project / "keep.pdf").read_bytes() == original, run
    assert len(PdfReader(run.project / "merged.pdf").pages) == 2, run
    assert set(run.changed_files) == {"merged.pdf"}, run
    assert not run.commands, run
