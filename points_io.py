import csv
from pathlib import Path
from point import Point6D

CSV_HEADER = ["name", "x", "y", "z", "a", "b", "c"]

def init_points_csv(filename: str):
    if not Path(filename).exists():
        with open(filename, "w", newline="") as f:
            csv.writer(f).writerow(CSV_HEADER)

def save_point_csv(filename: str, point: Point6D, overwrite=True):
    init_points_csv(filename)

    rows = []
    found = False

    with open(filename, "r", newline="") as f:
        rows = list(csv.reader(f))

    for i, row in enumerate(rows[1:], start=1):
        if row[0] == point.name:
            if overwrite:
                rows[i] = [point.name, point.x, point.y, point.z,
                           point.a, point.b, point.c]
                found = True
            else:
                raise ValueError("Point already exists")

    if not found:
        rows.append([point.name, point.x, point.y, point.z,
                     point.a, point.b, point.c])

    with open(filename, "w", newline="") as f:
        csv.writer(f).writerows(rows)

def load_point_csv(filename: str, name: str) -> Point6D:
    with open(filename, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["name"] == name:
                return Point6D(
                    name=row["name"],
                    x=float(row["x"]),
                    y=float(row["y"]),
                    z=float(row["z"]),
                    a=float(row["a"]),
                    b=float(row["b"]),
                    c=float(row["c"]),
                )
    raise KeyError(f"Point '{name}' not found")
