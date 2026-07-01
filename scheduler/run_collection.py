"""Backward-compatible entry point. The Collection Run logic now lives in
``banking_analysis.collection.runner`` (importable/testable, like the other
layers). See ADR 0003 / 0013.
"""

from banking_analysis.collection.runner import main

if __name__ == "__main__":
    main()
