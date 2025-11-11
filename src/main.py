import sys
from instance import read_instance
from model import optimize


def main():
    description = (
        "This program resolves the VM-IRP problem with benders "
        "decomposition. To run, you have to pass the following "
        "arguments: "
        "- '-i': File path of the VM-IRP instance"
        "- '-t': Gurobi time limit (seconds)"
        "\n"
        "Example:\n"
        "src/main.py -i instances/Instances_highcost_H3/abs1n10.dat -t 30\n"
    )

    arguments = {"-i": None, "-t": None}

    for index_argument, argument in enumerate(sys.argv):
        if argument in arguments and index_argument + 1 < len(sys.argv):
            arguments[argument] = sys.argv[index_argument + 1]

    for value in arguments.values():
        if value is None:
            raise Exception("Parameters not defined!\n" + description)

    instance_file_path = arguments["-i"]
    time_limit = float(arguments["-t"])
    data = read_instance(instance_file_path)
    result = optimize(data, time_limit)
    print(";".join([f"{x:.4f}" for x in result]))


if __name__ == "__main__":
    main()
