import re
from .models import BoardData
from ..system.tempfile_service import TempFileService
from pathlib import Path
from .bridgetex import build_analysis_template
import random


class PbnParser:
    output_dir = Path(__file__).parent.parent.resolve() / "temp"

    def pbn_to_hands(self, pbn: str):
        print(pbn)
        for i, board in enumerate(re.split(r"(\r\n|\n){2,}", pbn)):
            print(i, board)
            board_s = board.strip()
            if board_s == "":
                continue
            board_obj = BoardData()
            board_obj.sequence_number = i
            for match in re.finditer(r"\[([A-Za-z]+) \"([A-Za-z0-9\.\: ]+)\"\]", board_s):
                tag, value = match.groups()
                match tag:
                    case "Board":
                        board_obj.number = int(value)
                    case "Deal":
                        board_obj.apply_pbn(value)
            yield board_obj

    def pbn_to_analysis_file(self, pbn: str):
        name = f"pbn_{hex(random.getrandbits(16))[2:]}.tex"
        boards = list(self.pbn_to_hands(pbn))
        print(boards)
        TempFileService.TEMP_RWLOCK.acquire_read()
        build_analysis_template(boards, self.output_dir / name)
        TempFileService.TEMP_RWLOCK.release_read()
        return self.output_dir / name

