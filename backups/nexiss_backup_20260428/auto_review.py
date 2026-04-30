"""Root-level shim — delegates to scripts/auto_review.py."""
import runpy, pathlib
runpy.run_path(str(pathlib.Path(__file__).parent / "scripts" / "auto_review.py"), run_name="__main__")
