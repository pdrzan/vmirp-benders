import os


def read_instance(file_path):
    print(f"Reading instance {os.path.basename(file_path)}")

    data = {"supplier": {}, "customers": []}

    with open(file_path) as file:
        file.readline()

        data["n"], data["H"], data["C"] = map(int, file.readline().split())

        index, x, y, B_1, r_1, h_1 = file.readline().split()
        data["supplier"]["index"] = int(index)
        data["supplier"]["x"] = float(x)
        data["supplier"]["y"] = float(y)
        data["supplier"]["B_1"] = int(B_1)
        data["supplier"]["r_1"] = int(r_1)
        data["supplier"]["h_1"] = float(h_1)

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

    return data
