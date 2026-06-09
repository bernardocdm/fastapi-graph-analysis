# Roda em: http://localhost:8000
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import networkx as nx

# Path absoluto relativo ao arquivo — funciona independente de onde o script é chamado
DATA_DIR = Path(__file__).parent / "data/outputs"
HOST = "127.0.0.1"
PORT = 8000

app = FastAPI(title="FastAPI Graph Analysis API")

# allow_credentials=True é incompatível com allow_origins=["*"] no spec do CORS
# (causa erro em versões recentes do starlette). Como não usamos cookies/auth,
# basta listar as origens explícitas do Vite dev server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# /api/graph já contém tudo: nós com centralidades + comunidade + arestas.
# Não há centralities.json nem communities.json gerados pelo pipeline —
# esses dados estão embutidos em cada nó do collaboration_graph.json.
@app.get("/api/graph")
def get_graph():
    """Retorna o grafo completo (nós com métricas + arestas)."""
    file_path = DATA_DIR / "collaboration_graph.json"
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Execute primeiro: python main.py --use-mock"
        )
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/api/metrics")
def get_metrics():
    """Retorna métricas globais da rede calculadas do grafo."""
    file_path = DATA_DIR / "collaboration_graph.json"
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Execute primeiro: python main.py --use-mock"
        )
    
    with open(file_path, "r", encoding="utf-8") as f:
        graph_data = json.load(f)
    
    # Reconstruir grafo NetworkX a partir do JSON
    G = nx.node_link_graph(graph_data, directed=True)
    
    # Calcular métricas
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    density = nx.density(G)
    
    # Componentes conexas
    if G.is_directed():
        weak_components = nx.number_weakly_connected_components(G)
        strong_components = nx.number_strongly_connected_components(G)
    else:
        weak_components = nx.number_connected_components(G)
        strong_components = 0
    
    # Diâmetro (apenas se grafo é conexo)
    try:
        if G.is_directed():
            undirected = G.to_undirected()
            diameter = nx.diameter(undirected)
        else:
            diameter = nx.diameter(G)
    except:
        diameter = None
    
    # Reciprocidade
    reciprocity = nx.reciprocity(G) if G.is_directed() else 0
    
    return {
        "num_nodes": num_nodes,
        "num_edges": num_edges,
        "density": round(density, 4),
        "reciprocity": round(reciprocity, 4),
        "diameter": diameter,
        "weakly_connected_components": weak_components,
        "strongly_connected_components": strong_components,
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print(f"  API Server rodando em http://{HOST}:{PORT}")
    print("="*60)
    print("\nEndpoints:")
    print(f"   GET http://{HOST}:{PORT}/api/graph")
    print(f"   GET http://{HOST}:{PORT}/api/metrics")
    print(f"   GET http://{HOST}:{PORT}/health")
    print(f"\nDocs: http://{HOST}:{PORT}/docs\n")
    uvicorn.run(app, host=HOST, port=PORT)
