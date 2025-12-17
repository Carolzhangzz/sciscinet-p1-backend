import pandas as pd
import json
from pathlib import Path
from collections import defaultdict

# ========= 路径 =========
INPUT_PATH = Path("../data/processed/author_edges.csv")
OUTPUT_PATH = Path("../data/processed/author_network_d3.json")

# ========= 读 edge list =========
edges_df = pd.read_csv(INPUT_PATH)

# ========= 统计节点（作者） =========
nodes = {}
degree_count = defaultdict(int)

for _, row in edges_df.iterrows():
    src = row["source"]
    tgt = row["target"]

    degree_count[src] += 1
    degree_count[tgt] += 1

# 构建 node list
nodes_list = [
    {"id": author, "degree": degree}
    for author, degree in degree_count.items()
]

# ========= 构建 link list =========
links_list = [
    {
        "source": row["source"],
        "target": row["target"],
        "weight": int(row["weight"])
    }
    for _, row in edges_df.iterrows()
]

# ========= 合并为 D3 JSON =========
graph = {
    "nodes": nodes_list,
    "links": links_list
}

# ========= 保存 =========
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(graph, f, indent=2)

print(f"Saved D3 network JSON to {OUTPUT_PATH}")
print(f"Nodes: {len(nodes_list)}, Links: {len(links_list)}")
