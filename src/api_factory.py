from src.adapters.fred_adapter import FredAdapter
from src.adapters.cftc_adapter import CftcAdapter

_ADAPTERS = {
    "fred": FredAdapter(),
    "cftc": CftcAdapter(),
}


def get_adapter(source: str):
    adapter = _ADAPTERS.get(source)
    if adapter is None:
        raise ValueError(f"Unknown adapter source: '{source}'")
    return adapter
