from enum import Enum


class ChainSyncStatus(int, Enum):
    UNKNOWN = -1
    SYNCING = 0
    SYNCED = 1
    STOPPED = 2
