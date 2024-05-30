import os
from natsort import natsorted
import shutil
import matplotlib.pyplot as plt
import numpy as np


def init():
    try:
        shutil.rmtree("gcdata")
        shutil.rmtree("graph")

    except:
        pass
    try:
        os.mkdir("gcdata")
        os.mkdir("graph")
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
        return f"{self.ppdata.pp_header}\n{self.ppdata.pp}\n"


class GraphData:
    def __init__(self, block_num: int, compound) -> None:
        self.block_num: int = block_num
        self.compound: dict[str, list[float]] = compound

    def __repr__(self) -> str:
        return f"{self.block_num}|{self.compound}"


filename = "ASCIIData_HMC53L002.txt"


def load_data(filename: str) -> list[GraphData]:

    init()

    with open(filename, "r", encoding="ISO-8859-1") as fp:
        data = [i.replace("\n", "") for i in fp.readlines() if i.strip() != ""]

    header_indices = [n for n, i in enumerate(data) if "[Header]" in i]

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
    for n, i in enumerate(gc_data_):
        pp_header: list[str] = []
        conc: list[float] = []
        for k in i.data:
            conc.append(float(k.split(",")[7]))
            pp_header.append(k.split(",")[10])
        pp: list[float] = [i.pressure * j / 100 for i, j in zip(gc_data_, conc)]
        i.set_ppdata(PPData(pp_header, conc, pp))

    gc_data_sets: list[GCdata] = [
        gc_data_[i : i + 3] for i in range(0, len(gc_data_), 3)
    ]

    ret: list[GraphData] = []
    for n, i in enumerate(gc_data_sets):
        compound_i = {}
        for j in i:
            for name_index, name in enumerate(j.ppdata.pp_header):
                compound_i[name] = sum(
                    [i[t].ppdata.pp[name_index] for t in range(len(i))]
                ) / len(i)
        ret.append(GraphData(block_num=n, compound=compound_i))
    return ret


graph_data: list[GraphData] = load_data(filename)

fig = plt.figure(figsize=(10, 10))

all_values = [value for i in graph_data for value in i.compound.values()]
y_min, y_max = min(all_values), max(all_values)

for n, i in enumerate(graph_data):
    bar_plot = plt.bar(i.compound.keys(), i.compound.values())
    plt.ylim(0, y_max)
    plt.legend()
    plt.gca().tick_params(axis="x", direction="in", length=5)
    fig.savefig(f"graph/{n}.png", dpi=300)

    plt.clf()

fig, ax = plt.subplots(1, len(graph_data), figsize=(15, 5))
for n, i in enumerate(graph_data):
    ax[n].bar(i.compound.keys(), i.compound.values(), width=0.5, color="gray")
    ax[n].set_ylim(0, y_max + y_max * 0.1)
    ax[n].set_title(f"Sample {n} (n=3 / mean)")
plt.tight_layout()

fig.savefig("graph/summary.png", dpi=500)
plt.clf()
