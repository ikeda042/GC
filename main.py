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
    def __init__(
        self,
        block_num: int,
        date_acquired: str,
        compound_raw: dict[str, list[float]],
        compound: dict[str, float],
    ) -> None:
        self.block_num: int = block_num
        self.date_acquired: str = date_acquired
        self.compound_raw: dict[str, list[float]] = compound_raw
        self.compound: dict[str, float] = compound

    def __repr__(self) -> str:
        return f"{self.block_num}|{self.compound}"


def load_file(filename):
    encodings = ["ISO-8859-1"]
    for encoding in encodings:
        try:
            with open(filename, "r", encoding=encoding) as fp:
                data = [i.replace("\n", "") for i in fp.readlines() if i.strip() != ""]
                return data
        except:
            pass
    raise Exception("File not loaded")


def load_data(filename: str) -> list[GraphData]:

    init()

    data = load_file(filename)

    header_indices = [n for n, i in enumerate(data) if "[Header]" in i]

    for h in range(len(header_indices)):
        start = header_indices[h]
        end = header_indices[h + 1] if h + 1 < len(header_indices) else None
        with open(f"gcdata/data_{h}.txt", "w",encoding="utf-8") as fp:
            for i in data[start:end]:
                fp.write(str(i) + "\n")

    gc_data_: list[GCdata] = []
    for data_file in natsorted(os.listdir("gcdata")):
        with open(f"gcdata/{data_file}", "r") as fp:
            data = [i.replace("\n", "") for i in fp.readlines() if i.strip() != ""]
        gc_data = GCdata(data[14], data[17])
        gc_data.set_data(data[74:])
        gc_data.set_header(data[73].split(","))
        gc_data_.append(gc_data)

    table_string = ""
    compounds_data:list[dict[str,str]] = []
    for n, i in enumerate(gc_data_):
        pp_header: list[str] = []
        conc: list[float] = []
        for k in i.data:
            conc.append(float(k.split(",")[5]))
            pp_header.append(k.split(",")[1])
        pp: list[float] = [i.pressure * j / 100 for i, j in zip(gc_data_, conc)]
        i.set_ppdata(PPData(pp_header, conc, pp))
        tmp = {}
        for i in i.data:
            tmp[i.split(",")[1]] = float(i.split(",")[5])/100
        compounds_data.append(tmp)

    table_string += "Date,Pressure(bar),"+','.join([c for c in compounds_data[0].keys()])+"\n"
    for i,c in zip(gc_data_,compounds_data):
        table_string += f"{i.date_acquired.split(",")[-1]},{round(i.pressure,4)},{','.join([str(round(c[key],4)) for key in c.keys()])}\n"
    with open("graph/pressure_table.csv","w") as fp:
        fp.write(table_string)
    gc_data_sets: list[GCdata] = [
        gc_data_[i : i + 3] for i in range(0, len(gc_data_), 3)
    ]

    ret: list[GraphData] = []
    for n, i in enumerate(gc_data_sets):
        compound_i = {}
        compound_raw_i = {}
        for j in i:
            for name_index, name in enumerate(j.ppdata.pp_header):
                compound_i[name] = sum(
                    [i[t].ppdata.pp[name_index] for t in range(len(i))]
                ) / len(i)
                compound_raw_i[name] = [
                    i[t].ppdata.pp[name_index] for t in range(len(i))
                ]
        ret.append(
            GraphData(
                block_num=n,
                date_acquired=i[0].date_acquired,
                compound_raw=compound_raw_i,
                compound=compound_i,
            )
        )
    return ret


############################################################################
filename = "ASCIIDataHMC53_s001.txt"
############################################################################
graph_data: list[GraphData] = load_data(filename)

fig = plt.figure(figsize=(10, 10))

all_values = [value for i in graph_data for value in i.compound.values()]
y_min, y_max = min(all_values), max(all_values)


fig, ax = plt.subplots(1, len(graph_data), figsize=(30, 4))
for n, i in enumerate(graph_data):
    ax[n].tick_params(axis="x", which="both", bottom=False, top=False, labelbottom=True)
    ax[n].tick_params(direction="in")

    errors = [np.std(i.compound_raw[k]) for k in i.compound.keys()]

    ax[n].bar(
        i.compound.keys(),
        i.compound.values(),
        width=0.7,
        color="gray",
        yerr=errors,
        capsize=5,  
    )
    for k in i.compound.keys():
        ax[n].scatter(
            [k] * len(i.compound_raw[k]),
            i.compound_raw[k],
            color="black",
            s=10,
        )
    ax[n].set_ylim(0, y_max + y_max * 0.1)
    ax[n].set_title(f"{i.date_acquired.split(',')[-1]}")
    ax[n].set_xlabel("Gas Compound")
    ax[n].set_ylabel("Pressure (bar)")

fig.savefig("graph/summary_pp.png", dpi=500)
plt.clf()

fig, ax = plt.subplots(1, len(graph_data), figsize=(15, 5))
