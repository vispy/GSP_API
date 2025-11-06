# stdlib imports
import os

# pip imports
import uuid


class UuidUtils:

    GSP_UUID_COUNTER: int = 0

    @staticmethod
    def generate_uuid() -> str:
        # if GSP_UUID_COUNTER is set, use a deterministic uuid for testing purposes
        # - uuid becomes "uuid-counter-<counter>"
        if "GSP_UUID_COUNTER" in os.environ:
            _uuid = UuidUtils.GSP_UUID_COUNTER
            UuidUtils.GSP_UUID_COUNTER += 1
            return f"uuid-counter-{_uuid}"

        return str(uuid.uuid4())
