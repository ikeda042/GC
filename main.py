import os
from natsort import natsorted
import shutil


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
            self.pressure: float = 0.0
        self.header: list[str] = None
        self.data: list[str] = None

    def __repr__(self) -> str:
        return f"{self.date_acquired},{self.sample_name},{self.pressure})"

    def set_data(self, data: list[str]) -> None:
        self.data = data

    def set_header(self, header: list[str]) -> None:
        self.header = header


try:
    shutil.rmtree("data")
except:
    pass
try:
    os.mkdir("data")
except:
    pass

with open("ASCIIData_HMC53L002.txt", "r", encoding="ISO-8859-1") as fp:
    data = [i.replace("\n", "") for i in fp.readlines() if i.strip() != ""]

num_data: int = 0
header_indices: list[int] = []
for n, i in enumerate(data):
    if "[Header]" in i:
        num_data += 1
        header_indices.append(n)


for header_index in range(len(header_indices) - 1):
    with open(f"data/data_{header_index}.txt", "w") as fp:
        for i in data[header_indices[header_index] : header_indices[header_index + 1]]:
            fp.write(i + "\n")


with open(f"data/data_{num_data - 1}.txt", "w") as fp:
    for i in data[header_indices[-1] :]:
        fp.write(i + "\n")


gc_data_: list[GCdata] = []
for data_file in natsorted(os.listdir("data")):
    with open(f"data/{data_file}", "r") as fp:
        data = [i.replace("\n", "") for i in fp.readlines() if i.strip() != ""]
    gc_data = GCdata(data[14], data[17])
    gc_data.set_data(data[74:])
    gc_data.set_header(data[73].split(","))
    gc_data_.append(gc_data)


print(gc_data_[0].header)
print(gc_data_[0].data)


class PPData:
    def __init__(
        self,
        sample_name: str,
        pp_header: list[str],
        pp_data: list[str],
        pp: list[float],
    ) -> None:
        self.sample_name: str = sample_name
        self.pp_header: list[str] = pp_header
        self.conc: list[float] = pp_data
        self.pp: list[float] = pp


pp_data: list[PPData] = []
for n, i in enumerate(gc_data_):
    print(i.sample_name)
    print(i.header)
    print(i.data)
    pp_header: list[str] = []
    conc: list[float] = []
    for i in i.data:
        conc.append(float(i.split(",")[7]))
        pp_header.append(i.split(",")[10])
    pp: list[float] = [i.pressure * j / 100 for i, j in zip(gc_data_, conc)]
    print(pp_header)
    print(pp)
    print(conc)
    pp_data.append(PPData(pp_header, conc, pp))


pp_data_sets = [pp_data[i : i + 3] for i in range(0, len(pp_data), 3)]
