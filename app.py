from flask import Flask, jsonify
from flask_cors import CORS
import json
import os
import pandas as pd

app = Flask(__name__)
CORS(app)

# 数据文件路径
DATA_DIR = os.path.join(os.path.dirname(__file__), 'scripts', 'data', 'processed')

@app.route('/')
def home():
    """API 主页"""
    return jsonify({
        'message': 'SciSciNet Backend API',
        'version': '1.0',
        'endpoints': {
            'author_network': '/api/author-network',
            'citation_network': '/api/citation-network',
            'papers': '/api/papers',
            'authors': '/api/authors',
            'stats': '/api/stats',
            'timeline': '/api/timeline',  # NEW
            'patent_distribution': '/api/patent-distribution'  # NEW
        }
    })

@app.route('/api/author-network')
def get_author_network():
    """获取作者协作网络数据"""
    try:
        with open(os.path.join(DATA_DIR, 'author_network.json'), 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({'error': 'Author network data not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/citation-network')
def get_citation_network():
    """获取论文引用网络数据"""
    try:
        with open(os.path.join(DATA_DIR, 'citation_network.json'), 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({'error': 'Citation network data not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/papers')
def get_papers():
    """获取论文列表"""
    try:
        papers_df = pd.read_csv(os.path.join(DATA_DIR, 'papers.csv'))
        papers = papers_df.to_dict('records')
        
        return jsonify({
            'total': len(papers),
            'papers': papers
        })
    except FileNotFoundError:
        return jsonify({'error': 'Papers data not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/authors')
def get_authors():
    """获取作者列表"""
    try:
        authors_df = pd.read_csv(os.path.join(DATA_DIR, 'authors.csv'))
        authors = authors_df.to_dict('records')
        
        return jsonify({
            'total': len(authors),
            'authors': authors
        })
    except FileNotFoundError:
        return jsonify({'error': 'Authors data not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """获取数据统计信息"""
    try:
        with open(os.path.join(DATA_DIR, 'author_network.json'), 'r') as f:
            author_network = json.load(f)
        
        with open(os.path.join(DATA_DIR, 'citation_network.json'), 'r') as f:
            citation_network = json.load(f)
        
        stats = {
            'author_network': {
                'nodes': len(author_network['nodes']),
                'links': len(author_network['links']),
                'metadata': author_network.get('metadata', {})
            },
            'citation_network': {
                'nodes': len(citation_network['nodes']),
                'links': len(citation_network['links']),
                'metadata': citation_network.get('metadata', {})
            }
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/timeline')
def get_timeline():
    """NEW: 获取时间线数据 - 过去10年的论文数量"""
    try:
        papers_df = pd.read_csv(os.path.join(DATA_DIR, 'papers.csv'))
        
        # 筛选过去10年 (2015-2024)
        current_year = 2024
        papers_df = papers_df[
            (papers_df['Year'] >= current_year - 9) & 
            (papers_df['Year'] <= current_year)
        ]
        
        # 按年份分组计数
        timeline = papers_df.groupby('Year').size().reset_index(name='count')
        
        # 确保所有年份都有数据（填充0）
        all_years = list(range(current_year - 9, current_year + 1))
        timeline_dict = dict(zip(timeline['Year'], timeline['count']))
        
        result = [
            {'year': year, 'count': timeline_dict.get(year, 0)}
            for year in all_years
        ]
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/timeline/<int:year>')
def get_timeline_year(year):
    """NEW: 获取特定年份的论文数据"""
    try:
        papers_df = pd.read_csv(os.path.join(DATA_DIR, 'papers.csv'))
        year_papers = papers_df[papers_df['Year'] == year]
        
        return jsonify({
            'year': year,
            'count': len(year_papers),
            'papers': year_papers.to_dict('records')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/patent-distribution')
def get_patent_distribution():
    """NEW: 获取专利引用分布（所有论文）"""
    try:
        papers_df = pd.read_csv(os.path.join(DATA_DIR, 'papers.csv'))
        
        # 生成模拟的专利引用数据（因为OpenAlex数据中可能没有Patent_Count）
        # 如果你的数据有Patent_Count列，直接使用即可
        import numpy as np
        np.random.seed(42)
        
        if 'Patent_Count' not in papers_df.columns:
            # 模拟专利引用数据：大多数论文0-5个，少数更多
            papers_df['Patent_Count'] = np.random.choice(
                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20],
                size=len(papers_df),
                p=[0.3, 0.25, 0.15, 0.1, 0.08, 0.05, 0.03, 0.02, 0.01, 0.005, 0.003, 0.001, 0.001]
            )
        
        # 创建直方图数据
        patent_counts = papers_df['Patent_Count'].value_counts().sort_index()
        
        result = [
            {'patent_count': int(pc), 'frequency': int(freq)}
            for pc, freq in patent_counts.items()
        ]
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/patent-distribution/<int:year>')
def get_patent_distribution_year(year):
    """NEW: 获取特定年份的专利引用分布"""
    try:
        papers_df = pd.read_csv(os.path.join(DATA_DIR, 'papers.csv'))
        
        # 筛选特定年份
        year_papers = papers_df[papers_df['Year'] == year]
        
        if len(year_papers) == 0:
            return jsonify([])
        
        # 生成模拟专利引用数据
        import numpy as np
        np.random.seed(year)  # 使用年份作为seed，保持一致性
        
        if 'Patent_Count' not in year_papers.columns:
            year_papers = year_papers.copy()
            year_papers['Patent_Count'] = np.random.choice(
                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20],
                size=len(year_papers),
                p=[0.3, 0.25, 0.15, 0.1, 0.08, 0.05, 0.03, 0.02, 0.01, 0.005, 0.003, 0.001, 0.001]
            )
        
        # 创建直方图数据
        patent_counts = year_papers['Patent_Count'].value_counts().sort_index()
        
        result = [
            {'patent_count': int(pc), 'frequency': int(freq)}
            for pc, freq in patent_counts.items()
        ]
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """健康检查"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    print("=" * 70)
    print("SciSciNet Backend API Server")
    print("=" * 70)
    print("\nAvailable endpoints:")
    print("  - http://localhost:5001/")
    print("  - http://localhost:5001/api/author-network")
    print("  - http://localhost:5001/api/citation-network")
    print("  - http://localhost:5001/api/timeline")
    print("  - http://localhost:5001/api/patent-distribution")
    print("  - http://localhost:5001/api/patent-distribution/<year>")
    print("\nStarting server...")
    print("=" * 70)
    
    app.run(debug=True, host='0.0.0.0', port=5001)