# Add 'simple' tags

This program goes through .exb files in the input/ folder, and adds the tag 'simple' to empty ref-mod cells with corresponding ref-form cells.
Check the files in the input/ and output/ folders for examples.

## Structure

The program starts at the bottom of `simple_tag.py`, at the line `if __name__ == '__main__':`
From there, you can follow the function calls and the comments to see how the program works.

Especially interesting is the util.py file, and the `Cell` object.
The `Cell` object just has a few attributes of the exmaralda cells, and it's what the util.py functions usually return.
If you want to go through the cells in a certain tier, you can just call `util.cells_in_tier`, and look through the list it returns, or save a couple lists of cells in an .exb file.

While this program gives an example of going through the ref-form and ref-mod tiers, it edits the .exb files, which you don't want to do,
and it doesn't write the cells to a .csv file, which you might want to.
For the .csv file, you can check the other program's repository.
