"""Root-level shim — delegates to scripts/review_single.py."""
import runpy, pathlib
runpy.run_path(str(pathlib.Path(__file__).parent / "scripts" / "review_single.py"), run_name="__main__")
