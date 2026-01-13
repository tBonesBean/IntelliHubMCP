def format_diagnostic_report(report):
    """
    Convert the raw diagnose() output into a clean, human-readable
    multi-line string suitable for CLI output.
    """

    lines = []
    add = lines.append

    # Header
    add("=== IntelliHub Diagnostic Report ===")
    add(f"Status: {report.get('status', 'unknown').upper()}")
    add("")

    # Path validity
    add("[Path]")
    add(f"  Valid: {report['path_valid']}")
    add("")

    # File inventory
    inv = report["file_inventory"]
    add("[File Inventory]")
    add(f"  Total files: {inv['total_files']}")
    add(f"  Markdown files: {inv['markdown_files']}")
    add(f"  Has 00_README.md: {inv['has_root_readme']}")
    if inv["missing_expected"]:
        add("  Missing expected files:")
        for f in inv["missing_expected"]:
            add(f"    - {f}")
    else:
        add("  Missing expected files: None")
    add("")

    # Schemas
    sch = report["schemas"]
    add("[Schemas]")
    add(f"  Exists: {sch['exists']}")
    add(f"  Count: {sch['count']}")
    if sch["unreadable"]:
        add("  Unreadable:")
        for f in sch["unreadable"]:
            add(f"    - {f}")
    else:
        add("  Unreadable: None")
    add("")

    # Module purposes
    mp = report["module_purposes"]
    add("[Module Purposes]")
    add(f"  Exists: {mp['exists']}")
    add(f"  Count: {mp['count']}")
    if mp["unreadable"]:
        add("  Unreadable:")
        for f in mp["unreadable"]:
            add(f"    - {f}")
    else:
        add("  Unreadable: None")
    add("")

    # Search index
    si = report["search_index"]
    add("[Search Index]")
    add(f"  Searchable: {si['searchable']}")
    add(f"  Sample results: {len(si['sample_results'])}")
    add("")

    # Issues
    add("[Issues]")
    if report["issues"]:
        for issue in report["issues"]:
            add(f"  - {issue}")
    else:
        add("  None")
    add("")

    add("=== End of Report ===")

    return "\n".join(lines)

