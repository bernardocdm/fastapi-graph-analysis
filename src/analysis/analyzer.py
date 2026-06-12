from collections import deque
from src.graph.api import AbstractGraph


# ── Centralidades ─────────────────────────────────────────────────────────────

def _bfs_distances(graph: AbstractGraph, source: int) -> dict:
    """
    BFS a partir de 'source' no grafo direcionado.
    Retorna {nó: distância_mínima} para todos os nós alcançáveis.
    """
    dist = {source: 0}
    queue = deque([source])
    while queue:
        v = queue.popleft()
        for w in range(graph.getVertexCount()):
            if w not in dist and graph.hasEdge(v, w):
                dist[w] = dist[v] + 1
                queue.append(w)
    return dist


def _betweenness_brandes(graph: AbstractGraph) -> dict:
    """
    Algoritmo de Brandes (2001) para betweenness centrality em O(V·E).
    Retorna {índice: valor_normalizado} para grafo direcionado.
    """
    n = graph.getVertexCount()
    betweenness = {i: 0.0 for i in range(n)}

    for s in range(n):
        stack = []
        pred = {i: [] for i in range(n)}
        sigma = [0] * n
        dist  = [-1]  * n
        sigma[s] = 1
        dist[s]  = 0
        queue = deque([s])

        while queue:
            v = queue.popleft()
            stack.append(v)
            for w in range(n):
                if graph.hasEdge(v, w):
                    if dist[w] < 0:           # primeira visita
                        dist[w] = dist[v] + 1
                        queue.append(w)
                    if dist[w] == dist[v] + 1:
                        sigma[w] += sigma[v]
                        pred[w].append(v)

        delta = [0.0] * n
        while stack:
            w = stack.pop()
            for v in pred[w]:
                if sigma[w] > 0:
                    delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
            if w != s:
                betweenness[w] += delta[w]

    # Normalização para grafo direcionado: (n-1)(n-2)
    norm = (n - 1) * (n - 2)
    if norm > 0:
        for i in range(n):
            betweenness[i] /= norm

    return betweenness


def _closeness(graph: AbstractGraph) -> dict:
    """
    Closeness centrality com fórmula de Wasserman & Faust para grafos desconexos.
    Retorna {índice: valor} para grafo direcionado.
    """
    n = graph.getVertexCount()
    closeness = {}

    for s in range(n):
        dist = _bfs_distances(graph, s)
        reachable  = len(dist) - 1          # exclui o próprio nó
        total_dist = sum(dist.values())

        if reachable > 0 and total_dist > 0:
            # Normaliza para componentes parcialmente conectados
            closeness[s] = (reachable ** 2) / ((n - 1) * total_dist)
        else:
            closeness[s] = 0.0

    return closeness


def calculate_centralities(graph: AbstractGraph) -> dict:
    """
    Calcula todas as métricas de centralidade exigidas no trabalho:
      - Degree (in/out), normalizado
      - Betweenness (Brandes)
      - Closeness (Wasserman & Faust)
      - PageRank (Power Iteration, d=0.85, 100 iterações)

    Retorna: {username: {in_degree, out_degree, betweenness, closeness, pagerank}}
    """
    n = graph.getVertexCount()
    if n == 0:
        return {}

    # 1. Degrees
    metrics = {}
    for i in range(n):
        metrics[i] = {
            "in_degree":   graph.getVertexInDegree(i)  / max(1, n - 1),
            "out_degree":  graph.getVertexOutDegree(i) / max(1, n - 1),
            "betweenness": 0.0,
            "closeness":   0.0,
            "pagerank":    1.0 / n
        }

    # 2. PageRank — Power Iteration
    d = 0.85
    for _ in range(100):
        new_pr = [0.0] * n
        for i in range(n):
            acc = 0.0
            for j in range(n):
                if graph.hasEdge(j, i):
                    out_j = graph.getVertexOutDegree(j)
                    if out_j > 0:
                        acc += metrics[j]["pagerank"] / out_j
            new_pr[i] = (1.0 - d) / n + d * acc
        for i in range(n):
            metrics[i]["pagerank"] = new_pr[i]

    # 3. Betweenness (Brandes)
    btw = _betweenness_brandes(graph)
    for i in range(n):
        metrics[i]["betweenness"] = btw[i]

    # 4. Closeness
    cls = _closeness(graph)
    for i in range(n):
        metrics[i]["closeness"] = cls[i]

    # Converter chaves int → username
    return {graph.getVertexLabel(i): metrics[i] for i in range(n)}


