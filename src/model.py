import gurobipy as gp
import math
from concorde.tsp import TSPSolver

solved_bsp = {}


def optimize(data):
    vehicle_capacity = data["C"]
    time_horizon = range(data["H"])
    time_horizon_ = range(data["H"] + 1)
    customers = data["customers"]
    supplier = data["supplier"]

    model = gp.Model()

    B_t = model.addVars(
        [time for time in time_horizon_],
        vtype=gp.GRB.CONTINUOUS,
        name="B_i",
    )

    z_st = model.addVars(
        [customer["index"] for customer in customers],
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

    model.setObjective(
        (
            gp.quicksum(supplier["h_i"] * B_t[time] for time in time_horizon_)
            + gp.quicksum(
                customer["h_i"] * I_st[customer["index"], time]
                for customer in customers
                for time in time_horizon_
            )
            + gp.quicksum(eta_t[time] for time in time_horizon)
        ),
        gp.GRB.MINIMIZE,
    )

    model.addConstr(
        B_t[0] == supplier["B_i"],
        name="initial_supplier_inventory",
    )

    model.addConstrs(
        (
            B_t[time]
            == B_t[time - 1]
            + supplier["r_i"]
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
            - customer_r
            for customer_index, customer_r in [
                [customer["index"], customer["r_i"]] for customer in customers
            ]
            for time in time_horizon[1:]
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

    def get_dist(x_1, y_1, x_2, y_2):
        return math.sqrt((x_1 - x_2)**2 + (y_1 - y_2)**2)

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
                    
                if len(xs) < 2:
                    continue

                elif len(xs) == 2:
                    bsd_cost = 2 * get_dist(xs[0], ys[0], xs[1], ys[1])

                elif len(xs) == 3:
                    bsd_cost = get_dist(xs[0], ys[0], xs[1], ys[1]) + get_dist(xs[1], ys[1], xs[2], ys[2]) + get_dist(xs[2], ys[2], xs[0], ys[0])

                else:
                    tour_hash = '.'.join([str(node) for node in visited])
                    if tour_hash in solved_bsp:
                        continue

                    bsd_solver = TSPSolver.from_data(xs, ys, norm="EUC_2D")
                    bsd_sol = bsd_solver.solve(verbose=False)
                    bsd_cost = bsd_sol.optimal_value

                    solved_bsp[tour_hash] = bsd_sol.tour.tolist()

                if eta < bsd_cost:
                    for _time in time_horizon:
                        model.cbLazy(
                            eta_t[_time]
                            >= bsd_cost * (1 + gp.quicksum(z_st[customer, _time] for customer in visited) - len(visited))
                        )

    model.write("model.lp")
    model.Params.LazyConstraints = 1
    model.optimize(benders_cuts)

    for v in model.getVars():
        print(v.varName, "=", v.x)

    return
