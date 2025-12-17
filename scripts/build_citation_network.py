# build_citation_network.py
import pandas as pd
import json
import os

print("=" * 70)
print("Building Paper Citation Network")
print("=" * 70)

# 数据路径
DATA_DIR = 'data/processed'
OUTPUT_DIR = 'data/processed'

print(f"\nCurrent directory: {os.getcwd()}")
print(f"Looking for data in: {DATA_DIR}")

# 检查文件是否存在
if not os.path.exists(f"{DATA_DIR}/papers.csv"):
    print(f"\n❌ Error: Cannot find {DATA_DIR}/papers.csv")
    print("\nPlease run this script from the scripts directory:")
    print("  cd scripts")
    print("  python build_citation_network.py")
    exit(1)

print(f"\n[Step 1] Loading data from {DATA_DIR}...")

try:
    # 加载数据
    papers_df = pd.read_csv(f"{DATA_DIR}/papers.csv")
    print(f"  ✓ Loaded {len(papers_df)} papers")
    
    citations_df = pd.read_csv(f"{DATA_DIR}/paper_references.csv")
    print(f"  ✓ Loaded {len(citations_df)} citations")
    
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

print(f"\n[Step 3] Building citation network...")

# 获取 UCSD 论文的 ID 集合
ucsd_paper_ids = set(cs_papers['PaperId'].astype(str))
print(f"  UCSD paper IDs: {len(ucsd_paper_ids)}")

# 筛选 UCSD 论文之间的引用关系
# 引用关系：PaperId (citing paper) -> PaperReferenceId (cited paper)
internal_citations = citations_df[
    (citations_df['PaperId'].astype(str).isin(ucsd_paper_ids)) &
    (citations_df['PaperReferenceId'].astype(str).isin(ucsd_paper_ids))
]

print(f"  Internal citations (UCSD -> UCSD): {len(internal_citations)}")

# 构建节点
print(f"\n[Step 4] Creating network structure...")

nodes = []
for _, paper in cs_papers.iterrows():
    nodes.append({
        'id': str(paper['PaperId']),
        'title': paper.get('Title', 'Unknown'),
        'year': int(paper['Year']) if pd.notna(paper['Year']) else 0,
        'citationCount': int(paper.get('CitationCount', 0)) if pd.notna(paper.get('CitationCount', 0)) else 0
    })

print(f"  Nodes: {len(nodes)}")

# 构建边
links = []
for _, citation in internal_citations.iterrows():
    links.append({
        'source': str(citation['PaperId']),
        'target': str(citation['PaperReferenceId'])
    })

print(f"  Links: {len(links)}")

# 创建网络对象
network = {
    'nodes': nodes,
    'links': links,
    'metadata': {
        'total_papers': len(cs_papers),
        'total_citations': len(links),
        'year_range': f"{int(cs_papers['Year'].min())}-{int(cs_papers['Year'].max())}"
    }
}

# 保存
print(f"\n[Step 5] Saving network...")

output_path = f"{OUTPUT_DIR}/citation_network.json"
with open(output_path, 'w') as f:
    json.dump(network, f, indent=2)

print(f"  ✓ Saved to {output_path}")

print("\n" + "=" * 70)
print("✅ Citation network created successfully!")
print("=" * 70)
print("\nNetwork Statistics:")
print(f"  Nodes (Papers): {len(nodes)}")
print(f"  Links (Citations): {len(links)}")
print(f"  Year Range: {int(cs_papers['Year'].min())}-{int(cs_papers['Year'].max())}")

# 打印一些额外的统计信息
if len(nodes) > 0:
    citation_counts = [node['citationCount'] for node in nodes]
    print(f"\nCitation Statistics:")
    print(f"  Average citations per paper: {sum(citation_counts)/len(citation_counts):.2f}")
    print(f"  Most cited paper: {max(citation_counts)} citations")
    print(f"  Papers with 0 citations: {sum(1 for c in citation_counts if c == 0)}")

print("\nNext step: Use this network data in your frontend visualization!")