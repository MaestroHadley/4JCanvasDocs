# LMSDB_Files_Public

Public-safe package of Canvas LMS automation scripts.

## Included Areas

- `admin/`
  - Start-of-semester updates, PD enrollment, and grade sync scripts
- `archive/`
  - Two-step archive workflow (enrollment deactivation + course archive)
- `eoa_attendance/`
  - Attendance report generation and email workflow
- `CD2/`
  - Canvas Data 2 output/log directories (`.gitkeep` only)

## Setup

1. Populate environment variables for Canvas API and DB access in your local profile.
2. Replace placeholder values like `add_your_*` and `your_*` with local runtime values only.
3. Validate in beta/test before production runs.

## Important

- Do not commit real secrets.
- Generated logs/exports/reports are ignored by git in this package.
