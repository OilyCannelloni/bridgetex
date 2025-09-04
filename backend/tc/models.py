from dataclasses import dataclass
from pydantic import BaseModel
import re

def get_vul(board_n):
    return ["", "NS", "EW", "NSEW", "NS", "EW", "NSEW", "", "EW",
            "NSEW", "", "NS", "NSEW", "", "NS", "EW"][(board_n - 1) % 16]


def get_dealer(board_n):
    return "NESW"[(board_n - 1) % 4]


@dataclass
class Hand:
    spades: str
    hearts: str
    diamonds: str
    clubs: str

    def __str__(self):
        return f"♠{self.spades} ♥{self.hearts} ♦{self.diamonds} ♣{self.clubs}"

    def to_vhand(self) -> str:
        return f"\\vhand{{{self.spades}}}{{{self.hearts}}}{{{self.diamonds}}}{{{self.clubs}}}"
    
    @classmethod
    def from_pbn(cls, pbn):
        return cls(*pbn.split("."))


@dataclass
class BoardData:
    sequence_number: int = 0
    number: int = 0
    north: Hand = ""
    east: Hand = ""
    south: Hand = ""
    west: Hand = ""

    def __str__(self):
        return "\n".join((str(x) for x in (self.north, self.east, self.south, self.west)))

    def to_handdiagramv(self) -> str:
        return (f"\\handdiagramv[{self.number}]{{{self.north.to_vhand()}}}\n"
                f"{{{self.east.to_vhand()}}}\n"
                f"{{{self.south.to_vhand()}}}\n"
                f"{{{self.west.to_vhand()}}}\n"
                f"{{{get_vul(self.number)}}}\n")
    
    def apply_pbn(self, pbn):
        seat = re.match(r"^([NESW]):", pbn).groups()[0]
        
        hands = [None] * 4
        for i, hand in enumerate(pbn[2:].split(" ")):
            hands[("NESW".index(seat) + i) % 4] = Hand.from_pbn(hand)

        self.north = hands[0]
        self.east = hands[1]
        self.south = hands[2]
        self.west = hands[3]

    def iter_hands(self):
        yield self.north
        yield self.east
        yield self.south
        yield self.west
    

class CodeDTO(BaseModel):
    code: str


class FileTypes(BaseModel):
    tex: bool
    pbn: bool

class DownloadTcDTO(BaseModel):
    url: str
    boards: str
    file_types: FileTypes
