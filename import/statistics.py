import pyarrow.compute as pc
import pyarrow.parquet as pq

from frames_benchmark_record import FramesBenchmarkRecord
from load_csv import load_csv
from redirected_links import redirected_links
from statistics_record import StatisticsRecord

tests = load_csv("test.tsv", FramesBenchmarkRecord, delimiter="\t")
table = pq.read_table("train-00000-of-00001.parquet", memory_map=True)

pre_statistics = load_csv(
    "statistics.psv",
    StatisticsRecord,
    delimiter="|",
    fieldnames=["", "question", "naive", "local", "global", "hybrid"],
)
statistics_dict: dict[int, StatisticsRecord] = {}
for pre_statistic in pre_statistics:
    statistics_dict[pre_statistic.id] = pre_statistic
statistics = statistics_dict.values()

LINK = "link"
TEXT = "text"

# print(len(statistics))
acc_naive = 0
acc_local = 0
acc_global = 0
acc_hybrid = 0
acc_total = 0
for i, statistic in enumerate(statistics):
    count = len(tests[i].wiki_links)
    size = 0
    links = list(enumerate(redirected_links(tests[i].wiki_links)))
    for link_i, link in links:
        text = str(table.filter(pc.match_substring(table[LINK], link))[TEXT][0])
        size += len(text)
    print(str(statistic.id).rjust(3, "0"), count, str(size).rjust(6, " "), statistic.in_total())
    acc_naive += statistic.naive
    acc_local += statistic.local
    acc_global += statistic.global_
    acc_hybrid += statistic.hybrid
    acc_total += statistic.in_total()
print()
print(f"naive: {round(100.0 * acc_naive / len(statistics), 1)} %")
print(f"local: {round(100.0 * acc_local / len(statistics), 1)} %")
print(f"global: {round(100.0 * acc_global / len(statistics), 1)} %")
print(f"hybrid: {round(100.0 * acc_hybrid / len(statistics), 1)} %")
print()
print(f"total: {round(100.0 * acc_total / len(statistics), 1)} %")
