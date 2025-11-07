import gurobipy as gp


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
        vtype=gp.GRB.CONTINUOUS,
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

    model.write("model.lp")
    model.optimize()

    return