# ── Detecção de comunidades ───────────────────────────────────────────────────

def detect_communities(graph: AbstractGraph) -> dict:
    """
    Detecta comunidades via Label Propagation (sem networkx).
    Versão não-direcionada: considera vizinhos em qualquer direção.
    20 iterações para maior estabilidade.

    Retorna: {username: community_id}
    """
    n = graph.getVertexCount()
    if n == 0:
        return {}

    labels = list(range(n))

    for _ in range(20):
        changed = False
        order = list(range(n))

        for i in order:
            freq = {}
            for j in range(n):
                if graph.hasEdge(i, j) or graph.hasEdge(j, i):
                    lbl = labels[j]
                    freq[lbl] = freq.get(lbl, 0) + 1

            if freq:
                best = max(freq, key=lambda k: (freq[k], -k))  # desempate pelo menor id
                if best != labels[i]:
                    labels[i] = best
                    changed = True

        if not changed:
            break

    # Renumerar comunidades sequencialmente (0, 1, 2, ...)
    unique = sorted(set(labels))
    remap = {old: new for new, old in enumerate(unique)}
    labels = [remap[l] for l in labels]

    return {graph.getVertexLabel(i): labels[i] for i in range(n)}


# ── Métricas globais da rede ──────────────────────────────────────────────────

def _clustering_coefficient(graph: AbstractGraph):
    """
    Coeficiente de agrupamento local (versão não-direcionada sobre grafo direcionado).
    Retorna (dict {índice: coef}, média_global).
    """
    n = graph.getVertexCount()
    clustering = {}

    for i in range(n):
        neighbors = [j for j in range(n)
                     if j != i and (graph.hasEdge(i, j) or graph.hasEdge(j, i))]
        k = len(neighbors)
        if k < 2:
            clustering[i] = 0.0
            continue

        triangles = sum(
            1
            for a in range(len(neighbors))
            for b in range(a + 1, len(neighbors))
            if graph.hasEdge(neighbors[a], neighbors[b])
            or graph.hasEdge(neighbors[b], neighbors[a])
        )
        clustering[i] = (2 * triangles) / (k * (k - 1))

    avg = sum(clustering.values()) / n if n > 0 else 0.0
    return clustering, avg


def _assortativity(graph: AbstractGraph) -> float:
    """
    Assortatividade de grau (degree assortativity).
    Valores: > 0 (hubs conectam-se entre si), < 0 (dissortativo), ~ 0 (aleatório).
    """
    n = graph.getVertexCount()
    edges = [(i, j) for i in range(n) for j in range(n) if graph.hasEdge(i, j)]
    if not edges:
        return 0.0

    degrees = [graph.getVertexInDegree(i) + graph.getVertexOutDegree(i) for i in range(n)]
    m = len(edges)

    sum_ij = sum(degrees[i] * degrees[j] for i, j in edges)
    sum_i  = sum(degrees[i] for i, j in edges)
    sum_j  = sum(degrees[j] for i, j in edges)
    sum_sq = sum(degrees[i] ** 2 + degrees[j] ** 2 for i, j in edges)

    numerator   = (sum_ij / m) - (sum_i / m) * (sum_j / m)
    denominator = (sum_sq / (2 * m)) - ((sum_i + sum_j) / (2 * m)) ** 2

    return numerator / denominator if denominator != 0 else 0.0


