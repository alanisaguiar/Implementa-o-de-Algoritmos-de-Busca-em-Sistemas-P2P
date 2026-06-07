import json
import random
import time               
from collections import deque
import networkx as nx
import matplotlib.pyplot as plt

class Node:
    def __init__(self, node_id, resources):
        self.id = node_id
        self.resources = set(resources)
        self.neighbors = [] # Lista de objetos Node vizinhos
        self.cache = {} # Cache para busca informada: { 'recurso_X': 'no_Y' }

    def add_neighbor(self, neighbor):
        if neighbor not in self.neighbors:
            self.neighbors.append(neighbor)

class P2PNetwork:
    def __init__(self, config_file):
        self.nodes = {} # Dicionário { 'n1': NodeObj, ... }
        self.config = self.load_config(config_file)
        self.build_network()
        self.validate_network()

    def load_config(self, filename):
        with open(filename, 'r') as f:
            return json.load(f)

    def build_network(self):
        # 1. Criar Nós
        res_map = self.config['resources']
        for node_id, resources in res_map.items():
            self.nodes[node_id] = Node(node_id, resources)

        # 2. Criar Arestas (Conexões)
        edges = self.config['edges']
        for u, v in edges:
            if u in self.nodes and v in self.nodes:
                self.nodes[u].add_neighbor(self.nodes[v])
                self.nodes[v].add_neighbor(self.nodes[u]) # Grafo não direcionado

    def validate_network(self):
        print("Validando a rede...")
        # REQUISITO 4: Não pode haver arestas de um nó para ele mesmo (self-loop)
        for u, v in self.config['edges']:
            if u == v:
                raise ValueError(f"Aresta inválida: o nó {u} tem uma aresta para ele mesmo (self-loop)!")

        # REQUISITO 2: Min/Max Neighbors 
        min_n = self.config['min_neighbors']
        max_n = self.config['max_neighbors']
        
        for node in self.nodes.values():
            if not (min_n <= len(node.neighbors) <= max_n):
                raise ValueError(f"Nó {node.id} viola limites de vizinhos! Tem {len(node.neighbors)}, esperado [{min_n}-{max_n}]")
            
            # REQUISITO 3: Nós sem recursos 
            if not node.resources:
                raise ValueError(f"Nó {node.id} não possui recursos!")

        # REQUISITO 1: Rede Particionada (BFS para verificar conectividade) 
        if not self.is_connected():
            raise ValueError("A rede está particionada (desconectada)!")
        
        print("Rede validada com sucesso! ✅")

    def is_connected(self):
        """Verifica se existe caminho de qualquer nó para qualquer nó"""
        if not self.nodes: return True
        
        start_node = next(iter(self.nodes.values()))
        visited = set()
        queue = deque([start_node])
        visited.add(start_node.id)

        while queue:
            current = queue.popleft()
            for neighbor in current.neighbors:
                if neighbor.id not in visited:
                    visited.add(neighbor.id)
                    queue.append(neighbor)
        
        return len(visited) == len(self.nodes)

    def _shortest_path(self, start_id, target_id):
        """Retorna a lista de nós no caminho mais curto entre dois nós (BFS).
        Usado pela busca informada para simular o custo real (em mensagens)
        de chegar até o nó que possui o recurso."""
        if start_id == target_id:
            return [start_id]
        visited = {start_id}
        # Cada item da fila guarda o caminho percorrido até aquele nó
        queue = deque([[start_id]])
        while queue:
            path = queue.popleft()
            current = path[-1]
            for neighbor in self.nodes[current].neighbors:
                if neighbor.id == target_id:
                    return path + [neighbor.id]
                if neighbor.id not in visited:
                    visited.add(neighbor.id)
                    queue.append(path + [neighbor.id])
        return None  # Não há caminho (rede particionada)

    # --- NOVO MÉTODO: VISUALIZAÇÃO ---
    def draw_network(self):
        """Desenha a topologia da rede usando NetworkX."""
        print("Gerando gráfico da rede...")
        G = nx.Graph()
        
        # Adiciona nós e arestas ao grafo visual
        for node in self.nodes.values():
            G.add_node(node.id, resources=list(node.resources))
            for neighbor in node.neighbors:
                G.add_edge(node.id, neighbor.id)
        
        plt.figure(figsize=(8, 6))
        # Layout spring tenta deixar os nós espaçados visualmente
        pos = nx.spring_layout(G, seed=42) 
        
        # Desenha os nós
        nx.draw_networkx_nodes(G, pos, node_size=700, node_color='skyblue')
        
        # Desenha as arestas
        nx.draw_networkx_edges(G, pos, width=2, alpha=0.5, edge_color='gray')
        
        # Desenha os nomes (Labels)
        nx.draw_networkx_labels(G, pos, font_size=12, font_family='sans-serif', font_weight='bold')
        
        # Mostra os recursos como rótulos pequenos (opcional)
        labels_res = {n: f"\n\n{attr['resources']}" for n, attr in G.nodes(data=True)}
        nx.draw_networkx_labels(G, pos, labels=labels_res, font_size=8, font_color='darkblue')

        plt.title("Topologia da Rede P2P")
        plt.axis('off')
        plt.show() # Abre a janela com o desenho

    # --- MÉTODOS DE ANIMAÇÃO ---

    def animate_search(self, start_node_id, resource_name, ttl, algorithm):
        """Prepara o ambiente gráfico e chama a animação específica."""
        print(f"\n🎥 Iniciando ANIMAÇÃO ({algorithm}) por '{resource_name}'...")
        
        # 1. Configura o Grafo Visual (uma única vez)
        self.G_visual = nx.Graph()
        for node in self.nodes.values():
            self.G_visual.add_node(node.id)
            for neighbor in node.neighbors:
                self.G_visual.add_edge(node.id, neighbor.id)
        
        # Define posições fixas para os nós não ficarem pulando
        self.pos_visual = nx.spring_layout(self.G_visual, seed=42)
        
        # Abre a janela interativa
        plt.ion() 
        plt.figure(figsize=(8, 6))
        
        # 2. Escolhe o algoritmo visual
        base_algo = algorithm.replace("informed_", "")
        start_node = self.nodes[start_node_id]
        
        if base_algo == 'flooding':
            self._animate_flooding(start_node, resource_name, ttl)
        elif base_algo == 'random_walk':
            self._animate_random_walk(start_node, resource_name, ttl)
        
        plt.ioff() # Desliga o modo interativo
        plt.show() # Mantém a janela aberta no final

    def _update_plot(self, current_id=None, visited=None, found_id=None):
        """Função auxiliar para repintar a tela."""
        plt.clf() # Limpa a tela
        
        # Define cores
        node_colors = []
        for node in self.G_visual.nodes():
            if node == found_id:
                node_colors.append('green') # Achou!
            elif node == current_id:
                node_colors.append('orange') # Nó atual (sendo processado)
            elif visited and node in visited:
                node_colors.append('gray')   # Já visitado
            else:
                node_colors.append('skyblue') # Não visitado
        
        # Desenha
        nx.draw(self.G_visual, self.pos_visual, node_color=node_colors, with_labels=True, node_size=800)
        plt.title(f"Buscando... (Laranja=Atual, Cinza=Visitado, Verde=Achou)")
        plt.draw()
        plt.pause(0.8) # Pausa de 0.8 segundos para você ver a animação

    def _animate_flooding(self, start_node, resource_name, ttl):
        queue = deque([(start_node, ttl)])
        visited = set([start_node.id])
        
        while queue:
            current_node, current_ttl = queue.popleft()
            
            # ATUALIZA O GRÁFICO (Nó atual laranja)
            self._update_plot(current_id=current_node.id, visited=visited)
            
            # Verifica sucesso
            if resource_name in current_node.resources:
                print(f"✅ Visual: Recurso encontrado em {current_node.id}!")
                self._update_plot(found_id=current_node.id, visited=visited) # Pinta de verde
                return

            # Espalha para vizinhos
            if current_ttl > 0:
                for neighbor in current_node.neighbors:
                    if neighbor.id not in visited:
                        visited.add(neighbor.id)
                        queue.append((neighbor, current_ttl - 1))

    def _animate_random_walk(self, start_node, resource_name, ttl):
        current_node = start_node
        visited = set([start_node.id])
        
        while ttl >= 0:
            # ATUALIZA O GRÁFICO
            self._update_plot(current_id=current_node.id, visited=visited)
            
            if resource_name in current_node.resources:
                print(f"✅ Visual: Recurso encontrado em {current_node.id}!")
                self._update_plot(found_id=current_node.id, visited=visited)
                return

            if ttl == 0 or not current_node.neighbors:
                break
                
            next_node = random.choice(current_node.neighbors)
            ttl -= 1
            current_node = next_node
            visited.add(current_node.id)

    # --- ALGORITMOS DE BUSCA ---

    def search(self, start_node_id, resource_name, ttl, algorithm):
        start_node = self.nodes.get(start_node_id)
        if not start_node:
            raise ValueError(f"Nó inicial {start_node_id} não existe.")

        print(f"\n--- Iniciando Busca ({algorithm}) por '{resource_name}' (TTL: {ttl}) ---")

        # 1. Lógica da Busca Informada (Verificar Cache do nó inicial)
        is_informed = "informed" in algorithm
        
        if is_informed and resource_name in start_node.cache:
            known_location = start_node.cache[resource_name]
            print(f"💡 Cache Hit! O nó {start_node.id} já sabe que '{resource_name}' está em {known_location}.")
            
            caminho = self._shortest_path(start_node.id, known_location)
            return {
                "sucesso": True,
                "nó_destino": known_location,
                "mensagens": len(caminho) - 1,
                "nós_envolvidos": len(caminho)
            }

        # 2. Executa o algoritmo base se não achou no cache
        result = None
        base_algo = algorithm.replace("informed_", "") # flooding ou random_walk

        if base_algo == 'flooding':
            result = self._algo_flooding(start_node, resource_name, ttl)
        elif base_algo == 'random_walk':
            result = self._algo_random_walk(start_node, resource_name, ttl, is_informed)
        else:
            print(f"Algoritmo base '{base_algo}' desconhecido.")
            return None

        # 3. Aprendizado (Atualizar Cache)
        if is_informed and result["sucesso"]:
            target_id = result["nó_destino"]

            nos_que_aprendem = result.get("conjunto_nos", {start_node.id})
            for node_id in nos_que_aprendem:
                self.nodes[node_id].cache[resource_name] = target_id
            print(f"🧠 Aprendizado! {len(nos_que_aprendem)} nó(s) salvaram '{resource_name}' -> {target_id} no cache.")

        return result

    def _algo_flooding(self, start_node, resource_name, ttl):

        queue = deque([(start_node, ttl)])
        visited = set([start_node.id])
        msgs_count = 0
        nodes_involved = set([start_node.id])
        found = False
        target_node = None

        while queue:
            current_node, current_ttl = queue.popleft()
            if resource_name in current_node.resources:
                found = True
                target_node = current_node
                print(f"✅ Recurso encontrado no nó {current_node.id}!")
                break
            if current_ttl > 0:
                for neighbor in current_node.neighbors:
                    if neighbor.id not in visited:
                        msgs_count += 1
                        nodes_involved.add(neighbor.id)
                        visited.add(neighbor.id)
                        queue.append((neighbor, current_ttl - 1))
        
        return {"sucesso": found, "nó_destino": target_node.id if target_node else None, 
                "mensagens": msgs_count, "nós_envolvidos": len(nodes_involved),
                "conjunto_nos": nodes_involved}

    def _algo_random_walk(self, start_node, resource_name, ttl, is_informed=False):

        current_node = start_node
        msgs_count = 0
        nodes_involved = set([start_node.id])
        found = False
        target_id = None

        while ttl >= 0:
            # O nó atual tem o recurso?
            if resource_name in current_node.resources:
                found = True
                target_id = current_node.id
                print(f"✅ Recurso encontrado no nó {current_node.id}!")
                break

            if is_informed and resource_name in current_node.cache:
                destino = current_node.cache[resource_name]
                print(f"💡 Nó {current_node.id} consultou o cache: '{resource_name}' está em {destino}.")
                caminho = self._shortest_path(current_node.id, destino)
                msgs_count += len(caminho) - 1
                for nid in caminho:
                    nodes_involved.add(nid)
                found = True
                target_id = destino
                break

            if ttl == 0:
                break
            if not current_node.neighbors:
                break
            next_node = random.choice(current_node.neighbors)
            msgs_count += 1
            ttl -= 1
            current_node = next_node
            nodes_involved.add(current_node.id)

        return {"sucesso": found, "nó_destino": target_id,
                "mensagens": msgs_count, "nós_envolvidos": len(nodes_involved),
                "conjunto_nos": nodes_involved}

# --- TESTE COM ANIMAÇÃO ---
if __name__ == "__main__":
    try:
        rede = P2PNetwork("rede_teste.json")
        print(f"Rede montada com {len(rede.nodes)} nós.")

        print("\n--- Teste Rápido de Lógica ---")
        rede.search("n1", "r6", ttl=5, algorithm="flooding")

        
        input("\nPressione ENTER para ver a animação de FLOODING...")
        rede.animate_search("n1", "r6", ttl=4, algorithm="flooding")

    except Exception as e:
        print(f"Erro: {e}")