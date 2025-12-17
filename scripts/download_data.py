# download_data.py
import requests
import pandas as pd
import json
import time
from datetime import datetime
import os

# 创建数据目录
os.makedirs('data/raw', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)

# OpenAlex API base URL
BASE_URL = "https://api.openalex.org"

def get_ucsd_institution_id():
    """获取 UCSD 的 OpenAlex ID"""
    print("Searching for UCSD...")
    url = f"{BASE_URL}/institutions"
    params = {
        'search': 'University of California San Diego',
        'per_page': 5
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        print("\nFound institutions:")
        for inst in data['results']:
            print(f"  - {inst['display_name']}: {inst['id']}")
        
        # UCSD 的 ID
        ucsd = None
        for inst in data['results']:
            if 'San Diego' in inst['display_name'] and 'California' in inst['display_name']:
                ucsd = inst
                break
        
        if not ucsd:
            print("\nWarning: UCSD not found in top results, using first result")
            ucsd = data['results'][0]
        
        return ucsd['id']
    except Exception as e:
        print(f"Error getting institution ID: {e}")
        # 如果 API 失败，返回已知的 UCSD ID
        return "https://openalex.org/I138006243"

def download_ucsd_papers(institution_id, start_year=2020, end_year=2025, max_papers=1000):
    """下载 UCSD 的 CS 论文"""
    
    papers = []
    page = 1
    per_page = 200
    
    # 提取 institution ID
    inst_id = institution_id.split('/')[-1] if '/' in institution_id else institution_id
    
    print(f"\nDownloading UCSD papers ({start_year}-{end_year})...")
    print(f"Institution ID: {inst_id}")
    
    try:
        while len(papers) < max_papers:
            url = f"{BASE_URL}/works"
            
            # 简化查询，只按机构和年份过滤
            params = {
                'filter': f'institutions.id:{inst_id},publication_year:{start_year}-{end_year}',
                'per_page': per_page,
                'page': page,
                'select': 'id,title,publication_year,cited_by_count,authorships,referenced_works,topics'
            }
            
            print(f"\nFetching page {page}...", end=' ')
            response = requests.get(url, params=params)
            
            if response.status_code != 200:
                print(f"\nError: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                break
            
            data = response.json()
            results = data.get('results', [])
            
            if not results:
                print("No more results")
                break
            
            papers.extend(results)
            print(f"Got {len(results)} papers (Total: {len(papers)})")
            
            page += 1
            time.sleep(0.2)  # 避免请求过快
            
            if len(papers) >= max_papers:
                print(f"\nReached maximum of {max_papers} papers")
                break
                
    except Exception as e:
        print(f"\nError downloading papers: {e}")
        if papers:
            print(f"Continuing with {len(papers)} papers already downloaded")
    
    return papers

def process_papers_data(papers):
    """处理论文数据"""
    
    print("\nProcessing papers data...")
    
    papers_list = []
    authors_list = []
    paper_authors_list = []
    citations_list = []
    
    author_id_map = {}
    next_author_id = 1
    
    for idx, paper in enumerate(papers):
        try:
            paper_id = paper['id'].split('/')[-1]
            
            # 获取主题/领域信息
            topics = paper.get('topics', [])
            field = 'Computer Science' if any('computer' in str(t).lower() for t in topics) else 'General'
            
            # 论文信息
            papers_list.append({
                'PaperId': paper_id,
                'Title': paper.get('title', 'Unknown'),
                'Year': paper.get('publication_year', 0),
                'CitationCount': paper.get('cited_by_count', 0),
                'FieldsOfStudy': field
            })
            
            # 作者信息
            for authorship in paper.get('authorships', []):
                author = authorship.get('author', {})
                if not author:
                    continue
                
                author_openalex_id = author.get('id', '').split('/')[-1]
                if not author_openalex_id:
                    continue
                
                if author_openalex_id not in author_id_map:
                    author_id_map[author_openalex_id] = next_author_id
                    
                    authors_list.append({
                        'AuthorId': next_author_id,
                        'DisplayName': author.get('display_name', 'Unknown'),
                        'OpenAlexId': author_openalex_id
                    })
                    
                    next_author_id += 1
                
                author_id = author_id_map[author_openalex_id]
                
                # 论文-作者关系
                paper_authors_list.append({
                    'PaperId': paper_id,
                    'AuthorId': author_id,
                    'AuthorSequenceNumber': authorship.get('author_position', 'unknown')
                })
            
            # 引用关系
            for ref in paper.get('referenced_works', []):
                if ref:
                    ref_id = ref.split('/')[-1]
                    citations_list.append({
                        'PaperId': paper_id,
                        'PaperReferenceId': ref_id
                    })
            
            if (idx + 1) % 100 == 0:
                print(f"  Processed {idx + 1}/{len(papers)} papers")
                
        except Exception as e:
            print(f"  Error processing paper {idx}: {e}")
            continue
    
    # 转换为 DataFrame
    papers_df = pd.DataFrame(papers_list)
    authors_df = pd.DataFrame(authors_list)
    paper_authors_df = pd.DataFrame(paper_authors_list)
    citations_df = pd.DataFrame(citations_list)
    
    return papers_df, authors_df, paper_authors_df, citations_df

def save_data(papers_df, authors_df, paper_authors_df, citations_df):
    """保存处理后的数据"""
    
    print("\nSaving processed data...")
    
    papers_df.to_csv('data/processed/papers.csv', index=False)
    print(f"  ✓ papers.csv: {len(papers_df)} rows")
    
    authors_df.to_csv('data/processed/authors.csv', index=False)
    print(f"  ✓ authors.csv: {len(authors_df)} rows")
    
    paper_authors_df.to_csv('data/processed/paper_author_affiliations.csv', index=False)
    print(f"  ✓ paper_author_affiliations.csv: {len(paper_authors_df)} rows")
    
    citations_df.to_csv('data/processed/paper_references.csv', index=False)
    print(f"  ✓ paper_references.csv: {len(citations_df)} rows")
    
    # 打印统计信息
    print("\nData Statistics:")
    print(f"  Papers: {len(papers_df)}")
    print(f"  Authors: {len(authors_df)}")
    print(f"  Paper-Author relationships: {len(paper_authors_df)}")
    print(f"  Citations: {len(citations_df)}")
    print(f"  Years: {papers_df['Year'].min()} - {papers_df['Year'].max()}")

def main():
    print("=" * 70)
    print("SciSciNet Data Downloader for UCSD")
    print("=" * 70)
    
    try:
        # 1. 获取 UCSD ID
        print("\n[Step 1] Finding UCSD institution ID...")
        ucsd_id = get_ucsd_institution_id()
        print(f"✓ Using UCSD ID: {ucsd_id}")
        
        # 2. 下载论文数据
        print("\n[Step 2] Downloading papers...")
        papers = download_ucsd_papers(ucsd_id, 2020, 2025, max_papers=1000)
        print(f"✓ Downloaded {len(papers)} papers")
        
        if len(papers) == 0:
            print("\n❌ No papers downloaded. Please check:")
            print("  1. Internet connection")
            print("  2. OpenAlex API is accessible")
            return
        
        # 保存原始数据
        print("\nSaving raw data...")
        with open('data/raw/ucsd_papers.json', 'w') as f:
            json.dump(papers, f, indent=2)
        print(f"✓ Saved raw data to data/raw/ucsd_papers.json")
        
        # 3. 处理数据
        print("\n[Step 3] Processing data...")
        papers_df, authors_df, paper_authors_df, citations_df = process_papers_data(papers)
        
        # 4. 保存数据
        save_data(papers_df, authors_df, paper_authors_df, citations_df)
        
        print("\n" + "=" * 70)
        print("✅ Data download and processing complete!")
        print("=" * 70)
        print("\nNext steps:")
        print("1. Check data/processed/ for CSV files")
        print("2. Run build_author_network.py to create author collaboration network")
        print("3. Run build_citation_network.py to create citation network")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()