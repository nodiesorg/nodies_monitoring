from enum import Enum


class ChainSyncStatus(Enum):
    UNKNOWN = -1
    SYNCING = 0
    SYNCED = 1
    STOPPED = 2
