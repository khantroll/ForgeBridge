import sys


if __name__ == '__main__':
    try:
        if len(sys.argv) == 3 and sys.argv[1] == '--bundle-check':
            from gui_smoke import check
            check(sys.argv[2])
        else:
            from forgebridge.gui import main
            raise SystemExit(main())
    except Exception as exc:
        from forgebridge.gui_errors import startup_error
        startup_error(exc)
        raise SystemExit(1)
