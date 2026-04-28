"""
Legacy EuroSAT helper retained only to prevent accidental use.

The main pipeline uses preprocessing/align_datasets.py for all label mapping and proxy
generation. This legacy script encoded a contradictory mapping and is intentionally
disabled so it cannot silently produce inconsistent datasets.
"""


def process_eurosat(*_args, **_kwargs):
    raise RuntimeError(
        "preprocessing/eurosat_processor.py is a disabled legacy helper. "
        "Use preprocessing/align_datasets.py instead."
    )


if __name__ == "__main__":
    process_eurosat()
