#!/usr/bin/env python3
"""
External Tool Arsenal — VAPT Cycle Reference — Public Portfolio Edition
Muhammad Huzaifa Jamil — Cyber Security (SW) Engineer — July 2026

Sanitized derivative of reports/arsenal/gen_arsenal_report.py for public /
portfolio distribution. Reuses the shared design system, tool data, and
phase-detail rendering from the internal generator (single source of truth
for tool descriptions), but:
  - strips all "Virtuosoft" branding, replacing it with personal attribution
  - drops the "Currently Installed" / gap-tracking framing entirely
  - removes Section 09 (Installation & Detection Methodology) and Section 10
    (Coverage Gaps & Excluded Entries) — internal paths, script names, and
    the excluded-tools list have no place in a public-facing document
  - removes the "INTERNAL REFERENCE" classification labels
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "arsenal"))
from gen_arsenal_report import (  # noqa: E402
    TOOLS, PHASES, PHASE_ORDER, COVER_COLOR, ACCENT,
    h, code, build_css, compute_stats,
    section_title, make_stats_row, make_summary_table, make_phase_section,
)

OUT = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT, exist_ok=True)

OWNER_NAME = "Muhammad Huzaifa Jamil"
OWNER_TITLE = "Cyber Security (SW) Engineer"
OWNER_EMAILS = ["m.huzaifa.jamil@outlook.com", "m.huzaifa.jamil.cys@gmail.com"]

CSS = build_css(f"{OWNER_NAME.upper()} — EXTERNAL TOOL ARSENAL PORTFOLIO")


def make_cover_portfolio(counts, total, n_categories):
    stats = make_stats_row(counts, {"OK": total, "MISSING": 0})
    emails_line = " &middot; ".join(OWNER_EMAILS)
    return f'''
<div class="cover">
  <div class="cover-band">
    <div class="cover-classification">Portfolio Document &nbsp;&middot;&nbsp; Security Tooling Reference &nbsp;&middot;&nbsp; {h(OWNER_NAME)}</div>
    <div class="cover-doc-type">&#9656; External Tool Arsenal &amp; VAPT Cycle Mapping</div>
    <div class="cover-id">ARSENAL</div>
    <div class="cover-subtitle-band">&#9654; {total} tools catalogued &nbsp;|&nbsp; {n_categories} categories &nbsp;|&nbsp; 5 VAPT phases</div>
  </div>
  <div class="cover-body">
    <h1 class="cover-title">External Tool Arsenal &amp; VAPT Cycle Reference</h1>
    <p class="cover-description">
      A personal, hands-on reference for the {total} external command-line tools I use across
      reconnaissance, scanning, vulnerability assessment, exploitation, and mobile security
      testing. Each tool is mapped to the stage of the Vulnerability Assessment &amp; Penetration
      Testing (VAPT) lifecycle it serves, with a plain-language rationale for why it earns a
      place in my toolkit and a representative command showing how it's actually invoked.
    </p>
    <div class="cover-rule"></div>
    <table class="cover-meta-table">
      <tr><td class="mk">Document Subject</td><td class="mv">Personal VAPT Tool Arsenal &amp; Reference</td></tr>
      <tr><td class="mk">Tools Catalogued</td><td class="mv">{total} (across {n_categories} categories)</td></tr>
      <tr><td class="mk">VAPT Phases Mapped</td><td class="mv">5 &mdash; Recon, Scanning, Assessment, Exploitation, Mobile/Post-Exploitation</td></tr>
      <tr><td class="mk">Reference Date</td><td class="mv">July 2026</td></tr>
      <tr><td class="mk">Author</td><td class="mv">{h(OWNER_NAME)}</td></tr>
      <tr><td class="mk">Title</td><td class="mv">{h(OWNER_TITLE)}</td></tr>
      <tr><td class="mk">Contact</td><td class="mv">{emails_line}</td></tr>
      <tr><td class="mk">Document Version</td><td class="mv">1.0 &mdash; Portfolio Edition</td></tr>
    </table>
    {stats}
  </div>
  <div class="cover-footer">
    <span>Public portfolio document</span>
    <span class="assessor">{h(OWNER_NAME)}<br>{emails_line}</span>
    <span>{h(OWNER_TITLE.upper())}</span>
  </div>
</div>'''


def make_mgmt_summary_portfolio(total, n_categories):
    legend_items = "".join(
        f'<td><div class="phase-legend-item" style="background:{PHASES[p]["color"]};">'
        f'<div class="phase-legend-num">PHASE {PHASES[p]["num"]}</div>'
        f'<div class="phase-legend-label">{PHASES[p]["short"]}</div>'
        f'</div></td>'
        for p in PHASE_ORDER
    )
    return f'''
<div class="section">
  {section_title("00", "Management Summary &mdash; Plain-English Overview")}

  <div class="mgmt-summary">
    <div class="mgmt-summary-title">&#9654; For Non-Technical Readers &mdash; What This Document Is</div>

    <table class="mgmt-grid-table">
      <tr>
        <td>
          <div class="mgmt-card">
            <div class="mgmt-card-title">What Is a VAPT Cycle?</div>
            <div class="mgmt-card-body">
              A Vulnerability Assessment &amp; Penetration Test (VAPT) is not one activity — it is a
              sequence of stages, each building on the last: find what exists, map how it responds,
              check it against known weaknesses, prove exploitability, and (for mobile apps) get
              inside the running application itself. This document groups every tool I use by
              which of those five stages it belongs to.
            </div>
          </div>
        </td>
        <td>
          <div class="mgmt-card">
            <div class="mgmt-card-title">Why So Many Separate Tools?</div>
            <div class="mgmt-card-body">
              No single tool does all five stages well — each one specializes (subdomain discovery,
              port scanning, injection testing, credential attacks, mobile instrumentation) the same
              way a physical security audit uses different specialists for locks, alarms, and safes.
              <strong>{total} tools across {n_categories} categories</strong> give me
              professional-grade coverage at every stage instead of relying on one generalist tool
              to do all of it poorly.
            </div>
          </div>
        </td>
      </tr>
    </table>

    <div class="mgmt-card mgmt-card-full">
      <div class="mgmt-card-title">What Do the Phase Colours Mean?</div>
      <div class="mgmt-card-body">
        <table class="phase-legend-table"><tr>{legend_items}</tr></table>
        Work generally flows left to right — Recon feeds Scanning, Scanning feeds Assessment,
        Assessment feeds Exploitation — though in practice a real engagement loops back and
        forth between stages as new information surfaces.
      </div>
    </div>

    <div class="mgmt-card mgmt-card-full">
      <div class="mgmt-card-title">What&rsquo;s the Bottom Line?</div>
      <div class="mgmt-card-body">
        <strong>Every tool in this catalogue is one I have personally used hands-on</strong> across
        reconnaissance, scanning, assessment, and exploitation work — this is a working reference
        built from practice, not a theoretical wishlist.
      </div>
    </div>
  </div>
</div>'''


def assemble_html():
    counts, status_counts, n_categories = compute_stats()
    total = len(TOOLS)

    phase_sections = "".join(
        make_phase_section(p, f"{i+4:02d}") for i, p in enumerate(PHASE_ORDER)
    )

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>External Tool Arsenal &amp; VAPT Cycle Reference &mdash; {h(OWNER_NAME)}</title>
<style>
{CSS}
</style>
</head>
<body>

<!-- ── COVER PAGE ───────────────────────────────────────────────────────── -->
{make_cover_portfolio(counts, total, n_categories)}

<!-- ── SECTION 00: MANAGEMENT SUMMARY ──────────────────────────────────── -->
{make_mgmt_summary_portfolio(total, n_categories)}

<!-- ── SECTION 01: EXECUTIVE SUMMARY ───────────────────────────────────── -->
<div class="section">
  {section_title("01", "Executive Summary")}

  <p>This document provides a complete inventory of the <strong>{total} external command-line
  tools</strong> in my personal security-testing toolkit, spanning <strong>{n_categories}
  functional categories</strong> from passive subdomain enumeration through mobile runtime
  instrumentation. Every tool is mapped to exactly one of the <strong>5 stages of the VAPT
  lifecycle</strong> it primarily serves, alongside a plain-language rationale for why it earned
  a place in the toolkit and a representative command demonstrating real-world usage.</p>

  <p>This is a living reference, not a static list — each entry reflects a tool I have actually
  run against real targets, with the command syntax and rationale drawn from that hands-on use
  rather than copied from a README.</p>

  <div class="callout avoid">
    <div class="callout-label">How to Read This Document</div>
    &sect;02 gives the full flat inventory as a single scannable table. &sect;03 breaks down tool
    counts and the phase model itself. &sect;04&ndash;08 give one detailed card per tool, grouped
    by the VAPT phase it belongs to, each with a "why" rationale and an example invocation.
  </div>
</div>

<!-- ── SECTION 02: FULL TOOL INVENTORY TABLE ───────────────────────────── -->
<div class="section pb">
  {section_title("02", "Full Tool Inventory Table")}
  <p>The table below lists all {total} tools in phase order (Recon &rarr; Scanning &rarr;
  Assessment &rarr; Exploitation &rarr; Mobile/Post-Exploitation). Full rationale and example
  commands for each tool are in the phase-detail sections that follow (&sect;04&ndash;08).</p>

  {make_summary_table()}
</div>

<!-- ── SECTION 03: VAPT CYCLE &amp; PHASE BREAKDOWN ────────────────────── -->
<div class="section pb">
  {section_title("03", "VAPT Cycle &amp; Phase Breakdown")}
  <p>My toolkit is organised around a standard 5-stage penetration-testing lifecycle. Tool
  counts per phase are shown below; the detailed rationale for each phase's tools follows in
  &sect;04&ndash;08.</p>

  {make_stats_row(counts, status_counts)}

  <ul class="body-list">
    <li><strong>Phase 1 &mdash; Reconnaissance &amp; OSINT ({counts["recon"]} tools):</strong>
        {PHASES["recon"]["blurb"]}</li>
    <li><strong>Phase 2 &mdash; Scanning &amp; Enumeration ({counts["scan"]} tools):</strong>
        {PHASES["scan"]["blurb"]}</li>
    <li><strong>Phase 3 &mdash; Vulnerability Assessment ({counts["assess"]} tools):</strong>
        {PHASES["assess"]["blurb"]}</li>
    <li><strong>Phase 4 &mdash; Exploitation ({counts["exploit"]} tools):</strong>
        {PHASES["exploit"]["blurb"]}</li>
    <li><strong>Phase 5 &mdash; Mobile Runtime &amp; Post-Exploitation ({counts["mobile"]} tools):</strong>
        {PHASES["mobile"]["blurb"]}</li>
  </ul>

  <div class="callout avoid">
    <div class="callout-label">Note on Dual-Use Tools</div>
    Several tools genuinely span two phases — <code>gf</code>/<code>qsreplace</code>/<code>anew</code>
    are enumeration-support utilities also used to feed exploitation pipelines, and
    <code>jadx</code>/<code>apkleaks</code> perform static mobile recon that later informs the
    Phase 5 runtime work. Each tool below is assigned to the phase where it is <em>first</em>
    and most characteristically used, to keep the inventory a strict partition rather than an
    overlapping one.
  </div>
</div>

{phase_sections}

</body>
</html>"""


if __name__ == "__main__":
    html_content = assemble_html()

    html_path = f"{OUT}/EXTERNAL_TOOL_ARSENAL_PORTFOLIO_Muhammad_Huzaifa_Jamil.html"
    pdf_path = f"{OUT}/EXTERNAL_TOOL_ARSENAL_PORTFOLIO_Muhammad_Huzaifa_Jamil.pdf"

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"HTML written: {html_path}")

    print(f"Generating PDF: {pdf_path}")
    result = subprocess.run(
        ["python3", "-m", "weasyprint", html_path, pdf_path],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        size_kb = os.path.getsize(pdf_path) // 1024
        print(f"  PDF generated: {pdf_path}  ({size_kb} KB)")
    else:
        print(f"  ERROR generating PDF:\n{result.stderr[:2000]}")

    print("\nDone.")
