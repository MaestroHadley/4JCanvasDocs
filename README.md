# 4JCanvasDocs

Practical scripts and documentation for Canvas LMS administration, SIS workflows, and Canvas Data 2 automation.

This repository is intended to be reusable by district/admin teams that need quick wins with the Canvas API plus deeper data workflows with Canvas Data 2.

## What This Repo Covers

- Canvas API automations for common admin operations
- Canvas Data 2 workflows for reporting and archive processes
- Start-of-term and SIS passback support scripts
- Documentation for operational runbooks and setup

## Repository Layout

- `LMSDB_Files_Public/`
  - Public-ready Python and shell scripts for Canvas API + Canvas Data 2
  - Sanitized placeholders for credentials and email values
  - Includes archive, attendance, enrollment, and grade sync workflows
- `CanvasScripts/`
  - Legacy and utility scripts
- `GoogleApps/`
  - Google Apps Script integrations
- `Definitions.md`
  - Common terminology used in this project
- `archive.md`
  - Archive process documentation
- `canvas_data_2.md` and `canvas_data_2_linux.md`
  - Canvas Data 2 setup and usage notes
- `Start_of_Sem.md`
  - Start-of-semester workflow notes
- `synergy_passback.md`
  - Grade passback process notes
- `sub_acct_admins.md`
  - Sub-account admin update process

## Quick Start

1. Install Python 3 and `canvasapi`.
2. Copy credential placeholders into your own local environment profile (do not commit real keys).
3. Start with scripts in `LMSDB_Files_Public/`.
4. Review related runbook markdown files before running scripts against production.

## Security Notes

- This repo is sanitized for public sharing.
- Keep all real API tokens, DB credentials, and SMTP auth in local environment variables only.
- Use beta/test Canvas instances before running workflows in production.

## Recommended First Scripts

- `LMSDB_Files_Public/admin/grade_sync/assignment_sync.py`
- `LMSDB_Files_Public/admin/start_of_semester/start_of_semester.py`
- `LMSDB_Files_Public/archive/archive_enrollment.py`
- `LMSDB_Files_Public/archive/archive_courses.py`

## Presentation Notes (NCCE)

For a fast demo narrative:

1. Show a simple Canvas API automation (`assignment_sync.py`).
2. Show a “semester operations” script (`start_of_semester.py`).
3. Show the Canvas Data 2 -> SIS import archive workflow (`archive_enrollment.py` + `archive_courses.py`).

## Author

Nicholas Hadley, M.Ed.
Digital Learning Platform Manager, 4J Schools (Eugene, Oregon)
