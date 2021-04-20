# simple_tag.py
# Goal: go through the lab rotation annotated files,
# and add a 'simple' tag on any empty ref-mod cell with a corresponding ref-form cell.
# See bak_input/ and bak_output/ folders for examples

from pathlib import Path  # Nice representations of file paths, we use it to go through the files
from typing import Tuple, List  # Python optional type annotations

from bs4 import BeautifulSoup  # The library we use to parse the HTML-like .exb files

import util  # util.py, in this folder

INPUT_PATH = Path('.', 'input')
OUTPUT_PATH = Path('.', 'output')
INPUT_FILES = sorted(util.exb_in(INPUT_PATH))  # Searches through bak_input/ and finds all .exb files

SIMPLE_CELL_VALUE = 'simple'


def tag_simple(soup: BeautifulSoup, form_tier: str, mod_tier: str):
    # Takes in a form tier and a mod tier,
    # goes through all the matching cells,
    # and adds a 'simple' tag to empty mod cells.

    form_cells = util.cells_in_tier(soup, form_tier)
    mod_cells = util.cells_in_tier(soup, mod_tier)

    # Find ref_form cells with no corresponding ref_mod cell
    for form_cell in form_cells:
        # Get the empty ref-mod cells inside a ref-form cell
        mod_cells_within = util.cells_within_cell(form_cell, mod_cells)

        # Use the attributes of the ref-form cell to make a new ref-mod cell with the correct
        # start and end time, and 'simple' as its value.
        if len(mod_cells_within) == 0:
            simple_start = form_cell.start
            simple_end = form_cell.end
            simple_value = SIMPLE_CELL_VALUE
            # Make a cell object with all the information we want
            simple_cell = util.Cell(mod_tier, simple_start, simple_end, simple_value)

            # Call the util.py function to add the Cell object into the parsed soup structure.
            util.add_cell(soup, simple_cell)


def tag_simple_all_tiers(path: Path, soup: BeautifulSoup):
    # Go through the tiers in the file,
    # find all the pairs of (ref-formN, ref-modN),
    # And add a 'simple' tag to the empty ref-mod cells.

    # Check that the file has `ref-form1`
    if not util.has_tier(soup, 'ref-form1'):
        print(path.as_posix() + ': Missing tier `ref-form1`')
        return
    
    # Create pairs of `ref-formN` and `ref-modN` tiers
    tier_pairs: List[Tuple[str, str]] = []
    tier_n = 1

    def has_both_tiers(n):
        form_tier = 'ref-form' + str(n)
        mod_tier = 'ref-mod' + str(n)
        # There shouldn't be a tier `ref-form2` without a `ref-mod2`
        if util.has_tier(soup, form_tier) and not util.has_tier(soup, mod_tier):
            print(path.as_posix() + ': Missing tier `ref-mod' + str(n) + '`')
        return util.has_tier(soup, form_tier) and util.has_tier(soup, mod_tier)

    while has_both_tiers(tier_n):
        form_tier = 'ref-form' + str(tier_n)
        mod_tier = 'ref-mod' + str(tier_n)

        tier_pairs.append((form_tier, mod_tier))
        tier_n += 1

    # Add simple tags to each mod tier
    for form_tier, mod_tier in tier_pairs:
        tag_simple(soup, form_tier, mod_tier)
    pass


def write_file(file_name: str, soup: BeautifulSoup):
    # Write an bak_output/ file with the added 'simple' cells.

    output_file_path = OUTPUT_PATH.joinpath(file_name)
    with output_file_path.open(encoding='utf-8', mode='w') as output_file:
        soup_text = str(soup)  # Turn the soup object into a text file
        output_file.write(soup_text)  # Write it


if __name__ == '__main__':
    tag_files = list()
    for file_path in INPUT_FILES:  # Go through all the bak_input files
        with file_path.open(encoding='utf-8') as file:  # encoding='utf-8' is so it doesn't break on certain .exb files
            file_soup = BeautifulSoup(file, features='html.parser')  # Parse an .exb file
            tag_simple_all_tiers(file_path, file_soup)
            write_file(file_path.name, file_soup)
