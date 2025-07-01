import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from data_loader import read_destinations, read_fares
from travel_graph import TravelGraph

# Importar para incrustar Matplotlib en Tkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib

# Configuración de customtkinter
ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

# matplotlib.use('Agg')
class MetroTravelApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Metro Travel - Optimizador de Viajes al Caribe")
        self.geometry("1000x800") 

        # Configurar el protocolo de cierre de la ventana
        self.protocol("WM_DELETE_WINDOW", self.on_closing) 

        # Cargar datos al inicio de la aplicación
        self.destinations_data = read_destinations()
        self.fares_data = read_fares()

        if self.destinations_data is None or self.fares_data is None:
            messagebox.showerror("Error de Carga", "Error al cargar los datos. Asegúrate de que 'destinos.txt' y 'tarifas.txt' existan y estén correctamente formateados.")
            self.destroy() 
            return

        self.travel_graph_instance = TravelGraph(self.destinations_data, self.fares_data)

        # Obtener la lista de códigos de aeropuerto para los comboboxes
        self.airport_codes = sorted(list(self.destinations_data.keys()))

        self.create_widgets()
        self.draw_initial_graph() 

    def on_closing(self):
        """
        Maneja el evento de cierre de la ventana (cuando se presiona la 'X').
        Asegura que todos los recursos de Tkinter/CustomTkinter se liberen correctamente.
        """
        if messagebox.askokcancel("Cerrar Aplicación", "¿Estás seguro de que quieres salir?"):
            
            plt.close('all') 
            self.quit() 
            self.destroy() 

    def create_widgets(self):
        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Título
        title_label = ctk.CTkLabel(main_frame, text="Optimiza tu Viaje con Metro Travel", font=("Arial", 20, "bold"))
        title_label.pack(pady=10)

        # Frame para controles de entrada y resultados
        controls_results_frame = ctk.CTkFrame(main_frame)
        controls_results_frame.pack(pady=5, padx=5, fill="x")
        controls_results_frame.columnconfigure(0, weight=1)
        controls_results_frame.columnconfigure(1, weight=2)

        # Controles de entrada (izquierda)
        input_frame = ctk.CTkFrame(controls_results_frame)
        input_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        input_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(input_frame, text="Origen:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.origin_combobox = ctk.CTkComboBox(input_frame, values=self.airport_codes)
        self.origin_combobox.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.origin_combobox.set("CCS") 

        ctk.CTkLabel(input_frame, text="Destino:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.destination_combobox = ctk.CTkComboBox(input_frame, values=self.airport_codes)
        self.destination_combobox.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        self.visa_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(input_frame, text="Tengo Visa", variable=self.visa_var, 
                        command=self.on_visa_checkbox_toggle).grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        input_frame.grid_columnconfigure(1, weight=1)

        # Botones de acción
        button_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        cost_button = ctk.CTkButton(button_frame, text="Ruta más Barata", command=self.find_cheapest_route)
        cost_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        stops_button = ctk.CTkButton(button_frame, text="Menos Escalas", command=self.find_fewest_stops_route)
        stops_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Área de resultados
        results_frame = ctk.CTkFrame(controls_results_frame)
        results_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        results_frame.pack_propagate(False) 

        self.results_label = ctk.CTkLabel(results_frame, text="Resultados:", font=("Arial", 14, "bold"))
        self.results_label.pack(pady=5)

        self.path_text = ctk.CTkTextbox(results_frame, height=100, width=300, wrap="word")
        self.path_text.pack(pady=5, padx=5, fill="both", expand=True)
        self.path_text.insert("0.0", "Selecciona Origen y Destino, luego elige una opción de búsqueda.")
        self.path_text.configure(state="disabled") 

        #Área para el gráfico
        self.graph_frame = ctk.CTkFrame(main_frame, width=600, height=400) 
        self.graph_frame.pack(pady=10, padx=10, fill="both", expand=True)
        self.graph_frame.pack_propagate(False) 
        
        self.canvas = None 
        self.toolbar = None 

    def draw_graph(self, origin=None, destination=None, path=None):
        """
        Dibuja el grafo en la interfaz de usuario.
        """
        # Eliminar el gráfico anterior si existe
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            plt.close(self.canvas.figure) 
        if self.toolbar:
            self.toolbar.destroy()

        fig = self.travel_graph_instance.draw_graph_with_path(
            origin_node=origin, 
            destination_node=destination, 
            path_nodes=path, 
            has_visa=self.visa_var.get()
        )

        self.canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas.draw()

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.graph_frame)
        self.toolbar.update()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def draw_initial_graph(self):
        """Dibuja el grafo completo al iniciar la aplicación."""
        self.draw_graph(origin=None, destination=None, path=None)

    def on_visa_checkbox_toggle(self):
        """
        Función llamada cuando el checkbox 'Tengo Visa' cambia de estado.
        Redibuja el grafo para reflejar las nuevas restricciones.
        """
        self.path_text.configure(state="normal")
        self.path_text.delete("0.0", "end")
        self.path_text.insert("0.0", "El estado de la visa ha cambiado. Recalcula la ruta.")
        self.path_text.configure(state="disabled")

        self.draw_graph(origin=None, destination=None, path=None)

    def update_results_display(self, result_type, value, path_list, extra_routes=None):
        self.path_text.configure(state="normal")
        self.path_text.delete("0.0", "end")
        if value is None:
            self.path_text.insert("0.0", path_list) 
        else:
            path_str = " -> ".join(path_list)
            if result_type == "costo":
                self.path_text.insert("0.0", f"Costo Total: ${value:.2f}\nRuta: {path_str}\n")
                if extra_routes:
                    self.path_text.insert("end", "\nOtras rutas posibles (más caras):\n")
                    for idx, (cost, path) in enumerate(extra_routes, start=2):
                        if cost is not None:
                            path_str = " -> ".join(path)
                            self.path_text.insert("end", f"Ruta {idx}: ${cost:.2f} | {path_str}\n")
                        else:
                            self.path_text.insert("end", f"Ruta {idx}: {path}\n")
            elif result_type == "escalas":
                self.path_text.insert("0.0", f"Número de Escalas: {value}\nRuta: {path_str}")
            
            origin = self.origin_combobox.get()
            destination = self.destination_combobox.get()
            self.draw_graph(origin=origin, destination=destination, path=path_list)

        self.path_text.configure(state="disabled")

    def find_cheapest_route(self):
        origin = self.origin_combobox.get()
        destination = self.destination_combobox.get()
        has_visa = self.visa_var.get()

        if not origin or not destination:
            messagebox.showerror("Error de Entrada", "Por favor, selecciona un Origen y un Destino.")
            return
        if origin == destination:
            messagebox.showerror("Error de Entrada", "El Origen y el Destino no pueden ser el mismo.")
            return

        if not has_visa and self.destinations_data.get(destination, {}).get('requiere_visa', False):
            messagebox.showerror("Viaje No Permitido", f"No puedes viajar a {self.destinations_data[destination]['name']} sin visa.")
            self.update_results_display("error", None, "Viaje no permitido sin visa.")
            self.draw_graph(origin=origin, destination=destination, path=None) 
            return

        rutas = self.travel_graph_instance.find_k_shortest_paths_cost(origin, destination, has_visa, k=4)
        if rutas and rutas[0][0] is not None:
            costo, ruta = rutas[0]
            extra_rutas = rutas[1:] if len(rutas) > 1 else None
            self.update_results_display("costo", costo, ruta, extra_routes=extra_rutas)
        else:
            self.update_results_display("costo", None, rutas[0][1])

    def find_fewest_stops_route(self):
        origin = self.origin_combobox.get()
        destination = self.destination_combobox.get()
        has_visa = self.visa_var.get()

        if not origin or not destination:
            messagebox.showerror("Error de Entrada", "Por favor, selecciona un Origen y un Destino.")
            return
        if origin == destination:
            messagebox.showerror("Error de Entrada", "El Origen y el Destino no pueden ser el mismo.")
            return
        
        if not has_visa and self.destinations_data.get(destination, {}).get('requiere_visa', False):
            messagebox.showerror("Viaje No Permitido", f"No puedes viajar a {self.destinations_data[destination]['name']} sin visa.")
            self.update_results_display("error", None, "Viaje no permitido sin visa.")
            self.draw_graph(origin=origin, destination=destination, path=None) 
            return

        stops, path = self.travel_graph_instance.find_shortest_path_stops(origin, destination, has_visa)
        if stops is not None and isinstance(path, list):
            # Calcular el costo total de la ruta encontrada
            current_graph = self.travel_graph_instance.get_filtered_graph(has_visa)
            total_cost = 0
            for i in range(len(path)-1):
                total_cost += current_graph[path[i]][path[i+1]]['cost']
            self.path_text.configure(state="normal")
            self.path_text.delete("0.0", "end")
            path_str = " -> ".join(path)
            self.path_text.insert("0.0", f"Número de Escalas: {stops}\nCosto Total: ${total_cost:.2f}\nRuta: {path_str}")
            self.draw_graph(origin=origin, destination=destination, path=path)
            self.path_text.configure(state="disabled")
        else:
            self.update_results_display("escalas", None, path)


if __name__ == "__main__":
    app = MetroTravelApp()
    app.mainloop()