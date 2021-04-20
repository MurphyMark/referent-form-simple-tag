import bisect
from pathlib import Path
from typing import List, Optional, Tuple, Union

from bs4 import BeautifulSoup, Tag


# I wouldn't bother with the code in these functions, just what they do.

class Cell:
    tier: str
    start: int
    end: int
    value: str

    def get_previous(self, tier: List['Cell']) -> Optional['Cell']:
        idx = tier.index(self)
        try:
            return tier[idx - 1]
        except IndexError:
            return None

    def get_next(self, tier: List['Cell']) -> Optional['Cell']:
        idx = tier.index(self)
        try:
            return tier[idx + 1]
        except IndexError:
            return None

    def as_tag(self) -> Tag:
        tag = Tag(name='event',
                  attrs={'start': 'T' + str(self.start),
                         'end': 'T' + str(self.end)})
        tag.append(self.value)
        return tag

    def __init__(self, tier: str, start: int, end: int, value: str):
        self.tier = tier
        self.start = start
        self.end = end
        self.value = value

    def __lt__(self, other):
        return max(self.start, self.end) < min(other.start, other.end)


# Find all the .exb files in the given folder
def exb_in(directory: Path) -> [Path]:
    return [p for p in directory.glob('**/*.exb')]


# Check if a soup object has a certain tier -- `ref-mod1` or `ref-form3` for example
def has_tier(soup: BeautifulSoup, tier: str) -> bool:
    return soup.find('tier', category=tier) is not None


# Get a list of Cell objects with all the cells in the tier.
# These are easier to look through than the soup object.
def cells_in_tier(soup: BeautifulSoup, tier: str) -> List[Cell]:
    soup_tier = soup.find('tier', category=tier)
    soup_tier = list(soup_tier.children)
    cells: [Cell] = list()

    # Tier to cells
    for soup_cell in soup_tier:
        if isinstance(soup_cell, Tag):
            # 'T20' -> 20
            def cell_position_int(position: str) -> int:
                return int(position[1:])

            start = cell_position_int(soup_cell.attrs['start'])
            end = cell_position_int(soup_cell.attrs['end'])
            value = soup_cell.text

            cell = Cell(tier, start, end, value)
            cells.append(cell)

    return cells


# Find all the cells on one tier that are inside a specific cell on another tier.
# If you have:
#
# ref-form1         | a1             | a2          |
# ref-mod1          | b1 | b2  | b3  | b4    |
#
# calling cells_within_cell(a1, ref-mod1) would give a list of:
# b1, b2, and b3
def cells_within_cell(cell: Cell, search_tier: List[Cell]) -> List[Cell]:
    return [search_cell for search_cell in search_tier
            if search_cell.start >= cell.start
            and search_cell.end <= cell.end]


# If you have:
#
# ref-form1             | a1             | a2          |
# ref-mod1          | b1     | b2  | b3        | b4    |
#
# cells_intersecting_with_cell(a1, ref-mod1) would give:
# b1, b2, and b3
def cells_intersecting_with_cell(cell: Cell, search_tier: List[Cell]) -> List[Cell]:
    return [search_cell for search_cell in search_tier
            if cell.start <= search_cell.start <= cell.end
            or cell.start <= search_cell.end <= cell.end
            or search_cell.start <= cell.start <= search_cell.end
            or search_cell.start <= cell.end <= search_cell.end]


# If you have:
#
# ref-form1             | a1             | a2          |
# ref-mod1          | b1     | b2  | b3        | b4    |
#
# cells_surrounding_cell(b2, ref-form1) would give a1,
# but cells_surrounding_cell(b3, ref-form1) would give an empty list
def cells_surrounding_cells(cell: Cell, search_tier: List[Cell]) -> List[Cell]:
    surrounding_cells = list()
    for search_cell in search_tier:
        if search_cell.start <= cell.start <= search_cell.end:
            surrounding_cells.append(search_cell)
            break
        if (cell.start <= search_cell.start
                and search_cell.end <= cell.end):
            surrounding_cells.append(search_cell)
            break
        if search_cell.start <= cell.end <= search_cell.end:
            surrounding_cells.append(search_cell)
            break
    return surrounding_cells


# If you have:
#
# ref-form1         | a1 | a2 | a3 |
#
# neighboring_cells(a2, ref-form1) gives a1 and a3
def neighboring_cells(cell: Cell, cells: List[Cell]) -> Tuple[Cell, Cell]:
    bisect.insort_left(cells, cell)
    cell_idx = cells.index(cell)

    if cell_idx == 0:
        previous_neighbor = None
    else:
        previous_neighbor = cells[cell_idx - 1]

    if cell_idx == len(cells) - 1:
        next_neighbor = None
    else:
        next_neighbor = cells[cell_idx + 1]

    return previous_neighbor, next_neighbor


# Ignore this unless you're trying to work on the soup object directly.
# If you're doing that, lemme know and I can try and help.
def find_cell_child(tier: BeautifulSoup, cell: Cell) -> Union[Tag, None]:

    child_tags = tier.children

    for child in child_tags:
        if isinstance(child, Tag):
            attrs = child.attrs

            def cell_position_int(position: str) -> int:
                return int(position[1:])

            start_attr = cell_position_int(attrs['start'])
            end_attr = cell_position_int(attrs['end'])
            value_attr = child.text

            if (start_attr == cell.start and
                    end_attr == cell.end and
                    value_attr == cell.value):
                return child


# Use this if you want to write a new .exb file with additional cells added.
# Otherwise, don't.
def add_cell(soup: BeautifulSoup, cell: Cell):
    soup_tier = soup.find('tier', category=cell.tier)
    tier_cells = cells_in_tier(soup, cell.tier)

    previous_neighbor, next_neighbor = neighboring_cells(cell, tier_cells)

    if previous_neighbor is not None:
        previous_neighbor_tag = find_cell_child(soup_tier, previous_neighbor)
        previous_neighbor_tag.insert_after(cell.as_tag())

    elif next_neighbor is not None:
        next_neighbor_tag = find_cell_child(soup_tier, next_neighbor)
        next_neighbor_tag.insert_before(cell.as_tag())

    else:
        soup_tier.append(cell.as_tag())
