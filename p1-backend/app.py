from flask import Flask, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)  # 允许所有来源访问

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
            'stats': '/api/stats'
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
        import pandas as pd
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
        import pandas as pd
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

@app.route('/health')
def health_check():
    """健康检查"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    print("=" * 70)
    print("SciSciNet Backend API Server")
    print("=" * 70)
    print("\nAvailable endpoints:")
    print("  - http://localhost:5000/")
    print("  - http://localhost:5000/api/author-network")
    print("  - http://localhost:5000/api/citation-network")
    print("  - http://localhost:5000/api/papers")
    print("  - http://localhost:5000/api/authors")
    print("  - http://localhost:5000/api/stats")
    print("\nStarting server...")
    print("=" * 70)
    
    app.run(debug=True, host='0.0.0.0', port=5001)