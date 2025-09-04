"""
This module is used to scrape the bridge hands from the TC Results website
and generate a LaTeX file with the hand diagrams.
"""

import re
import time
import random
from typing import Generator
from pydantic import BaseModel
from dataclasses import dataclass
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, JavascriptException, NoSuchElementException
from abc import ABC, abstractmethod

from .models import *
from .bridgetex import build_analysis_template, build_pbn
from ..system.tempfile_service import TempFileService


class SSEEvent(BaseModel):
    @abstractmethod
    def to_sse() -> str:
        pass

class BoardLoadedEvent(SSEEvent, ABC):
    sequence_number: int
    tournament_seqnence_number: int
    board_number: str
    total_boards: int
    board_content: str = ""

    def to_sse(self):
        return f"event: boardLoaded\ndata: {self.model_dump_json()}\n\n"

class TcFileReadyEvent(SSEEvent, ABC):
    session_id: str 
    file_type: str

    def to_sse(self):
        return f"event: tcFileReady\ndata: {self.model_dump_json()}\n\n"
    

class ErrorEvent(SSEEvent, ABC):
    message: str   

    def to_sse(self) -> str:
        return f"event: download_error\ndata: {self.model_dump_json()}\n\n"


class CloseEvent(SSEEvent, ABC):
    def to_sse(self):
        return f"retry: 10000000\n\nevent: end\n\n"


class TCResultsDownloader(webdriver.Chrome):
    """
    This class is used to scrape the data from the TC Results website.
    """
    def __init__(self, url: str):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--log-level=3")  # suppress INFO and WARNING
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        super().__init__(options=options)
        self.url_base = ""
        self.active_board_nr: int | None = None
        self.board_numbers = []
        self.board_data = {}

        self.initialize(url)

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()

    def get_url_tail(self, board_number: int) -> str:
        """
        This method returns the URL tail for the given board number.
        """
        return f"#000000RB000000000{board_number:03d}000001000001000000000000000000"

    def initialize(self, url: str):
        """
        This method prepares the driver by loading the main page and
        extracting the board numbers.
        """
        self.url_base = self.prepare_url(url)
        try:
            self.get(self.url_base)
            time.sleep(0.5)
        except:
            raise TimeoutException()
        self.board_numbers = self.execute_script("return settings.BoardsNumbers")

    def prepare_url(self, url: str):
        if '#' in url:
            url = url[:url.index('#')]
        if not url.endswith("/") or not url.endswith(".html"):
            url += "/"
        return url

    def set_active_board(self, board_number):
        """
        This method sets the active board number.
        """
        url = self.url_base + self.get_url_tail(board_number)
        print(f"GET: {url}")
        self.get(url)
        # hehe
        time.sleep(0.5)
        # TODO improve waiting maybe sth like that
        # try:
        #     WebDriverWait(driver, 30).until(
        #         lambda d: d.execute_script("return document.readyState") == "complete"
        #     )
        # except TimeoutException as err:
        #     raise TimeoutError("Page not loaded") from err
        self.active_board_nr = board_number

    def get_true_board_number(self) -> int:
        element = self.find_element(By.ID, "tabB_bTitle0")
        html_content = element.get_attribute("innerHTML")
        match = re.match(r'<h1 class="mb-0"> *([0-9]*) *</h1>', html_content)
        return int(match.groups()[0])

    def get_cards(self, span_name) -> Hand:
        """
        This method extracts the cards from the given span element.
        """
        try:
            element = self.find_element(By.ID, span_name)
            html_content = element.get_attribute("innerHTML")

            spades, hearts, diamonds, clubs = "", "", "", ""
            spades_length, hearts_length, diamonds_length = 0, 0, 0

            if 'spades.gif' in html_content:
                spades, spades_length = self.extract_cards(html_content, 'spades.gif', -1)
            if 'hearts.gif' in html_content:
                hearts, hearts_length = self.extract_cards(html_content, 'hearts.gif', -1)
            if 'diamonds.gif' in html_content:
                diamonds, diamonds_length = self.extract_cards(html_content, 'diamonds.gif', -1)
            if 'clubs.gif' in html_content:
                clubs, _clubs_length = self.extract_cards(html_content, 'clubs.gif', \
                    13 - (spades_length + hearts_length + diamonds_length))

            return Hand(spades, hearts, diamonds, clubs)

        except (TimeoutException, NoSuchElementException):
            raise TimeoutException()

    def extract_cards(self, html_content, suit_img, suit_length):
        """
        This method extracts the card string that follows the suit image (gif).
        """
        suit_index = html_content.index(suit_img)

        card_start = html_content.find('>', suit_index) + 1
        card_end = (html_content.find('<', card_start) if suit_length == \
                    -1 else card_start + suit_length + 1)
        result = html_content[card_start:card_end].strip()

        result = result.replace('10', 'T')
        result = result.replace('1', 'T')
        return result, len(result)

    def load_board(self, board_number: int = 0):
        """
        This method loads the board data for the given board number.
        """
        if board_number != 0:
            self.set_active_board(board_number)

        hands = []
        for span_name in ("tabB_nCards0", "tabB_eCards0", "tabB_sCards0", "tabB_wCards0"):
            hands.append(self.get_cards(span_name))

        true_number = self.get_true_board_number()
        # pylint: disable=E1120
        board = BoardData(self.active_board_nr, true_number, *hands)
        self.board_data[self.active_board_nr] = board

        true_number_str = '' if self.active_board_nr == true_number else f'({true_number})'
        print(f"Loaded board #{self.active_board_nr}{true_number_str}:")
        # print(str(board))
        return BoardLoadedEvent(
            tournament_seqnence_number=self.active_board_nr, 
            board_number=true_number_str, 
            total_boards=-1, 
            sequence_number=-1,
            board_content=str(board))
    

