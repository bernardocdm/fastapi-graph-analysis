import json
import networkx as nx
from pathlib import Path
from src.config import PROCESSED_DATA_DIR

class CollaborationGraphBuilder:
    """Construtor de grafos de colaboração direcionados e ponderados utilizando NetworkX."""

    def __init__(self, exclude_bots=True):
        self.exclude_bots = exclude_bots
        self.graph = nx.DiGraph()

    def build_from_mined_data(self, data):
        """
        Gera um grafo direcionado com base nos dados obtidos da mineração.
        - Nó: Contribuidor (usuário).
        - Aresta A -> B: Usuário A comentou/revisou um PR/Issue criado por B.
        - Peso: Quantidade de interações de A no conteúdo de B.
        """
        self.graph.clear()
        
        # Juntar issues e PRs para iteração unificada
        items = data.get("issues", []) + data.get("prs", [])
        
        # Dicionários auxiliares de metadados para nós
        user_avatars = {}
        user_types = {}
        user_contributions = {} # Contagem de participações ativas

        # Dicionário temporário para contar interações A -> B
        # Estrutura: {(A, B): {"comments": 0, "reviews": 0}}
        edge_interactions = {}

        def register_user(username, avatar_url, user_type):
            if not username:
                return False
            # Filtro opcional de bots
            if self.exclude_bots and (user_type == "Bot" or "[bot]" in username.lower() or username == "dependabot"):
                return False
            user_avatars[username] = avatar_url
            user_types[username] = user_type
            if username not in user_contributions:
                user_contributions[username] = 0
            return True

        for item in items:
            author = item.get("author")
            author_avatar = item.get("author_avatar", "")
            author_type = item.get("author_type", "User")
            
            # Registrar autor
            if not register_user(author, author_avatar, author_type):
                continue
                
            # Autor ganha 1 ponto por abrir a Issue/PR
            user_contributions[author] += 1
            
            # 1. Processar comentários da Issue/PR
            for comment in item.get("comments", []):
                commenter = comment.get("author")
                commenter_avatar = comment.get("author_avatar", "")
                commenter_type = comment.get("author_type", "User")
                
                if not register_user(commenter, commenter_avatar, commenter_type):
                    continue
                
                # O comentador ganha 1 ponto por interagir
                user_contributions[commenter] += 1
                
                # Ignorar auto-interação (comentando no próprio post)
                if commenter != author:
                    pair = (commenter, author)
                    if pair not in edge_interactions:
                        edge_interactions[pair] = {"comments": 0, "reviews": 0}
                    edge_interactions[pair]["comments"] += 1

            # 2. Processar revisões de PRs
            for review in item.get("reviews", []):
                reviewer = review.get("author")
                reviewer_avatar = review.get("author_avatar", "")
                reviewer_type = review.get("author_type", "User")
                
                if not register_user(reviewer, reviewer_avatar, reviewer_type):
                    continue
                
                # O revisor ganha 1 ponto
                user_contributions[reviewer] += 1
                
                # Ignorar auto-revisão
                if reviewer != author:
                    pair = (reviewer, author)
                    if pair not in edge_interactions:
                        edge_interactions[pair] = {"comments": 0, "reviews": 0}
                    edge_interactions[pair]["reviews"] += 1

        # Adicionar nós com metadados ao grafo
        for username in user_avatars.keys():
            self.graph.add_node(
                username,
                avatar_url=user_avatars[username],
                user_type=user_types[username],
                contributions=user_contributions[username]
            )

        # Adicionar arestas direcionadas com pesos
        for (source, target), metrics in edge_interactions.items():
            # Apenas adicionar se ambos os nós foram registrados com sucesso no grafo
            if source in self.graph and target in self.graph:
                total_weight = metrics["comments"] + metrics["reviews"]
                self.graph.add_edge(
                    source,
                    target,
                    weight=total_weight,
                    comments=metrics["comments"],
                    reviews=metrics["reviews"]
                )

        print(f"[INFO] Grafo construído com {self.graph.number_of_nodes()} nós e {self.graph.number_of_edges()} arestas.")
        return self.graph

    def get_networkx_graph(self):
        """Retorna o objeto nx.DiGraph bruto."""
        return self.graph

    def save_graph_state(self, filepath=None):
        """Salva a estrutura e atributos do grafo atual em um arquivo JSON compatível."""
        path = filepath or PROCESSED_DATA_DIR / "graph_state.json"
        
        # Converter grafo NetworkX em formato de dicionário node-link serializável
        data = nx.node_link_data(self.graph)
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"[INFO] Estado do grafo salvo com sucesso em: {Path(path).name}")

    def load_graph_state(self, filepath=None):
        """Carrega e reconstrói o grafo a partir de um arquivo JSON anteriormente salvo."""
        path = filepath or PROCESSED_DATA_DIR / "graph_state.json"
        
        if not Path(path).exists():
            raise FileNotFoundError(f"Arquivo de estado do grafo não encontrado: {path}")
            
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # Reconstrói o grafo a partir do dicionário formatado
        self.graph = nx.node_link_graph(data)
        print(f"[INFO] Grafo carregado com sucesso contendo {self.graph.number_of_nodes()} nós.")
        return self.graph
