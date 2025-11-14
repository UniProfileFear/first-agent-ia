# interfaz.py - Interfaz de usuario y ejecución
import tkinter as tk
from tkinter import ttk, messagebox
import time
import traceback
from modelo import Museo, VelocidadControl
from agentes import AgenteSecuencial  # Importa el orquestador

class InterfazMuseo:
    """Vista de la aplicación (Patrón MVC)"""
    def __init__(self, root):
        self.root = root
        self.root.title("Agente IA")
        self.root.geometry("1200x800")
        
        self.museo = Museo()
        self.agente = None
        self.ejecutando = False
        self.velocidad = VelocidadControl()
        
        self._crear_widgets()
        
    def _crear_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Canvas de visualización
        self.canvas = tk.Canvas(main_frame, width=720, height=720, bg="white", borderwidth=2, relief="groove")
        self.canvas.grid(row=0, column=0, rowspan=3, padx=10)
        
        # Panel de control
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Selección de algoritmo (ahora solo informativa)
        ttk.Label(control_frame, text="📚 Algoritmos:", font=("Arial", 12, "bold")).grid(row=0, column=0, pady=5, sticky=tk.W)
        
        info_frame = ttk.LabelFrame(control_frame, text="Secuencia de ejecución", padding=10)
        info_frame.grid(row=1, column=0, pady=10, sticky=(tk.W, tk.E))
        ttk.Label(info_frame, text="1. Hill Climbing", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W)
        ttk.Label(info_frame, text="2. Simulated Annealing", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W)
        ttk.Label(info_frame, text="3. Tabla comparativa", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W)
        
        # Velocidad de animación
        ttk.Label(control_frame, text="⚡ Velocidad:", font=("Arial", 12, "bold")).grid(row=2, column=0, pady=10, sticky=tk.W)
        self.velocidad_slider = ttk.Scale(control_frame, from_=0.1, to=2.0, orient=tk.HORIZONTAL, command=self._cambiar_velocidad)
        self.velocidad_slider.set(0.5)
        self.velocidad_slider.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        # Botones de control
        btn_frame = ttk.Frame(control_frame)
        btn_frame.grid(row=4, column=0, pady=20)
        
        self.btn_iniciar = ttk.Button(btn_frame, text="▶ Iniciar Secuencia", command=self.iniciar)
        self.btn_iniciar.grid(row=0, column=0, padx=5)
        
        self.btn_pausar = ttk.Button(btn_frame, text="⏸ Pausar", command=self.pausar, state=tk.DISABLED)
        self.btn_pausar.grid(row=0, column=1, padx=5)
        
        self.btn_reiniciar = ttk.Button(btn_frame, text="🔄 Reiniciar", command=self.reiniciar)
        self.btn_reiniciar.grid(row=0, column=2, padx=5)
        
        # Estadísticas en tiempo real
        stats_frame = ttk.LabelFrame(control_frame, text="📊 Estadísticas", padding=10)
        stats_frame.grid(row=5, column=0, pady=20, sticky=(tk.W, tk.E))
        
        self.stats_labels = {}
        for i, stat in enumerate(["Iter/Nodo", "Área Actual", "Mejor Área", "Solapamientos", "Algoritmo"]):
            ttk.Label(stats_frame, text=f"{stat}:", font=("Arial", 10, "bold")).grid(row=i, column=0, sticky=tk.W)
            self.stats_labels[stat] = ttk.Label(stats_frame, text="0", font=("Arial", 10))
            self.stats_labels[stat].grid(row=i, column=1, sticky=tk.W)
        
        # Log de eventos
        log_frame = ttk.LabelFrame(control_frame, text="📝 Log de Eventos", padding=10)
        log_frame.grid(row=6, column=0, pady=20, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.log_text = tk.Text(log_frame, width=45, height=15, font=("Courier", 9))
        scroll = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scroll.set)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        control_frame.columnconfigure(0, weight=1)
        control_frame.rowconfigure(6, weight=1)
        
        self._dibujar_museo()
    
    def _dibujar_museo(self):
        """Dibuja el plano del museo"""
        self.canvas.delete("all")
        escala = 6
        
        # Borde principal
        self.canvas.create_rectangle(10, 10, 10 + self.museo.tamano*escala, 
                                     10 + self.museo.tamano*escala, 
                                     outline="black", width=3)
        
        # Cuadrícula y graduaciones
        for i in range(0, self.museo.tamano + 1, 20):
            # Eje X
            self.canvas.create_text(10 + i*escala, 5 + self.museo.tamano*escala, 
                                   text=str(i), font=("Arial", 8))
            # Eje Y
            self.canvas.create_text(5, 10 + (self.museo.tamano - i)*escala, 
                                   text=str(i), font=("Arial", 8))
    
    def actualizar_visualizacion(self):
        """Actualiza posiciones de cámaras en el canvas"""
        self._dibujar_museo()
        escala = 6
        
        for i, (x, y) in enumerate(self.museo.camaras):
            canvas_x = 10 + x * escala
            canvas_y = 10 + (self.museo.tamano - y) * escala
            radio_px = self.museo.radio * escala
            
            # Área de cobertura
            color = f"#{(i*25)%255:02x}{(i*40)%255:02x}ff"
            self.canvas.create_oval(
                canvas_x - radio_px, canvas_y - radio_px,
                canvas_x + radio_px, canvas_y + radio_px,
                fill=color, stipple="gray12", outline=color, width=2
            )
            
            # Cámara (centro)
            self.canvas.create_oval(canvas_x - 4, canvas_y - 4, canvas_x + 4, canvas_y + 4, 
                                   fill="red", width=2)
            self.canvas.create_text(canvas_x, canvas_y, text=str(i+1), 
                                   fill="white", font=("Arial", 8, "bold"))
        
        self.root.update()
    
    def actualizar_stats(self, iteracion, area_actual, mejor_area, algoritmo):
        """Actualiza las estadísticas en pantalla"""
        self.stats_labels["Iter/Nodo"].config(text=str(iteracion))
        self.stats_labels["Área Actual"].config(text=f"{area_actual:.1f} m²")
        self.stats_labels["Mejor Área"].config(text=f"{mejor_area:.1f} m²")
        self.stats_labels["Solapamientos"].config(text=str(self.museo.solapamientos))
        self.stats_labels["Algoritmo"].config(text=algoritmo)
    
    def log(self, mensaje):
        """Añade mensaje al log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert("1.0", f"[{timestamp}] {mensaje}\n")
    
    def iniciar(self):
        """Inicia la ejecución secuencial"""
        if self.ejecutando:
            return
        
        self.ejecutando = True
        self.btn_iniciar.config(state=tk.DISABLED)
        self.btn_pausar.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        
        # Crear orquestador
        self.agente = AgenteSecuencial(self.museo, self)
        
        self.log("🎬 INICIANDO EJECUCIÓN SECUENCIAL...")
        self.log("📌 Algoritmo 1/2: Hill Climbing")
        self.root.update()
        time.sleep(1)
        
        # Ejecutar en segundo plano
        self.root.after(100, self._ejecutar)
    
    def _ejecutar(self):
        """Ejecuta el agente secuencial (CORRECCIÓN DEL BUG)"""
        try:
            # Llamar al método CORRECTO del AgenteSecuencial
            self.agente.ejecutar_todos()
        except Exception as e:
            # Mostrar error detallado para debugging
            messagebox.showerror("Error", f"Error en ejecución:\n{e}\n\n{traceback.format_exc()}")
        finally:
            self.ejecutando = False
            self.btn_iniciar.config(state=tk.NORMAL)
            self.btn_pausar.config(state=tk.DISABLED)
    
    def pausar(self):
        """Pausa la ejecución"""
        self.velocidad.pausar()
        self.btn_iniciar.config(state=tk.NORMAL)
        self.btn_pausar.config(state=tk.DISABLED)
    
    def reiniciar(self):
        """Reinicia todo el sistema"""
        self.ejecutando = False
        self.velocidad.reanudar()
        self.museo.camaras = []
        self.museo.calcular_area_cubierta()
        self.actualizar_visualizacion()
        self.actualizar_stats(0, 0, 0, "Ninguno")
        self.btn_iniciar.config(state=tk.NORMAL)
        self.btn_pausar.config(state=tk.DISABLED)
        self.log("🔄 Sistema reiniciado")
    
    def _cambiar_velocidad(self, value):
        """Cambia velocidad de animación"""
        self.velocidad.set_delay(float(value))


def main():
    """Función principal"""
    root = tk.Tk()
    app = InterfazMuseo(root)
    
    # Mensaje inicial
    app.log("🏛️ MUSEO DE HISTORIA DE CUBA")
    app.log("📐 Dimensiones: 120m × 120m (14,400 m²)")
    app.log("📹 Cámaras: 10 unidades | Radio: 15m")
    app.log("🎯 Objetivo: Maximizar área SIN solapamientos")
    app.log("📖 Algoritmos: Hill Climbing + Simulated Annealing")
    app.log("⚡ Pulse 'Iniciar Secuencia' para comenzar")
    
    root.mainloop()


if __name__ == "__main__":
    main()