def _weakly_connected_components(graph: AbstractGraph) -> int:
    """Conta componentes fracamente conexos via BFS não-direcionado."""
    n = graph.getVertexCount()
    visited = [False] * n
    count = 0

    for start in range(n):
        if visited[start]:
            continue
        count += 1
        queue = deque([start])
        visited[start] = True
        while queue:
            v = queue.popleft()
            for w in range(n):
                if not visited[w] and (graph.hasEdge(v, w) or graph.hasEdge(w, v)):
                    visited[w] = True
                    queue.append(w)

    return count


def _strongly_connected_components(graph: AbstractGraph) -> int:
    """Conta componentes fortemente conexos via algoritmo de Kosaraju."""
    n = graph.getVertexCount()

    # Passo 1: DFS no grafo original → pilha de finish order
    visited = [False] * n
    finish_stack = []

    def dfs1(v):
        stack = [(v, False)]
        while stack:
            node, returning = stack.pop()
            if returning:
                finish_stack.append(node)
                continue
            if visited[node]:
                continue
            visited[node] = True
            stack.append((node, True))
            for w in range(n):
                if not visited[w] and graph.hasEdge(node, w):
                    stack.append((w, False))

    for i in range(n):
        if not visited[i]:
            dfs1(i)

    # Passo 2: DFS no grafo transposto seguindo a pilha
    visited2 = [False] * n
    count = 0

    def dfs2(v):
        stack = [v]
        while stack:
            node = stack.pop()
            if visited2[node]:
                continue
            visited2[node] = True
            for w in range(n):
                if not visited2[w] and graph.hasEdge(w, node):  # transposto
                    stack.append(w)

    while finish_stack:
        v = finish_stack.pop()
        if not visited2[v]:
            dfs2(v)
            count += 1

    return count


def _network_diameter(graph: AbstractGraph) -> float:
    """
    Diâmetro da rede: maior distância mínima entre qualquer par de nós alcançáveis.
    Retorna 0 se o grafo não tiver arestas.
    """
    n = graph.getVertexCount()
    max_dist = 0

    for s in range(n):
        dist = _bfs_distances(graph, s)
        if dist:
            local_max = max(dist.values())
            if local_max > max_dist:
                max_dist = local_max

    return float(max_dist)


def get_network_metrics(graph: AbstractGraph) -> dict:
    """
    Compila todas as métricas globais da rede exigidas na Etapa 3.

    Retorna:
        nodes, edges, density, reciprocity,
        weakly_connected_components, strongly_connected_components,
        average_clustering, assortativity, diameter
    """
    n = graph.getVertexCount()
    e = graph.getEdgeCount()

    if n <= 1:
        return {
            "nodes": n, "edges": e,
            "density": 0.0, "reciprocity": 0.0,
            "weakly_connected_components":  1,
            "strongly_connected_components": 1,
            "average_clustering": 0.0,
            "assortativity": 0.0,
            "diameter": 0.0
        }

    max_edges = n * (n - 1)
    density = e / max_edges if max_edges > 0 else 0.0

    mutual = sum(
        1 for i in range(n) for j in range(n)
        if i != j and graph.hasEdge(i, j) and graph.hasEdge(j, i)
    )
    reciprocity = mutual / e if e > 0 else 0.0

    _, avg_clustering = _clustering_coefficient(graph)
    assortativity    = _assortativity(graph)
    wcc              = _weakly_connected_components(graph)
    scc              = _strongly_connected_components(graph)
    diameter         = _network_diameter(graph)

    return {
        "nodes":   n,
        "edges":   e,
        "density": density,
        "reciprocity": reciprocity,
        "weakly_connected_components":  wcc,
        "strongly_connected_components": scc,
        "average_clustering": avg_clustering,
        "assortativity": assortativity,
        "diameter": diameter
    }