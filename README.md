# SOSR 2018 submission

## External dependencies

 * Octave
 * METIS
 * Boost

## Compiling

 1. Install external dependencies
 2. Clone this repository with `git clone` and `cd` to the root directory
 3. Compile One Big Switch by running:

    ```
    g++ -O2 external/batch_DFS_MP.cpp -o external/batch_DFS_MP
    ```

 4. Prepare python by running `python setup.py develop --user`

## Running

To get the overhead and running time (Figure 2b, 2c, and part of Table 1) run: 

```
python runner.py --algo [algo] [classbench] single --capacity [cap] --length [len]
```

The automated binary search that calculates minimal capacity (Figure 2a and part of Table 1):
```
python runner.py --algo [algo] [classbench] capacity --start [left] --end [right] --step -2 --length [len]
```

Possible values for `[algo]` are **pbd** (pivot-based Palette), **cbd** (cut-based Palette), **obs**, **bm**, and **bit**. Files for `[classbench]` are inside `classbench` directory.
