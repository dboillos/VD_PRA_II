import pandas as pd
import argparse

# --------------------------------------------------
# Argumentos
# --------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument(
    "--input",
    required=True,
    help="CSV original del CDC"
)
parser.add_argument(
    "--year",
    type=int,
    default=2018,
    help="Año para las visualizaciones por raza"
)
parser.add_argument(
    "--race-sex",
    default="Male",
    help="Sexo para la visualización por raza (Male/Female)"
)

args = parser.parse_args()

print(">>> SCRIPT EJECUTÁNDOSE <<<")

# --------------------------------------------------
# Cargar datos
# --------------------------------------------------
df = pd.read_csv(args.input)

# ==================================================
# 1) Evolución temporal total
# ==================================================

# No hace falta reconstruir el formato
trend_total = df[
    (df["STUB_NAME"] == "Total")
    & (df["STUB_LABEL"] == "All persons")
    & (df["AGE"] == "All ages")
][["YEAR", "ESTIMATE"]]

trend_total = (
    trend_total
    .groupby("YEAR", as_index=False)["ESTIMATE"]
    .mean()
    .sort_values("YEAR")
)

trend_total.to_csv("suicide_trend_total.csv", index=False)
print(f"✔ suicide_trend_total.csv -> {len(trend_total)} filas (1 por año)")

# ==================================================
# 2) Evolución por sexo (formato wide para Flourish)
# ==================================================

# YEAR | Female | Male
# 1950 | 5.35   | 19.5

by_sex = df[
    (df["STUB_NAME"] == "Sex")
    & (df["AGE"] == "All ages")
][["YEAR", "STUB_LABEL", "ESTIMATE"]].rename(
    columns={"STUB_LABEL": "Sex"}
)

by_sex = (
    by_sex
    .groupby(["YEAR", "Sex"], as_index=False)["ESTIMATE"]
    .mean()
    .pivot(index="YEAR", columns="Sex", values="ESTIMATE")
    .reset_index()
    .sort_values("YEAR")
)

by_sex.to_csv("suicide_by_sex.csv", index=False)
print(f"✔ suicide_by_sex.csv -> {len(by_sex)} filas (wide format)")

# ==================================================
# 3) Diferencias por raza (año concreto, single race)
# ==================================================
by_race_2018 = df[
    (df["YEAR"] == args.year)
    & (df["STUB_NAME"] == "Sex and race")
    & (df["AGE"] == "All ages")
    & (df["STUB_LABEL"].str.startswith(f"{args.race_sex}:"))
][["STUB_LABEL", "ESTIMATE"]].copy()

by_race_2018["Race"] = by_race_2018["STUB_LABEL"].str.replace(
    f"{args.race_sex}: ", "", regex=False
)

by_race_2018 = (
    by_race_2018
    .groupby("Race", as_index=False)["ESTIMATE"]
    .mean()
    .sort_values("ESTIMATE", ascending=False)
)

by_race_2018.to_csv(
    f"suicide_by_race_{args.year}.csv",
    index=False
)

print(
    f"✔ suicide_by_race_{args.year}.csv -> "
    f"{len(by_race_2018)} filas (1 por raza)"
)

print(">>> FIN OK <<<")


# ==================================================
# 4) Sexo × Raza (año concreto, Sex and race) - LONG para heatmap
# ==================================================

# Race | Sex | ESTIMATE
# White | Female | 7.1
# White | Male   | 26.05
# Black or African American | Female | 2.8
# Black or African American | Male   | 11.6


sex_race_heatmap = df[
    (df["YEAR"] == args.year)
    & (df["STUB_NAME"] == "Sex and race")
    & (df["AGE"] == "All ages")
][["STUB_LABEL", "ESTIMATE"]].copy()

# Extraer Sex y Race desde "Male: White"
sex_race_heatmap[["Sex", "Race"]] = sex_race_heatmap["STUB_LABEL"].str.split(
    ": ", n=1, expand=True
)

# Una fila por (Race, Sex)
sex_race_heatmap = (
    sex_race_heatmap
    .groupby(["Race", "Sex"], as_index=False)["ESTIMATE"]
    .mean()
)

output4 = f"suicide_sex_race_{args.year}_heatmap.csv"
sex_race_heatmap.to_csv(output4, index=False)
print(f"✔ {output4} -> {len(sex_race_heatmap)} filas (long format)")
