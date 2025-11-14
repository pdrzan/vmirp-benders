# Branch-and-benders-cut for the Vendor-Managed Inventory Routing Problem


This repository has a implementation of a *branch-and-benders-cut* (B\&BC) algorithm for the Vendor-Managed Inventory Routing Problem (VMIR).

## Repository organization

- `/src`: All the source code of the algorithm.
- `/instances`: Group of VMIR instances proposed by Archetti [^1].
- `/results`: Test resoults of the algorithm. More information [here](./results/README.md).
- `/graphics`: Code for generate performance graphs.

## Running the algorithm

To run this algorithm you have to install [pyconcorde](https://github.com/jvkersch/pyconcorde). After that, install other necessary dependencies executing:

```bash
pip install -r requirements.txt
```

With all dependencies installed, you can execute the algorithm with this command:

```bash
python src/main.py -i <instance-path> -t <time-limit-in-seconds>
```

[^1]: Claudia Archetti, Luca Bertazzi, Gilbert Laporte, Maria Grazia Speranza, (2007) A Branch-and-Cut Algorithm for a Vendor-Managed Inventory-Routing Problem. Transportation Science 41(3):382-391.
https://doi.org/10.1287/trsc.1060.0188