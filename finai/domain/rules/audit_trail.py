import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple


@dataclass
class CalculationAuditEntry:
    index: int
    timestamp: float
    rule_name: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    prev_hash: str
    current_hash: str = ""

    def calculate_hash(self) -> str:
        payload = {
            "index": self.index,
            "timestamp": self.timestamp,
            "rule_name": self.rule_name,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "prev_hash": self.prev_hash,
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


class CalculationAuditLedger:
    def __init__(self):
        self.chain: List[CalculationAuditEntry] = []
        self._create_genesis_block()

    def _create_genesis_block(self):
        genesis = CalculationAuditEntry(
            index=0,
            timestamp=1700000000.0,
            rule_name="GENESIS",
            input_data={},
            output_data={"status": "FinAI Rule Engine Ledger Initialized"},
            prev_hash="0" * 64,
        )
        genesis.current_hash = genesis.calculate_hash()
        self.chain.append(genesis)

    def log_calculation(self, rule_name: str, input_data: Dict[str, Any], output_data: Dict[str, Any]) -> CalculationAuditEntry:
        prev_entry = self.chain[-1]
        entry = CalculationAuditEntry(
            index=len(self.chain),
            timestamp=time.time(),
            rule_name=rule_name,
            input_data=input_data,
            output_data=output_data,
            prev_hash=prev_entry.current_hash,
        )
        entry.current_hash = entry.calculate_hash()
        self.chain.append(entry)
        return entry

    def verify_integrity(self) -> Tuple[bool, int, str]:
        """
        Recomputes the entire hash chain from genesis block to current block.
        Returns: (is_valid, total_checked_blocks, latest_hash)
        """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            # Verify link to previous hash
            if current.prev_hash != previous.current_hash:
                return False, i, current.current_hash

            # Recompute block hash
            if current.current_hash != current.calculate_hash():
                return False, i, current.current_hash

        return True, len(self.chain), self.chain[-1].current_hash


# Global Ledger Singleton
GLOBAL_AUDIT_LEDGER = CalculationAuditLedger()
