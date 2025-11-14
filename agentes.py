# agentes.py
from modelo import Museo
import random
import math
import time

class AgenteHillClimbing:
    """Hill Climbing con Reinicios Aleatorios"""
    def __init__(self, museo, interfaz):
        self.museo = museo
        self.interfaz = interfaz
        self.max_restarts = 20
        self.mejor_global = None
        self.valor_global = -1
        self.tiempo_ejecucion = 0
        
    def buscar(self):
        """RANDOM-RESTART HILL-CLIMBING"""
        self.interfaz.log("="*50)
        self.interfaz.log("🚀 INICIANDO HILL CLIMBING...")
        inicio = time.time()
        
        for restart in range(self.max_restarts):
            self.interfaz.log(f"🔁 Reinicio {restart + 1}/{self.max_restarts}")
            
            estado = self._generar_estado_aleatorio()
            valor = self._evaluar(estado)
            
            while True:
                self.museo.camaras = estado
                self.interfaz.actualizar_visualizacion()
                self.interfaz.actualizar_stats(
                    iteracion=restart + 1,
                    area_actual=valor,
                    mejor_area=self.valor_global,
                    algoritmo="Hill Climbing"
                )
                
                sucesores = self.museo.generar_vecinos(estado)
                if not sucesores:
                    break
                
                mejor_sucesor = max(sucesores, key=self._evaluar)
                mejor_valor = self._evaluar(mejor_sucesor)
                
                if mejor_valor <= valor:  # Máximo local alcanzado
                    break
                
                estado = mejor_sucesor
                valor = mejor_valor
                self.interfaz.velocidad.sleep()
            
            if valor > self.valor_global:
                self.valor_global = valor
                self.mejor_global = estado
        
        self.tiempo_ejecucion = time.time() - inicio
        self.museo.camaras = self.mejor_global
        self.interfaz.log(f"🏁 FIN HILL CLIMBING - Área: {self.valor_global:.1f} m²")
        
        return {
            'algoritmo': 'Hill Climbing',
            'area': self.valor_global,
            'tiempo': self.tiempo_ejecucion,
            'iteraciones': self.max_restarts,
            'solucion': self.mejor_global
        }
    
    def _generar_estado_aleatorio(self):
        """Genera estado inicial válido"""
        camaras = []
        intentos = 0
        while len(camaras) < self.museo.num_camaras and intentos < 500:
            x = random.randint(self.museo.radio, self.museo.tamano - self.museo.radio)
            y = random.randint(self.museo.radio, self.museo.tamano - self.museo.radio)
            posicion = (x, y)
            if all(not self.museo.hay_solapamiento(posicion, c) for c in camaras):
                camaras.append(posicion)
            intentos += 1
        return camaras
    
    def _evaluar(self, estado):
        """Función objetivo"""
        temp = self.museo.camaras
        self.museo.camaras = estado
        area = self.museo.calcular_area_cubierta()
        self.museo.camaras = temp
        return area


