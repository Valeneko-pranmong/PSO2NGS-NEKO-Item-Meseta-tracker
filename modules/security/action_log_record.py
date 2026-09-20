from datetime import datetime
import re
from typing import Optional

MESETA_REGEX = re.compile(r'\t(?:N-)?Meseta\s*\(\s*(\d+)\s*\)', re.IGNORECASE)
WALLET_REGEX = re.compile(r'\tCurrent(?:N-)?Meseta\s*\(\s*(\d+)\s*\)', re.IGNORECASE)
ITEM_REGEX = re.compile(r'\t([^\t]+)\tNum\((\d+)\)')


class ActionLogRecord:
    """Represents a structured record parsed from a PSO2:NGS ActionLog line."""

    def __init__(
        self,
        timestamp: Optional[datetime] = None,
        sequence_number: int = -1,
        action: str = "",
        player_id: str = "",
        character_name: str = "",
        meseta_drop: int = 0,
        current_wallet: int = 0,
        has_wallet_update: bool = False,
        item_name: str = "",
        item_count: int = 0,
        raw_line: str = "",
    ):
        self.timestamp = timestamp
        self.sequence_number = sequence_number
        self.action = action
        self.player_id = player_id
        self.character_name = character_name
        self.meseta_drop = meseta_drop
        self.current_wallet = current_wallet
        self.has_wallet_update = has_wallet_update
        self.item_name = item_name
        self.item_count = item_count
        self.raw_line = raw_line

    @property
    def has_meseta_drop(self) -> bool:
        return self.meseta_drop > 0

    @property
    def has_item_drop(self) -> bool:
        return bool(self.item_name and self.item_count > 0)

    def __repr__(self) -> str:
        return (
            f"ActionLogRecord(seq={self.sequence_number}, action='{self.action}', "
            f"char='{self.character_name}', drop={self.meseta_drop}, "
            f"wallet={self.current_wallet}, item='{self.item_name}'x{self.item_count})"
        )


class ActionLogParser:
    """Parses raw lines from NGS ActionLog into structured ActionLogRecord objects."""

    @staticmethod
    def parse_line(line: str) -> Optional[ActionLogRecord]:
        if not line or not line.strip():
            return None

        clean_line = line.strip()
        parts = clean_line.split('\t')
        if len(parts) < 3:
            return None

        # 1. Timestamp (parts[0])
        dt: Optional[datetime] = None
        ts_str = parts[0].strip()
        try:
            dt = datetime.fromisoformat(ts_str)
        except Exception:
            try:
                dt = datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S")
            except Exception:
                dt = None

        # 2. Sequence Number (parts[1])
        seq = -1
        try:
            seq = int(parts[1].strip())
        except (ValueError, IndexError):
            pass

        # 3. Action Tag (parts[2])
        action = parts[2].strip()

        # 4. Player ID (parts[3]) & Character Name (parts[4])
        player_id = ""
        character_name = ""
        if len(parts) >= 5 and parts[3].strip().isdigit():
            player_id = parts[3].strip()
            cname = parts[4].strip()
            if cname and not cname.startswith("[") and "Num(" not in cname:
                character_name = cname

        # 5. Meseta Drop (Only parse for legitimate in-game farming actions, ignoring warehouse/storage/shops)
        meseta_drop = 0
        m_match = None
        if ActionLogParser.is_valid_farming_action(action, raw_line=line):
            m_match = MESETA_REGEX.search(line)
            if m_match:
                try:
                    meseta_drop = int(m_match.group(1))
                except ValueError:
                    pass

        # 6. Current Wallet
        current_wallet = 0
        has_wallet_update = False
        w_match = WALLET_REGEX.search(line)
        if w_match:
            try:
                current_wallet = int(w_match.group(1))
                has_wallet_update = True
            except ValueError:
                pass

        # 7. Item Drop
        item_name = ""
        item_count = 0
        if not m_match and "Num(" in line:
            i_match = ITEM_REGEX.search(line)
            if i_match:
                iname = i_match.group(1).strip()
                try:
                    icnt = int(i_match.group(2))
                    if iname and not iname.startswith("[") and "Meseta" not in iname:
                        item_name = iname
                        item_count = icnt
                except ValueError:
                    pass

        return ActionLogRecord(
            timestamp=dt,
            sequence_number=seq,
            action=action,
            player_id=player_id,
            character_name=character_name,
            meseta_drop=meseta_drop,
            current_wallet=current_wallet,
            has_wallet_update=has_wallet_update,
            item_name=item_name,
            item_count=item_count,
            raw_line=line,
        )

    @staticmethod
    def is_valid_farming_action(action: str, has_wallet_update: bool = False, raw_line: str = "") -> bool:
        if (
            "[Pickup]" in action
            or "[AutoSell]" in action
            or "[Reward]" in action
            or "[Clear]" in action
        ):
            return True
        if has_wallet_update and "[" not in raw_line:
            return True
        return False
