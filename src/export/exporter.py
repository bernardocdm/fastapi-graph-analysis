import csv
import json
import copy
import networkx as nx
from pathlib import Path
from src.config import OUTPUT_DATA_DIR

def _prepare_augmented_graph(graph, centralities=None, communities=None):
    """
    Cria uma cópia profunda do grafo e adiciona as métricas calculadas como
    atributos dos nós para que sejam salvas no arquivo final de exportação.
    """
    augmented = copy.deepcopy(graph)
    
    # Adicionar métricas aos nós se fornecidas
    for node in augmented.nodes():
        if centralities and node in centralities:
            node_metrics = centralities[node]
            augmented.nodes[node]["in_degree"] = float(node_metrics.get("in_degree", 0.0))
            augmented.nodes[node]["out_degree"] = float(node_metrics.get("out_degree", 0.0))
            augmented.nodes[node]["betweenness"] = float(node_metrics.get("betweenness", 0.0))
            augmented.nodes[node]["closeness"] = float(node_metrics.get("closeness", 0.0))
            augmented.nodes[node]["pagerank"] = float(node_metrics.get("pagerank", 0.0))
            
        if communities and node in communities:
            augmented.nodes[node]["community"] = int(communities[node])
            
    return augmented

def export_to_gexf(graph, filepath=None, centralities=None, communities=None):
    """
    Exporta o grafo no formato GEXF, ideal para visualização avançada no Gephi.
    Garante que todas as métricas de centralidade e comunidade sejam embutidas no XML.
    """
    path = filepath or OUTPUT_DATA_DIR / "collaboration_graph.gexf"
    
    # Preparar grafo com atributos enriquecidos
    enriched_graph = _prepare_augmented_graph(graph, centralities, communities)
    
    # Salvar em formato GEXF
    nx.write_gexf(enriched_graph, path)
    print(f"[INFO] Grafo exportado com sucesso no formato Gephi (GEXF) em: {Path(path).name}")
    return path

def export_to_json(graph, filepath=None, centralities=None, communities=None):
    """
    Exporta o grafo em formato JSON (node-link), excelente para visualização web com D3.js ou Vis.js.
    """
    path = filepath or OUTPUT_DATA_DIR / "collaboration_graph.json"
    
    enriched_graph = _prepare_augmented_graph(graph, centralities, communities)
    
    data = nx.node_link_data(enriched_graph)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"[INFO] Grafo exportado com sucesso no formato JSON em: {Path(path).name}")
    return path

def export_metrics_to_csv(centralities, communities, graph, filepath=None):
    """
    Exporta a tabela comparativa de métricas de todos os contribuidores em formato CSV.
    """
    path = filepath or OUTPUT_DATA_DIR / "collaboration_metrics.csv"
    
    headers = [
        "Username", 
        "Contributions", 
        "InDegreeCentrality", 
        "OutDegreeCentrality", 
        "BetweennessCentrality", 
        "ClosenessCentrality", 
        "PageRank", 
        "CommunityID"
    ]
    
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for username in graph.nodes():
            node_data = graph.nodes[username]
            contributions = node_data.get("contributions", 0)
            
            c_data = centralities.get(username, {})
            in_deg = c_data.get("in_degree", 0.0)
            out_deg = c_data.get("out_degree", 0.0)
            between = c_data.get("betweenness", 0.0)
            closeness = c_data.get("closeness", 0.0)
            p_rank = c_data.get("pagerank", 0.0)
            
            comm_id = communities.get(username, 0)
            
            writer.writerow([
                username,
                contributions,
                f"{in_deg:.6f}",
                f"{out_deg:.6f}",
                f"{between:.6f}",
                f"{closeness:.6f}",
                f"{p_rank:.6f}",
                comm_id
            ])
            
    print(f"[INFO] Métricas comparativas exportadas com sucesso em formato CSV em: {Path(path).name}")
    return path
