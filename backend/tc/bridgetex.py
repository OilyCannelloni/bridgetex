from .models import *


def bidding_header(board_n):
    vul = get_vul(board_n)
    ss = ""
    for letter in "WNES":
        if letter in vul:
            ss += f"\\vul{{{letter}}}"
        else:
            ss += f"\\nvul{{{letter}}}"

        if letter != "S":
            ss += " & "
        else:
            ss += "\\\\\n"
    return ss


def bidding_shift_dashes(board_n):
    dealer = get_dealer(board_n)
    match dealer:
        case "W":
            return "\\\\\n"
        case "N":
            return "  -  & & & \\\\\n"
        case "E":
            return "  -  &  -  & & \\\\\n"
        case "S":
            return "  -  &  -  &  -  & \\\\\n"
        case _:
            return ""


def build_analysis_page(board: BoardData):
    ss = ""
    ss += "\n\\pagebreak\n"
    ss += f"\\section*{{Rozdanie {board.sequence_number or board.number}}}\n"
    ss += board.to_handdiagramv()
    ss += r"""
\begin{table}[h!]
    \centering
    \begin{tabular}{cccc}
        """
    ss += bidding_header(board.number)
    ss += "\t\t" + bidding_shift_dashes(board.number)

    ss += r"""
    \end{tabular}
\end{table}
"""
    return ss


def build_analysis_template(boards, target_file, verbose=False):
    with open(target_file, "w") as file:
        header = r"""
\documentclass[12pt, a4paper]{article}
\usepackage{import}

\import{../../lib/}{bridge.sty}

\title{Board Set Analysis}
\author{... using MacaroniBridge/TCResultsParser}

\begin{document}
\maketitle

    
    """
        if verbose:
            print(header)
        file.write(header)

        for board in boards:
            page = build_analysis_page(board)
            if verbose:
                print(page)
            file.write(page)

        footer = r"""
\end{document}        
"""
        if verbose:
            print(footer)
        file.write(footer)

def hand_to_pbn(board: BoardData):
    def fmt_hand(hand: Hand) -> str:
        suits = [
            hand.spades if hand.spades else "",
            hand.hearts if hand.hearts else "",
            hand.diamonds if hand.diamonds else "",
            hand.clubs if hand.clubs else "",
        ]
        return ".".join(suits)

    vul = get_vul(board.number) or "None"
    dealer = get_dealer(board.number)
    # Deal order in PBN is always: N, E, S, W (starting from dealer)
    hands = {
        "N": fmt_hand(board.north),
        "E": fmt_hand(board.east),
        "S": fmt_hand(board.south),
        "W": fmt_hand(board.west),
    }
    deal_str = f"N:{hands['N']} {hands['E']} {hands['S']} {hands['W']}"
    pbn_lines = [
        f"[Board \"{board.number}\"]",
        f"[Dealer \"{dealer}\"]",
        f"[Vulnerable \"{vul}\"]",
        f"[Deal \"{deal_str}\"]",
        "\n"
    ]

    return "\n".join(pbn_lines)


def build_pbn(boards, target_file, verbose=False):
    ss = ""
    for board in boards:
        ss += hand_to_pbn(board)

    with open(target_file, "w") as file:
        file.write(ss)