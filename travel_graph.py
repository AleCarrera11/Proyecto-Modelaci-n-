import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.figure import Figure 

class TravelGraph:
    def __init__(self, destinations_data, fares_data):
        self.destinations = destinations_data
        self.fares = fares_data
        self.graph = nx.Graph() 

        if self.destinations:
            for code, data in self.destinations.items():
                self.graph.add_node(code, name=data['name'], requiere_visa=data['requiere_visa'])
        else:
            print("No se pudieron cargar los datos de destinos. El grafo no se inicializará correctamente.")
            
        if self.fares:
            for fare in self.fares:
                origin = fare['origin']
                destination = fare['destination']
                price = fare['price']
                if self.graph.has_node(origin) and self.graph.has_node(destination):
                    self.graph.add_edge(origin, destination, cost=price, stops=1)
                else:
                    print(f"Advertencia: Vuelo de {origin} a {destination} no añadido, uno o ambos aeropuertos no existen en la lista de destinos.")
        else:
            print("No se pudieron cargar los datos de tarifas.")

    def get_filtered_graph(self, has_visa: bool):
        if has_visa:
            return self.graph
        else:
            nodes_without_visa_restriction = [
                node for node, data in self.graph.nodes(data=True)
                if not data.get('requiere_visa', False)
            ]
            filtered_g = self.graph.subgraph(nodes_without_visa_restriction)
            return filtered_g

    def find_shortest_path_cost(self, origin: str, destination: str, has_visa: bool):
        current_graph = self.get_filtered_graph(has_visa)
        
        if origin not in current_graph or destination not in current_graph:
            return None, "Origen o destino no accesible sin visa o no existe."

        try:
            path = nx.dijkstra_path(current_graph, source=origin, target=destination, weight='cost')
            cost = nx.dijkstra_path_length(current_graph, source=origin, target=destination, weight='cost')
            return cost, path
        except nx.NetworkXNoPath:
            return None, "No se encontró una ruta por costo entre los destinos seleccionados."
        except Exception as e:
            return None, f"Error al calcular la ruta por costo: {e}"

    def find_shortest_path_stops(self, origin: str, destination: str, has_visa: bool):
        current_graph = self.get_filtered_graph(has_visa)
        
        if origin not in current_graph or destination not in current_graph:
            return None, "Origen o destino no accesible sin visa o no existe."

        try:
            path = nx.shortest_path(current_graph, source=origin, target=destination)
            stops = len(path) - 1
            return stops, path
        except nx.NetworkXNoPath:
            return None, "No se encontró una ruta por escalas entre los destinos seleccionados."
        except Exception as e:
            return None, f"Error al calcular la ruta por escalas: {e}"

    def draw_graph_with_path(self, origin_node, destination_node, path_nodes=None, has_visa=True) -> Figure:
        """
        Dibuja el grafo, resaltando una ruta si se proporciona.
        Retorna el objeto Figure de Matplotlib para ser incrustado en Tkinter.
        """
        graph_to_draw = self.get_filtered_graph(has_visa)
        
        pos = nx.spring_layout(graph_to_draw, seed=42, k=0.9, iterations=50) 
        
        
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.clear()

        all_nodes = list(self.graph.nodes()) 
        visa_required_nodes = [node for node, data in self.graph.nodes(data=True) if data.get('requiere_visa', False)]
        
        current_nodes = list(graph_to_draw.nodes())
        
        
        node_colors = []
        for node in current_nodes:
            if node == origin_node:
                node_colors.append('lightgreen') # Origen
            elif node == destination_node:
                node_colors.append('salmon') # Destino
            elif self.destinations[node]['requiere_visa']:
                node_colors.append('lightblue') # Nodos con visa (accesibles si tiene visa)
            else:
                node_colors.append('lightgray') # Otros nodos

        # Dibujar todos los nodos accesibles
        nx.draw_networkx_nodes(graph_to_draw, pos, nodelist=current_nodes, 
                               node_color=node_colors, node_size=1000, ax=ax, edgecolors='black')
        
        # Dibujar aristas generales
        nx.draw_networkx_edges(graph_to_draw, pos, edgelist=graph_to_draw.edges(), 
                               width=1.0, alpha=0.5, edge_color='gray', ax=ax)

        # Resaltar la ruta si se proporciona
        if path_nodes:
            path_edges = [(path_nodes[i], path_nodes[i+1]) for i in range(len(path_nodes)-1)]

            path_edges_undirected = []
            for u, v in path_edges:
                if graph_to_draw.has_edge(u,v):
                    path_edges_undirected.append((u,v))
                elif graph_to_draw.has_edge(v,u): 
                    path_edges_undirected.append((v,u))

            nx.draw_networkx_edges(graph_to_draw, pos, edgelist=path_edges_undirected, 
                                   width=3.0, edge_color='red', ax=ax)
            
            # Resaltar los nodos de la ruta
            nx.draw_networkx_nodes(graph_to_draw, pos, nodelist=path_nodes, node_color='gold', node_size=1200, ax=ax, edgecolors='black')
            # Asegura de que el origen y destino siguen resaltados
            if origin_node in path_nodes:
                nx.draw_networkx_nodes(graph_to_draw, pos, nodelist=[origin_node], node_color='lightgreen', node_size=1200, ax=ax, edgecolors='black')
            if destination_node in path_nodes:
                nx.draw_networkx_nodes(graph_to_draw, pos, nodelist=[destination_node], node_color='salmon', node_size=1200, ax=ax, edgecolors='black')

        # Etiquetas de nodos
        nx.draw_networkx_labels(graph_to_draw, pos, font_size=9, font_weight='bold', ax=ax)

        # Mostrar pesos de las aristas (costo o paradas)
        edge_labels = nx.get_edge_attributes(graph_to_draw, 'cost') 
        nx.draw_networkx_edge_labels(graph_to_draw, pos, edge_labels=edge_labels, font_size=8, ax=ax)

        ax.set_title("Grafo de Rutas de Metro Travel")
        ax.set_axis_on() 
        plt.tight_layout() 
        
        return fig 