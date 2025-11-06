import os
import math


def distance_between(x_i, x_j, y_i, y_j):
    return round(math.sqrt((x_i - x_j) ** 2 + (y_i - y_j) ** 2))


def read_instance(file_path):
    print(f"Reading instance {os.path.basename(file_path)}")

    data = {"supplier": {}, "customers": []}

    with open(file_path) as file:
        file.readline()

        data["n"], data["H"], data["C"] = map(int, file.readline().split())

        index, x, y, B_0, r_0, h_0 = file.readline().split()
        data["supplier"]["index"] = int(index)
        data["supplier"]["x"] = float(x)
        data["supplier"]["y"] = float(y)
        data["supplier"]["B_0"] = int(B_0)
        data["supplier"]["r_0"] = int(r_0)
        data["supplier"]["h_0"] = float(h_0)

        for _ in range(data["n"] - 1):
            index, x, y, I_i0, U_i, L_i, r_i, h_i = file.readline().split()
            data["customers"].append(
                {
                    "index": int(index),
                    "x": float(x),
                    "y": float(y),
                    "I_i0": int(I_i0),
                    "U_i": int(U_i),
                    "L_i": int(L_i),
                    "r_i": int(r_i),
                    "h_i": float(h_i),
                }
            )

        data["distance_matrix"] = []

        for customer_i in [data["supplier"]] + data["customers"]:
            distance_row = []

            for customer_j in [data["supplier"]] + data["customers"]:
                distance_row.append(
                    distance_between(
                        customer_i["x"],
                        customer_j["x"],
                        customer_i["y"],
                        customer_j["y"],
                    )
                )

            data["distance_matrix"].append(distance_row)

    return data
