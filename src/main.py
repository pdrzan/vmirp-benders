import sys
from instance import read_instance


def main():
    description = (
        "This program resolves the VM-IRP problem with benders "
        "decomposition. To run, you have to pass the following "
        "arguments: "
        "- '-i': File path of the VM-IRP instance"
        "\n"
        "Example:\n"
        "src/main.py -i instances/Instances_highcost_H3/abs1n10.dat\n"
    )

    arguments = {"-i": None}

    for index_argument, argument in enumerate(sys.argv):
        if argument in arguments and index_argument + 1 < len(sys.argv):
            arguments[argument] = sys.argv[index_argument + 1]

    for value in arguments.values():
        if value is None:
            raise Exception("Parameters not defined!\n" + description)

    instance_file_path = arguments["-i"]
    data = read_instance(instance_file_path)


if __name__ == "__main__":
    main()
