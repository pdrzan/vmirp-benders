import sys
from os.path import isfile
from instance import read_instance
from model import optimize
from pathlib import Path
import re


def main():
    description = """
    This programs runs a benders decomposition algorithm for the VM-IRP.
    The tests are run in mass from the instances placed within the folder
    'instances' and the results are saved within the folder 'results'.
    arguments:
        '-t' time
    """

    arguments = {"-t": None}


    for index_argument, argument in enumerate(sys.argv):
        if argument in arguments and index_argument + 1 < len(sys.argv):
            arguments[argument] = sys.argv[index_argument + 1]

    for value in arguments.values():
        if value is None:
            raise Exception("Parameters not defined!\n" + description)
        
    time_limit = float(arguments["-t"])

    target = Path("instances/")

    folders = []
    for item in target.iterdir():
        if item.is_dir():
                folders.append(item.name)

    sizes = [5*i for i in range(1,11)]
    for size in sizes:
         for folder in folders:
              for i in range(1,6):
                    file = f"instances/{folder}/abs{i}n{size}.dat"
                    if isfile(file):
                        data = read_instance(file)
                        result = optimize(data, time_limit)
                        with open(f"results/{folder}/abs{i}n{size}.out", 'w') as f:
                            f.write(";".join([file] + [f"{x:.4f}" for x in result]))


if __name__ == "__main__":
    main()