class TCResultsDriver:
    class TCSession:
        url: str
        boards: str
        creation_date: int
        file_types: FileTypes

        def __init__(self, tc_dto: DownloadTcDTO):
            self.url = tc_dto.url
            self.boards = tc_dto.boards
            self.creation_date = time.time()
            self.file_types = tc_dto.file_types


    class DriverError(Exception):
        message: str
        def __init__(self, message, *args):
            super().__init__(*args)
            self.message = message
        

    output_dir = Path(__file__).parent.parent.resolve() / "temp"
    _sessions: dict[str, TCSession] = {}

    def create_session(self, download_dto: DownloadTcDTO):
        id = hex(random.getrandbits(16))[2:]
        self._sessions[id] = self.TCSession(download_dto)
        return id

    def clear_sessions(self):
        now = time.time()
        for id in self._sessions.keys():
            if now - self._sessions[id].creation_date >= 5 * 60:
                self._sessions.pop(id, None)

    def resolve_boards(self, boards_str) -> list[int]:
        try:
            if boards_str == '' or boards_str == '0':
                return []

            boards = []
            for part in boards_str.split(","):
                token = part.strip()
                if not "-" in token:
                    boards.append(int(token))
                    continue
                l, r = token.split("-")
                boards.extend(list(range(int(l), int(r) + 1)))
            return boards

        except ValueError:
            raise self.DriverError("Nieprawidłowy format podanych rozdań.")

    def download_boards(self, session_id: str) -> Generator[str, None, None]:
        try: 
            if session_id not in self._sessions.keys():
                raise self.DriverError("Nieprawidłowe ID sesji")

            session = self._sessions[session_id]
            boards = self.resolve_boards(session.boards)

            with TCResultsDownloader(session.url) as downloader:
                for e in self._download_boards(session_id, downloader, boards):
                    yield e.to_sse()

        except self.DriverError as err:
            yield ErrorEvent(message=err.message).to_sse()
            yield CloseEvent().to_sse()
        except (JavascriptException, TimeoutException):
            yield ErrorEvent(message="Nieprawidłowy link.").to_sse()
            yield CloseEvent().to_sse()
        finally:
            self._sessions.pop(session_id, None)
            try:
                if downloader is not None:
                    downloader.quit()
            except Exception:
                pass


    def _download_boards(self, session_id: str, downloader: TCResultsDownloader, boards: list[int]) -> Generator[str, None, None]:
        if session_id not in self._sessions.keys():
            raise self.DriverError("Nieprawidłowe ID sesji")

        session = self._sessions[session_id]
        boards = self.resolve_boards(session.boards)

        with TCResultsDownloader(session.url) as downloader:
            if len(boards) == 0:
                boards = downloader.board_numbers
                if len(boards) > 50:
                    raise self.DriverError("Turniej ma więcej niż 50 rozdań. Jeśli na pewno chcesz pobrać je wszystkie, podaj ich dokładne numery.")
            
            if set(boards).isdisjoint(set(downloader.board_numbers)):
                raise self.DriverError("Żadne z rozdań o podanych numerach nie istnieje w tym turnieju. \n"
                "W przypadku turnieju wieloetapowego wklej link razem z numerem etapu.")

            for i, board in enumerate(boards):
                if board not in downloader.board_numbers:
                    yield ErrorEvent(message=f"Rozdanie {board} nie istnieje w tym turnieju.")
                    continue
                bl_e = downloader.load_board(board)
                bl_e.total_boards = len(boards)
                bl_e.sequence_number = i + 1
                yield bl_e

            if session.file_types.tex:
                yield self.generate_tex_file(session, session_id, downloader.board_data.values())
            time.sleep(0.5)
            if session.file_types.pbn:
                yield self.generate_pbn_file(session, session_id, downloader.board_data.values())
            yield CloseEvent()


    def generate_tex_file(self, session, session_id, board_data):
        if session.file_types.tex:
            name = f"{session_id}.tex"
            TempFileService.TEMP_RWLOCK.acquire_read()
            build_analysis_template(board_data, self.output_dir / name)
            TempFileService.TEMP_RWLOCK.release_read()
            return TcFileReadyEvent(session_id=session_id, file_type="tex")
            
    def generate_pbn_file(self, session, session_id, board_data):
        if session.file_types.pbn:
            name = f"{session_id}.pbn"
            TempFileService.TEMP_RWLOCK.acquire_read()
            build_pbn(board_data, self.output_dir / name)
            TempFileService.TEMP_RWLOCK.release_read()
            return TcFileReadyEvent(session_id=session_id, file_type="pbn")


        
            

