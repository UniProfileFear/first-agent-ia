# modelo.py - Clases de datos del museo
import random

class Museo:
    """Representa el entorno del museo"""
    def __init__(self, tamano=120, num_camaras=10, radio_cobertura=15):
        self.tamano = tamano
        self.num_camaras = num_camaras
        self.radio = radio_cobertura
        self.camaras = []
        self.solapamientos = 0
        
    def calcular_area_cubierta(self):
        """Heurística: área cubierta sin solapamientos"""
        puntos_cubiertos = set()
        self.solapamientos = 0
        
        for camara in self.camaras:
            x, y = camara
            for i in range(max(0, int(x - self.radio)), min(self.tamano, int(x + self.radio)) + 1):
                for j in range(max(0, int(y - self.radio)), min(self.tamano, int(y + self.radio)) + 1):
                    if math.sqrt((i - x)**2 + (j - y)**2) <= self.radio:
                        punto = (i, j)
                        if punto in puntos_cubiertos:
                            self.solapamientos += 1
                        puntos_cubiertos.add(punto)
        
        return len(puntos_cubiertos)

    def es_valido(self, posicion):
        """Verifica si una posición está dentro del museo"""
        x, y = posicion
        return 0 <= x <= self.tamano and 0 <= y <= self.tamano

    def hay_solapamiento(self, pos1, pos2):
        """Restricción binaria: No solapamiento"""
        dist = math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
        return dist < self.radio * 2

    def generar_vecinos(self, estado):
        """Sucesores para búsqueda local"""
        vecinos = []
        for i in range(len(estado)):
            for dx, dy in [(5,0), (-5,0), (0,5), (0,-5)]:
                nueva_pos = (estado[i][0] + dx, estado[i][1] + dy)
                if self.es_valido(nueva_pos):
                    nuevo_estado = estado.copy()
                    nuevo_estado[i] = nueva_pos
                    
                    # Verificar restricciones
                    solapa = False
                    for j, pos in enumerate(nuevo_estado):
                        if i != j and self.hay_solapamiento(pos, nuevo_estado[i]):
                            solapa = True
                            break
                    
                    if not solapa:
                        vecinos.append(nuevo_estado)
        return vecinos


class VelocidadControl:
    """Control de velocidad de animación (patrón de diseño)"""
    def __init__(self):
        self.delay = 0.5
        self.pausado = False
    
    def sleep(self):
        import time
        if not self.pausado:
            time.sleep(self.delay)
    
    def pausar(self):
        self.pausado = True
    
    def reanudar(self):
        self.pausado = False
    
    def set_delay(self, value):
        self.delay = value