class AgenteSimulatedAnnealing:
    """Simulated Annealing"""
    def __init__(self, museo, interfaz):
        self.museo = museo
        self.interfaz = interfaz
        self.temp_inicial = 1000
        self.enfriamiento = 0.95
        self.mejor_global = None
        self.valor_global = -1
        self.tiempo_ejecucion = 0
        
    def buscar(self):
        """SIMULATED ANNEALING"""
        self.interfaz.log("="*50)
        self.interfaz.log("🚀 INICIANDO SIMULATED ANNEALING...")
        inicio = time.time()
        
        estado_actual = self._generar_estado_aleatorio()
        valor_actual = self._evaluar(estado_actual)
        self.mejor_global = estado_actual
        self.valor_global = valor_actual
        
        temperatura = self.temp_inicial
        iteracion = 0
        
        while temperatura > 0.1:
            iteracion += 1
            
            self.museo.camaras = estado_actual
            self.interfaz.actualizar_visualizacion()
            self.interfaz.actualizar_stats(
                iteracion=iteracion,
                area_actual=valor_actual,
                mejor_area=self.valor_global,
                algoritmo="Simulated Annealing"
            )
            
            vecino = self._vecino_aleatorio(estado_actual)
            if vecino is None:
                temperatura *= self.enfriamiento
                continue
            
            valor_vecino = self._evaluar(vecino)
            delta = valor_vecino - valor_actual
            
            if delta > 0 or random.random() < math.exp(delta / temperatura):
                estado_actual = vecino
                valor_actual = valor_vecino
                
                if valor_actual > self.valor_global:
                    self.valor_global = valor_actual
                    self.mejor_global = estado_actual
            
            if iteracion % 50 == 0:
                self.interfaz.log(f"❄️ T={temperatura:.2f}, Área={valor_actual:.1f} m²")
            
            temperatura *= self.enfriamiento
            self.interfaz.velocidad.sleep()
        
        self.tiempo_ejecucion = time.time() - inicio
        self.museo.camaras = self.mejor_global
        self.interfaz.log(f"🏁 FIN SIMULATED ANNEALING - Área: {self.valor_global:.1f} m²")
        
        return {
            'algoritmo': 'Simulated Annealing',
            'area': self.valor_global,
            'tiempo': self.tiempo_ejecucion,
            'iteraciones': iteracion,
            'solucion': self.mejor_global
        }
    
    def _vecino_aleatorio(self, estado):
        """Genera vecino perturbando una cámara"""
        nuevo_estado = estado.copy()
        idx = random.randint(0, len(estado) - 1)
        x, y = nuevo_estado[idx]
        
        dx = random.randint(-10, 10)
        dy = random.randint(-10, 10)
        nueva_pos = (max(self.museo.radio, min(self.museo.tamano - self.museo.radio, x + dx)),
                     max(self.museo.radio, min(self.museo.tamano - self.museo.radio, y + dy)))
        
        nuevo_estado[idx] = nueva_pos
        
        for i, pos in enumerate(nuevo_estado):
            if i != idx and self.museo.hay_solapamiento(pos, nueva_pos):
                return None
        return nuevo_estado
    
    def _generar_estado_aleatorio(self):
        """Genera estado inicial válido"""
        camaras = []
        intentos = 0
        while len(camaras) < self.museo.num_camaras and intentos < 500:
            x = random.randint(self.museo.radio, self.museo.tamano - self.museo.radio)
            y = random.randint(self.museo.radio, self.museo.tamano - self.museo.radio)
            posicion = (x, y)
            if all(not self.museo.hay_solapamiento(posicion, c) for c in camaras):
                camaras.append(posicion)
            intentos += 1
        return camaras
    
    def _evaluar(self, estado):
        """Función objetivo"""
        temp = self.museo.camaras
        self.museo.camaras = estado
        area = self.museo.calcular_area_cubierta()
        self.museo.camaras = temp
        return area


class AgenteSecuencial:
    """Orquesta ambos algoritmos y muestra tabla comparativa"""
    def __init__(self, museo, interfaz):
        self.museo = museo
        self.interfaz = interfaz
        self.resultados = []
        
    def ejecutar_todos(self):
        """Ejecuta Hill Climbing y Simulated Annealing secuencialmente"""
        # Ejecutar Hill Climbing
        self.interfaz.log("\n📌 ALGORITMO 1 DE 2: HILL CLIMBING")
        self.interfaz.log("="*50)
        agente_hc = AgenteHillClimbing(self.museo, self.interfaz)
        resultado_hc = agente_hc.buscar()
        self.resultados.append(resultado_hc)
        
        # Pausa entre algoritmos
        self.interfaz.log("\n⏳ PAUSA DE 2 SEGUNDOS...")
        self.interfaz.log("="*50)
        time.sleep(2)
        
        # Ejecutar Simulated Annealing
        self.interfaz.log("\n📌 ALGORITMO 2 DE 2: SIMULATED ANNEALING")
        self.interfaz.log("="*50)
        agente_sa = AgenteSimulatedAnnealing(self.museo, self.interfaz)
        resultado_sa = agente_sa.buscar()
        self.resultados.append(resultado_sa)
        
        # Mostrar tabla comparativa
        self._mostrar_tabla_comparativa()
        
    def _mostrar_tabla_comparativa(self):
        """Muestra tabla comparativa final en el log"""
        self.interfaz.log("\n" + "═"*60)
        self.interfaz.log("📊 TABLA COMPARATIVA FINAL ")
        self.interfaz.log("═"*60)
        
        # Cabeceras
        self.interfaz.log(f"{'Algoritmo':<20} {'Área (m²)':<12} {'Tiempo (s)':<12} {'Iteraciones':<12}")
        self.interfaz.log("─"*60)
        
        # Datos
        for res in self.resultados:
            self.interfaz.log(f"{res['algoritmo']:<20} {res['area']:<12.1f} {res['tiempo']:<12.2f} {res['iteraciones']:<12}")
        
        self.interfaz.log("═"*60)
        
        # Ganador
        ganador = max(self.resultados, key=lambda x: x['area'])
        mejora = ((ganador['area'] - min(r['area'] for r in self.resultados)) / 
                  min(r['area'] for r in self.resultados) * 100)
        
        self.interfaz.log(f"🏆 GANADOR: {ganador['algoritmo']}")
        self.interfaz.log(f"📈 Área máxima: {ganador['area']:.1f} m²")
        self.interfaz.log(f"📊 Mejora relativa: {mejora:.1f}%")
        self.interfaz.log("═"*60)