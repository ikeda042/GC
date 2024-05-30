import os
from natsort import natsorted
import shutil
import matplotlib.pyplot as plt
import numpy as np


def init():
    try:
        shutil.rmtree("gcdata")
    except:
        pass
    try:
        os.mkdir("gcdata")
    except:
        pass


class PPData:
    def __init__(
        self,
        pp_header: list[str],
        pp_data: list[str],
        pp: list[float],
    ) -> None:
        self.pp_header: list[str] = pp_header
        self.conc: list[float] = pp_data
        self.pp: list[float] = pp


class GCdata:
    def __init__(self, date_acquired: str, samle_name: str) -> None:
        self.date_acquired: str = date_acquired
        self.sample_name: str = samle_name
        try:
            self.pressure = float(
                self.sample_name.split("_")[-1]
                .replace("bar", "")
                .replace("\n", "")
                .replace(" ", "")
                .replace("s", "")
            )
        except:
            self.pressure: float = -np.inf
        self.header: list[str] = None
        self.data: list[str] = None
        self.ppdata: PPData = None

    def set_data(self, data: list[str]) -> None:
        self.data = data

    def set_header(self, header: list[str]) -> None:
        self.header = header

    def set_ppdata(self, ppdata: PPData) -> None:
        self.ppdata = ppdata

    def __repr__(self) -> str:
        return f"{self.date_acquired},{self.sample_name},{self.pressure})"


filename = "ASCIIData_HMC53L002.txt"


def load_data(filename: str) -> list[str]:
    init()
    with open(filename, "r", encoding="ISO-8859-1") as fp:
        data = [i.replace("\n", "") for i in fp.readlines() if i.strip() != ""]

    header_indices = [n for n, i in enumerate(data) if "[Header]" in i]
    num_data = sum(1 for _ in header_indices)

    for h in range(len(header_indices)):
        start = header_indices[h]
        end = header_indices[h + 1] if h + 1 < len(header_indices) else None
        with open(f"gcdata/data_{h}.txt", "w") as fp:
            for i in data[start:end]:
                fp.write(i + "\n")

    gc_data_: list[GCdata] = []
    for data_file in natsorted(os.listdir("gcdata")):
        with open(f"gcdata/{data_file}", "r") as fp:
            data = [i.replace("\n", "") for i in fp.readlines() if i.strip() != ""]
        gc_data = GCdata(data[14], data[17])
        gc_data.set_data(data[74:])
        gc_data.set_header(data[73].split(","))
        gc_data_.append(gc_data)


# pp_data: list[PPData] = []
# for n, i in enumerate(gc_data_):
#     print(i.sample_name)
#     print(i.header)
#     print(i.data)
#     pp_header: list[str] = []
#     conc: list[float] = []
#     for k in i.data:
#         conc.append(float(k.split(",")[7]))
#         pp_header.append(k.split(",")[10])
#     pp: list[float] = [i.pressure * j / 100 for i, j in zip(gc_data_, conc)]
#     print(pp_header)
#     print(pp)
#     print(conc)
#     pp_data.append(PPData(i.sample_name, pp_header, conc, pp))


# pp_data_sets = [pp_data[i : i + 3] for i in range(0, len(pp_data), 3)]

# for i in pp_data_sets:
#     print(i[0].sample_name)
#     print(i[1].sample_name)
#     print(i[2].sample_name)
#     print("+++++++++++++++++++++++")
load_data(filename)
