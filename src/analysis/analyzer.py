import networkx as nx

def calculate_centralities(graph):
    """
    Calcula diversas métricas de centralidade para cada nó no grafo.
    Retorna um dicionário estruturado por nó.
    """
    if len(graph) == 0:
        return {}

    # Usar networkx para calcular as métricas
    in_degree = nx.in_degree_centrality(graph)
    out_degree = nx.out_degree_centrality(graph)
    
    # Betweenness e Closeness
    betweenness = nx.betweenness_centrality(graph)
    closeness = nx.closeness_centrality(graph)
    
    # PageRank ponderado com múltiplos fallbacks robustos
    try:
        pagerank = nx.pagerank(graph, weight="weight")
    except Exception as e:
        print(f"[WARN] Falha ao calcular PageRank ponderado: {e}. Tentando não ponderado...")
        try:
            pagerank = nx.pagerank(graph)
        except Exception as e2:
            print(f"[WARN] Falha crítica no PageRank: {e2}. Usando distribuição uniforme padrão.")
            # Fallback seguro e infalível
            num_nodes = len(graph)
            pagerank = {node: 1.0 / num_nodes for node in graph.nodes()}

    # Combinar tudo em um dicionário estruturado
    metrics = {}
    for node in graph.nodes():
        metrics[node] = {
            "in_degree": in_degree.get(node, 0.0),
            "out_degree": out_degree.get(node, 0.0),
            "betweenness": betweenness.get(node, 0.0),
            "closeness": closeness.get(node, 0.0),
            "pagerank": pagerank.get(node, 0.0)
        }
    
    return metrics

def detect_communities(graph):
    """
    Detecta comunidades no grafo usando o algoritmo de Louvain.
    Como Louvain se aplica a redes não direcionadas, convertemos temporariamente o grafo.
    Retorna um dicionário mapeando cada nó ao ID da sua comunidade (0, 1, 2...).
    """
    if len(graph) == 0:
        return {}
        
    # Converter para não direcionado para compatibilidade com Louvain
    undirected_graph = graph.to_undirected()
    
    try:
        # Detecta comunidades usando NetworkX
        communities_sets = nx.community.louvain_communities(undirected_graph, weight="weight")
        
        # Mapear nós para IDs de comunidade
        node_communities = {}
        for community_id, node_set in enumerate(communities_sets):
            for node in node_set:
                node_communities[node] = community_id
        return node_communities
    except Exception as e:
        print(f"[WARN] Falha na detecção de comunidades Louvain: {e}. Usando partição trivial.")
        return {node: 0 for node in graph.nodes()}

def get_network_metrics(graph):
    """
    Calcula e retorna estatísticas globais da rede.
    Trata grafos desconectados de forma robusta.
    """
    num_nodes = graph.number_of_nodes()
    num_edges = graph.number_of_edges()
    
    if num_nodes == 0:
        return {
            "nodes": 0,
            "edges": 0,
            "density": 0.0,
            "reciprocity": 0.0,
            "weakly_connected_components": 0,
            "strongly_connected_components": 0,
            "average_clustering": 0.0,
            "diameter": 0.0
        }
        
    density = nx.density(graph)
    reciprocity = nx.reciprocity(graph)
    
    # Componentes conectados
    weakly_connected = nx.number_weakly_connected_components(graph)
    strongly_connected = nx.number_strongly_connected_components(graph)
    
    # Coeficiente de agrupamento (clustering) médio convertendo para não direcionado
    average_clustering = nx.average_clustering(graph.to_undirected())
    
    # Calcular diâmetro de forma robusta
    # Diâmetro é a maior distância possível. Se for desconectado, tiramos a maior distância do maior subgrafo conectado.
    diameter = 0.0
    try:
        undirected_copy = graph.to_undirected()
        if nx.is_connected(undirected_copy):
            diameter = float(nx.diameter(undirected_copy))
        else:
            # Pegar o maior componente conectado
            largest_cc = max(nx.connected_components(undirected_copy), key=len)
            subgraph = undirected_copy.subgraph(largest_cc)
            diameter = float(nx.diameter(subgraph))
    except Exception as e:
        print(f"[WARN] Não foi possível calcular o diâmetro da rede: {e}")
        diameter = 0.0
        
    return {
        "nodes": num_nodes,
        "edges": num_edges,
        "density": density,
        "reciprocity": reciprocity,
        "weakly_connected_components": weakly_connected,
        "strongly_connected_components": strongly_connected,
        "average_clustering": average_clustering,
        "diameter": diameter
    }
