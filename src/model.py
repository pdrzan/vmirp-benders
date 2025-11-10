import gurobipy as gp
import math
from concorde.tsp import TSPSolver

solved_bsp = {}
solved_list = []


def optimize(data):
    vehicle_capacity = data["C"]
    time_horizon = range(data["H"] + 1)
    time_horizon_ = range(data["H"] + 2)
    customers = data["customers"]
    supplier = data["supplier"]

    nodes = [1] + [customer["index"] for customer in customers]

    def get_dist(x_1, y_1, x_2, y_2):
        return math.sqrt((x_1 - x_2)**2 + (y_1 - y_2)**2)

    dist = [[0 for _ in range(len(customers)+1)] for _ in range(len(customers)+1)]

    for i in range(len(customers)):
        dist[i+1][0] = int(get_dist(supplier["x"], supplier["y"], customers[i]["x"], customers[i]["y"]))
        dist[0][i+1] = dist[i+1][0]
    
    for i in range(len(customers)):
        for j in range(len(customers)):
            dist[i+1][j+1] = int(get_dist(customers[i]["x"], customers[i]["y"], customers[j]["x"], customers[j]["y"]))
            dist[j+1][i+1] = dist[i+1][j+1]

    model = gp.Model()
    model.Params.LazyConstraints = 1
    model.Params.Threads = 1
    model.Params.TimeLimit = 30 * 60

    B_t = model.addVars(
        [time for time in time_horizon_],
        vtype=gp.GRB.CONTINUOUS,
        name="B_i",
    )

    z_st = model.addVars(
        nodes,
        [time for time in time_horizon],
        vtype=gp.GRB.BINARY,
        name="z_st",
    )

    x_st = model.addVars(
        [customer["index"] for customer in customers],
        [time for time in time_horizon_],
        vtype=gp.GRB.CONTINUOUS,
        name="x_st",
    )

    I_st = model.addVars(
        [customer["index"] for customer in customers],
        [time for time in time_horizon_],
        vtype=gp.GRB.CONTINUOUS,
        name="I_st",
    )

    eta_t = model.addVars(
        [time for time in time_horizon],
        vtype=gp.GRB.CONTINUOUS,
        name="eta_t",
    )

    v_ijt = model.addVars(
        nodes,
        nodes,
        [time for time in time_horizon],
        vtype=gp.GRB.CONTINUOUS,
        name="v_ijt",
    )

    u_it = model.addVars(
        [customer["index"] for customer in customers],
        [time for time in time_horizon],
        vtype=gp.GRB.CONTINUOUS,
        name="u_it",
    )

    model.setObjective(
        (
            gp.quicksum(supplier["h_i"] * B_t[time] for time in time_horizon_[1:])
            + gp.quicksum(
                customer["h_i"] * I_st[customer["index"], time]
                for customer in customers
                for time in time_horizon_[1:]
            )
            + gp.quicksum(eta_t[time] for time in time_horizon)
        ),
        gp.GRB.MINIMIZE,
    )

    model.addConstr(
        B_t[0] == supplier["B_i"],
        name="initial_supplier_inventory",
    )

    model.addConstr(
        (
            gp.quicksum(x_st[customer["index"], 0] for customer in customers)
            == 0
        ),
        name="initial_deliveries",
    )

    model.addConstr(
        (
            gp.quicksum(z_st[customer["index"], 0] for customer in customers)
            == 0
        ),
        name="initial_visits",
    )

    model.addConstrs(
        (
            z_st[1, time]
            >= z_st[customer_index, time]
            for customer_index in [customer["index"] for customer in customers]
            for time in time_horizon 
        ),
        name="supplier_moviments",
    )

    model.addConstrs(
        (
            B_t[time]
            == B_t[time - 1]
            + (supplier["r_i"] if time > 1 else 0)
            - gp.quicksum(x_st[customer["index"], time - 1] for customer in customers)
            for time in time_horizon_[1:]
        ),
        name="supplier_inventory",
    )

    model.addConstrs(
        (
            B_t[time]
            >= gp.quicksum(x_st[customer["index"], time] for customer in customers)
            for time in time_horizon
        ),
        name="inventory_for_delivery",
    )

    model.addConstrs(
        (
            I_st[customer_index, 0] == customer_initial_inventory
            for customer_index, customer_initial_inventory in [
                [customer["index"], customer["I_i"]] for customer in customers
            ]
        ),
        name="initial_customer_inventory",
    )

    model.addConstrs(
        (
            I_st[customer_index, time]
            == I_st[customer_index, time - 1]
            + x_st[customer_index, time - 1]
            - (customer_r if time > 1 else 0)
            for customer_index, customer_r in [
                [customer["index"], customer["r_i"]] for customer in customers
            ]
            for time in time_horizon_[1:]
        ),
        name="customer_inventory",
    )

    model.addConstrs(
        (
            I_st[customer_index, time] >= 0
            for customer_index in [customer["index"] for customer in customers]
            for time in time_horizon_
        ),
        name="inventory_for_delivery",
    )

    model.addConstrs(
        (
            x_st[customer_index, time]
            >= customer_max_inventory * z_st[customer_index, time]
            - I_st[customer_index, time]
            for customer_index, customer_max_inventory in [
                [customer["index"], customer["U_i"]] for customer in customers
            ]
            for time in time_horizon
        ),
        name="min_quantity_delivered_customer",
    )

    model.addConstrs(
        (
            x_st[customer_index, time]
            <= customer_max_inventory - I_st[customer_index, time]
            for customer_index, customer_max_inventory in [
                [customer["index"], customer["U_i"]] for customer in customers
            ]
            for time in time_horizon
        ),
        name="max_quantity_delivered_customer_1",
    )

    model.addConstrs(
        (
            x_st[customer_index, time]
            <= customer_max_inventory * z_st[customer_index, time]
            for customer_index, customer_max_inventory in [
                [customer["index"], customer["U_i"]] for customer in customers
            ]
            for time in time_horizon
        ),
        name="max_quantity_delivered_customer_2",
    )

    model.addConstrs(
        (
            gp.quicksum(x_st[customer["index"], time] for customer in customers)
            <= vehicle_capacity
            for time in time_horizon
        ),
        name="vehicle_capacity",
    )

    model.addConstrs(
        (
            gp.quicksum(v_ijt[i, j, time] for j in nodes)
            == z_st[i, time]
            for i in nodes
            for time in time_horizon
        ),
        name="a",
    )

    model.addConstrs(
        (
            gp.quicksum(v_ijt[i, j, time] for i in nodes)
            == z_st[j, time]
            for j in nodes
            for time in time_horizon
        ),
        name="b",
    )

    model.addConstrs(
        (
            u_it[customer_index, time]
            >= 2 * z_st[customer_index, time]
            for customer_index in [customer["index"] for customer in customers]
            for time in time_horizon
        ),
        name="c",
    )

    model.addConstrs(
        (
            u_it[customer_index, time] <= gp.quicksum(z_st[i, time] for i in nodes)
            for customer_index in [customer["index"] for customer in customers]
            for time in time_horizon
        ),
        name="d",
    )

    model.addConstrs(
        (
            u_it[i, time] - u_it[j, time] + 1
            <= (len(customers) + 1) * (1 - v_ijt[i, j, time])
            for i in [customer["index"] for customer in customers]
            for j in [customer["index"] for customer in customers]
            for time in time_horizon
        ),
        name="a",
    )

    model.addConstrs(
        (
            eta_t[time]
            >= gp.quicksum(
                dist[i-1][j-1]
                * v_ijt[i, j, time]
                for i in nodes
                for j in nodes if i!=j)
            for time in time_horizon
        ),
        name="e",
    )

    def benders_cuts(model, where):
        if where == gp.GRB.Callback.MIPSOL:
            for time in time_horizon:
                xs = [supplier["x"]]
                ys = [supplier["y"]]
                visited = []
                eta = model.cbGetSolution(eta_t[time])
                variables = []
                for customer in customers:
                    if model.cbGetSolution(z_st[customer["index"], time]) > 0.99:
                        xs += [customer["x"]]
                        ys += [customer["y"]]
                        visited += [customer["index"]]
                        variables += [z_st[customer["index"], time]]
                

                tour_hash = '.'.join([str(node) for node in visited])
                if tour_hash in solved_bsp:
                    bsd_cost = solved_bsp[tour_hash]

                elif len(xs) < 2:
                    continue

                elif len(xs) == 2:
                    bsd_cost = 2 * get_dist(xs[0], ys[0], xs[1], ys[1])

                elif len(xs) == 3:
                    bsd_cost = get_dist(xs[0], ys[0], xs[1], ys[1]) + get_dist(xs[1], ys[1], xs[2], ys[2]) + get_dist(xs[2], ys[2], xs[0], ys[0])

                else:
                    if tour_hash in solved_bsp:
                        continue

                    bsd_solver = TSPSolver.from_data(xs, ys, norm="EUC_2D")
                    bsd_sol = bsd_solver.solve(verbose=False)
                    bsd_cost = bsd_sol.optimal_value

                    solved_bsp[tour_hash] = bsd_cost
                    solved_list.append(tour_hash)
                    if len(solved_list) > 10000:
                        removed_sol = solved_list.pop(0)
                        del solved_bsp[removed_sol]

                if eta < bsd_cost:
                    for _time in time_horizon:
                        model.cbLazy(
                            eta_t[_time]
                            # >= bsd_cost
                            # * (1 + gp.quicksum(z_st[customer, _time] for customer in visited) - len(visited))
                            >= bsd_cost * z_st[1, _time]
                            - gp.quicksum(
                                2
                                * max([dist[customer-1][i-1] for i in (visited + [1])])
                                * (1 - z_st[customer, _time])
                                for customer in visited
                                )
                        )

    model.write("model.lp")
    model.optimize(benders_cuts)

    # for v in model.getVars():
    #     print(v.varName, "=", v.x)

    return
