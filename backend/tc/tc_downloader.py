"""
This module is used to scrape the bridge hands from the TC Results website
and generate a LaTeX file with the hand diagrams.
"""

import re
import time
import random
import json
from pydantic import BaseModel
from dataclasses import dataclass
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

from .models import Hand, BoardData
from .bridgetex import build_analysis_template


class BoardLoadedEvent(BaseModel):
    sequence_number: int
    board_number: str
    total_boards: int
    board_content: str = ""

    def to_sse(self):
        return f"event: boardLoaded\ndata: {self.model_dump_json()}\n\n"

class TcFileReadyEvent(BaseModel):
    id: str 

    def to_sse(self):
        return f"event: tcFileReady\ndata: {self.model_dump_json()}\n\n"
    
class ErrorEvent(BaseModel):
    message: str   

    def to_sse(self):
        return f"event: error\ndata: {self.model_dump_json()}\n\n"


class TCResultsDownloader(webdriver.Chrome):
    """
    This class is used to scrape the data from the TC Results website.
    """
    def __init__(self, url: str):
        options = Options()
        options.add_argument("--headless=new")
        super().__init__(options=options)
        self.url_base = ""
        self.active_board_nr: int | None = None
        self.board_numbers = []
        self.board_data = {}

        self.initialize(url)

    def get_url_tail(self, board_number: int) -> str:
        """
        This method returns the URL tail for the given board number.
        """
        return f"#000000RB0000000000{board_number:02d}000001000001000000000000000000"

    def initialize(self, url_base: str):
        """
        This method prepares the driver by loading the main page and
        extracting the board numbers.
        """
        self.url_base = url_base
        self.get(self.url_base)
        time.sleep(0.5)
        self.board_numbers = self.execute_script("return settings.BoardsNumbers")

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

        except TimeoutException:
            print(f"Error loading element: {span_name}")
            return Hand("", "", "", "")

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
        print(str(board))
        return BoardLoadedEvent(
            sequence_number=self.active_board_nr, 
            board_number=true_number_str, 
            total_boards=-1, 
            board_content=str(board))

    # pylint: disable=E0202
    def board_numbers(self):
        """
        This method returns an iterator for the board numbers.
        """
        for m in self.board_numbers:
            yield m
            

class TCResultsDriver:
    def __init__(self):
        self.output_dir = Path(__file__).parent.parent.resolve() / "temp"

    def download_boards(self, url, boards):
        driver = TCResultsDownloader(url)
        # try:
        if len(boards) == 0:
            boards = driver.board_numbers

        for board in boards:
            bl_e = driver.load_board(board)
            bl_e.total_boards = len(boards)
            yield bl_e.to_sse()

        id = hex(random.getrandbits(16))[2:]
        name = f"analysis_{id}.tex"
        build_analysis_template(driver.board_data.values(), self.output_dir / name)
        yield TcFileReadyEvent(id=id).to_sse()
        
        # except Exception as ex:
        #     yield ErrorEvent(f"{ex}").to_sse()
        #     raise ex from None
            

