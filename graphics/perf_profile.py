import pandas as pd

results_list = [
    'lowcost_H3',
    'lowcost_H6',
    'highcost_H3',
    'highcost_H6'
]

archetti_rename_dict = {
    'Instance': 'instance',
    'CPU': 'time',
    'z*': 'LB'
}


def main():
    perf_profile_txt = ""
    df_total = pd.DataFrame()
    for result in results_list:
        file = f"results/{result}.csv"
        df_bbc = pd.read_csv(file, sep=";")
        df_bbc = df_bbc[['instance', 'time', 'LB', 'gap']]
        df_bbc["method"] = "B&BC"
        df_archetti = pd.read_excel(f"results/Results_{result}.xls", sheet_name='Foglio1').rename(columns=archetti_rename_dict)
        df_archetti["gap"] = 0
        df_archetti["method"] = "Archetti et al."

        df = pd.concat([df_bbc, df_archetti])

        df["time"] = df.apply(lambda row: max(row["time"], 0.01), axis=1)

        df["count"] = 1
        mask = (
            df
            .groupby(["instance"])
            .agg({
                'count': 'sum',
                'time': 'min'
            })
            .reset_index()
            .query("count == 2")
            .rename(columns={'time': 'min_time'})
            [["instance", "min_time"]]
        )

        df = df.merge(mask)

        df["instance"] = result + df["instance"]

        df["tau"] = df["time"] / df["min_time"]
        max_tau = df["tau"].max()

        df["tau"] = df.apply(lambda row: row["tau"] if row["gap"] < 0.001 else max_tau + 1, axis=1)

        df = df[df["tau"] <= max_tau]

        df_total = pd.concat([df, df_total])
    
    
    instances = df_total[["instance"]].drop_duplicates().count()

    df_total = df_total.sort_values(["tau"])
    df_total["perc"] = float(1 / (instances))
    df_total["perf_profile"] = df_total.groupby("method")["perc"].cumsum()

    df_total = (
        df_total
        .groupby(["tau", "method"])
        ["perf_profile"].max()
        .reset_index()
    )
    
    for method in df_total["method"].unique():
        df = df_total[df_total["method"] == method]
        perf_profile_txt += method + ":\n"
        df["plot"] = df.apply(lambda row: f"({row["tau"]},{row["perf_profile"]})", axis=1)
        perf_profile_txt += df["plot"].sum() + "\n\n"
    
    print(perf_profile_txt)
        






if __name__ == "__main__":
    main()