def apply_exit_logic(audit_results, policy):
    """
    Determine exit code based on audit results and enforcement mode.
    """
    if audit_results.get("failed", False):
        print("[FAIL] Audit did not pass enforcement rules ❌")
        exit_code = audit_results.get("exit_code", 2)
        exit(exit_code)
    else:
        print("[PASS] Audit passed or violations were in dry-run mode ✅")