import pytest
import networkx as nx
from pathlib import Path
from src import config
from src.mining.miner import GitHubMiner
from src.graph.builder import CollaborationGraphBuilder
from src import analysis
from src.analysis import analyzer
from src.export import exporter

def test_directories_creation():
    """Testa se as pastas padrão de dados são criadas corretamente."""
    config.init_directories()
    assert config.DATA_DIR.exists()
    assert config.RAW_DATA_DIR.exists()
    assert config.PROCESSED_DATA_DIR.exists()
    assert config.OUTPUT_DATA_DIR.exists()

def test_mock_data_generation():
    """Testa se a geração de dados mock possui todas as chaves e estrutura necessárias."""
    data = GitHubMiner.generate_mock_data()
    assert "repository" in data
    assert "issues" in data
    assert "prs" in data
    assert len(data["issues"]) > 0 or len(data["prs"]) > 0
    
    # Testar formato de uma issue
    first_issue = data["issues"][0]
    assert "number" in first_issue
    assert "author" in first_issue
    assert "comments" in first_issue
    assert "is_pr" in first_issue

def test_graph_builder_and_bot_filtering():
    """Testa se o construtor do grafo monta nós/arestas com pesos certos e filtra bots."""
    # Massa de dados de teste controlada
    test_data = {
        "issues": [
            {
                "number": 1,
                "title": "Bug in API",
                "author": "tiangolo",
                "author_avatar": "avatar_t",
                "author_type": "User",
                "is_pr": False,
                "comments": [
                    {"author": "dmontagu", "author_avatar": "avatar_d", "author_type": "User"},
                    {"author": "dependabot", "author_avatar": "avatar_dep", "author_type": "Bot"}
                ]
            }
        ],
        "prs": [
            {
                "number": 2,
                "title": "Improve docs",
                "author": "dmontagu",
                "author_avatar": "avatar_d",
                "author_type": "User",
                "is_pr": True,
                "comments": [
                    {"author": "tiangolo", "author_avatar": "avatar_t", "author_type": "User"}
                ],
                "reviews": [
                    {"author": "tiangolo", "author_avatar": "avatar_t", "author_type": "User", "state": "APPROVED"}
                ]
            }
        ]
    }
    
    # Caso 1: Excluindo bots
    builder = CollaborationGraphBuilder(exclude_bots=True)
    g = builder.build_from_mined_data(test_data)
    
    # dependabot (Bot) deve ser excluído
    assert "dependabot" not in g.nodes()
    assert "tiangolo" in g.nodes()
    assert "dmontagu" in g.nodes()
    
    # Contribuições
    # tiangolo abriu 1 issue + comentou 1 pr + revisou 1 pr = 3 contribuições
    assert g.nodes["tiangolo"]["contributions"] == 3
    # dmontagu abriu 1 pr + comentou 1 issue = 2 contribuições
    assert g.nodes["dmontagu"]["contributions"] == 2
    
    # Arestas
    # dmontagu comentou no post de tiangolo -> Aresta dmontagu -> tiangolo (peso 1)
    assert g.has_edge("dmontagu", "tiangolo")
    assert g.edges["dmontagu", "tiangolo"]["weight"] == 1
    
    # tiangolo comentou e revisou no post de dmontagu -> Aresta tiangolo -> dmontagu (peso 2)
    assert g.has_edge("tiangolo", "dmontagu")
    assert g.edges["tiangolo", "dmontagu"]["weight"] == 2
    assert g.edges["tiangolo", "dmontagu"]["comments"] == 1
    assert g.edges["tiangolo", "dmontagu"]["reviews"] == 1

def test_analyzer_metrics():
    """Testa se as funções do analisador de rede calculam as centralidades e comunidades sem erros."""
    # Grafo de teste direcionado
    g = nx.DiGraph()
    g.add_node("A", contributions=10)
    g.add_node("B", contributions=5)
    g.add_node("C", contributions=2)
    
    # Arestas direcionadas com pesos
    g.add_edge("A", "B", weight=3)
    g.add_edge("B", "C", weight=1)
    g.add_edge("C", "A", weight=2)
    
    # Testar cálculo de centralidades
    centralities = analyzer.calculate_centralities(g)
    assert "A" in centralities
    assert "in_degree" in centralities["A"]
    assert "pagerank" in centralities["A"]
    
    # Testar detecção de comunidades (Louvain)
    communities = analyzer.detect_communities(g)
    assert "A" in communities
    assert "B" in communities
    
    # Testar estatísticas de rede
    metrics = analyzer.get_network_metrics(g)
    assert metrics["nodes"] == 3
    assert metrics["edges"] == 3
    assert metrics["density"] == 0.5  # Para N=3 direcionado, arestas max = 3 * 2 = 6, então densidade é 3/6 = 0.5
    assert metrics["reciprocity"] == 0.0

def test_exporter_runs(tmp_path):
    """Testa se os exportadores salvam arquivos fisicamente sem levantar exceções."""
    g = nx.DiGraph()
    g.add_node("tiangolo", contributions=15)
    g.add_node("dmontagu", contributions=10)
    g.add_edge("dmontagu", "tiangolo", weight=4, comments=4, reviews=0)
    
    centralities = analyzer.calculate_centralities(g)
    communities = analyzer.detect_communities(g)
    
    # Arquivos temporários
    gexf_file = tmp_path / "test.gexf"
    json_file = tmp_path / "test.json"
    csv_file = tmp_path / "test.csv"
    
    # Executar exportadores
    exporter.export_to_gexf(g, gexf_file, centralities, communities)
    exporter.export_to_json(g, json_file, centralities, communities)
    exporter.export_metrics_to_csv(centralities, communities, g, csv_file)
    
    # Verificar se foram gerados
    assert gexf_file.exists()
    assert json_file.exists()
    assert csv_file.exists()
    
    # Garantir que o JSON é parseável
    import json
    with open(json_file, "r") as f:
        data = json.load(f)
        assert "nodes" in data
        assert "links" in data
