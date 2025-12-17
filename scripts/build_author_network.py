# build_author_network.py - Final Fixed Version
import pandas as pd
import json
from collections import defaultdict
import os

print("=" * 70)
print("Building Author Collaboration Network")
print("=" * 70)

# 数据路径 - 从 scripts 目录运行时，数据在 ./data/processed/
DATA_DIR = 'data/processed'
OUTPUT_DIR = 'data/processed'

print(f"\nCurrent directory: {os.getcwd()}")
print(f"Looking for data in: {DATA_DIR}")

# 检查文件是否存在
if not os.path.exists(f"{DATA_DIR}/papers.csv"):
    print(f"\n❌ Error: Cannot find {DATA_DIR}/papers.csv")
    print("\nPlease run this script from the scripts directory:")
    print("  cd scripts")
    print("  python build_author_network.py")
    exit(1)

print(f"\n[Step 1] Loading data from {DATA_DIR}...")

try:
    # 加载数据
    papers_df = pd.read_csv(f"{DATA_DIR}/papers.csv")
    print(f"  ✓ Loaded {len(papers_df)} papers")
    
    authors_df = pd.read_csv(f"{DATA_DIR}/authors.csv")
    print(f"  ✓ Loaded {len(authors_df)} authors")
    
    paper_authors_df = pd.read_csv(f"{DATA_DIR}/paper_author_affiliations.csv")
    print(f"  ✓ Loaded {len(paper_authors_df)} paper-author relationships")
    
except Exception as e:
    print(f"❌ Error loading data: {e}")
    exit(1)

print(f"\n[Step 2] Filtering data...")

# 筛选 2020-2025 年的论文
papers_df = papers_df[(papers_df['Year'] >= 2020) & (papers_df['Year'] <= 2025)]
print(f"  Papers 2020-2025: {len(papers_df)}")

# 筛选 Computer Science 论文
if 'FieldsOfStudy' in papers_df.columns:
    cs_papers = papers_df[
        papers_df['FieldsOfStudy'].str.contains('Computer Science', case=False, na=False)
    ]
    print(f"  Computer Science papers: {len(cs_papers)}")
    
    if len(cs_papers) < 50:
        print(f"  Warning: Only {len(cs_papers)} CS papers found, using all papers instead")
        cs_papers = papers_df
else:
    print("  No FieldsOfStudy column, using all papers")
    cs_papers = papers_df

print(f"\n[Step 3] Building author collaboration network...")

# 获取这些论文的所有作者关系
paper_ids = cs_papers['PaperId'].unique()
relevant_paper_authors = paper_authors_df[
    paper_authors_df['PaperId'].isin(paper_ids)
]

print(f"  Relevant paper-author relationships: {len(relevant_paper_authors)}")

# 按论文分组，找出合作关系
paper_groups = relevant_paper_authors.groupby('PaperId')['AuthorId'].apply(list)

# 构建边（合作关系）
edges = defaultdict(int)
for paper_id, authors in paper_groups.items():
    if len(authors) < 2:
        continue
    
    # 为每对作者创建一条边
    for i in range(len(authors)):
        for j in range(i + 1, len(authors)):
            edge = tuple(sorted([authors[i], authors[j]]))
            edges[edge] += 1  # 权重为合作次数

print(f"  Total collaborations: {len(edges)}")

# 构建节点
print(f"\n[Step 4] Creating network structure...")

author_ids = set()
for edge in edges:
    author_ids.update(edge)

nodes = []
for author_id in author_ids:
    author_info = authors_df[authors_df['AuthorId'] == author_id]
    
    if len(author_info) > 0:
        # 计算作者的论文数
        paper_count = len(relevant_paper_authors[
            relevant_paper_authors['AuthorId'] == author_id
        ])
        
        nodes.append({
            'id': str(author_id),
            'name': author_info.iloc[0]['DisplayName'],
            'paperCount': paper_count
        })

print(f"  Nodes: {len(nodes)}")

# 构建边
links = []
for (source, target), weight in edges.items():
    links.append({
        'source': str(source),
        'target': str(target),
        'weight': int(weight)
    })

print(f"  Links: {len(links)}")

# 创建网络对象
network = {
    'nodes': nodes,
    'links': links,
    'metadata': {
        'total_papers': len(cs_papers),
        'total_authors': len(nodes),
        'total_collaborations': len(links),
        'year_range': f"{int(cs_papers['Year'].min())}-{int(cs_papers['Year'].max())}"
    }
}

# 保存
print(f"\n[Step 5] Saving network...")

output_path = f"{OUTPUT_DIR}/author_network.json"
with open(output_path, 'w') as f:
    json.dump(network, f, indent=2)

print(f"  ✓ Saved to {output_path}")

print("\n" + "=" * 70)
print("✅ Author collaboration network created successfully!")
print("=" * 70)
print("\nNetwork Statistics:")
print(f"  Nodes (Authors): {len(nodes)}")
print(f"  Links (Collaborations): {len(links)}")
print(f"  Papers: {len(cs_papers)}")
print(f"  Year Range: {int(cs_papers['Year'].min())}-{int(cs_papers['Year'].max())}")

# 打印一些额外的统计信息
if len(links) > 0:
    weights = [link['weight'] for link in links]
    print(f"\nCollaboration Statistics:")
    print(f"  Average collaborations per pair: {sum(weights)/len(weights):.2f}")
    print(f"  Max collaborations: {max(weights)}")
    print(f"  Min collaborations: {min(weights)}")

if len(nodes) > 0:
    paper_counts = [node['paperCount'] for node in nodes]
    print(f"\nAuthor Statistics:")
    print(f"  Average papers per author: {sum(paper_counts)/len(paper_counts):.2f}")
    print(f"  Most prolific author: {max(paper_counts)} papers")

print("\nNext step: Use this network data in your frontend visualization!")