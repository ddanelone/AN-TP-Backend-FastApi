# services/tp4/core.py 
# Singleton para procesamiento de datos TP4

import os
import glob
import cv2
import numpy as np
import pandas as pd
from .utils import (detectar_y0, recorte_superior, pre_segmentar, extraer_contorno, 
                   centroide, encontrar_puntos_contacto, calcular_pendiente_spline, 
                   calcular_pendiente_poly, corregir_angulo_contacto)

# Constantes Físicas
RUTA_IMAGENES = os.path.join("data", "tp4")
PATRON = "TP4_Gota_*.jpg"
ESCALA_UM_POR_PX = 4.13
ESCALA_M_POR_PX = ESCALA_UM_POR_PX * 1e-6
FPS = 20538
DT = 1.0 / FPS
RHO = 7380.0
MARGEN_BASE_PX = 12

class TP4DataProcessor:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TP4DataProcessor, cls).__new__(cls)
            cls._instance.data = None
            cls._instance.logs = []
            cls._instance.visualization_data = {}
        return cls._instance

    def get_data(self):
        if self.data is None:
            self.process_images()
        return self.data

    def get_logs(self):
        return "\n".join(self.logs)

    def get_visualization_frame(self):
        if self.data is None:
            self.process_images()
        return self.visualization_data

    def process_images(self):
        self.logs.clear()
        self.logs.append(">>> Iniciando procesamiento de imágenes TP4 (Con ajuste de sustrato)...")
        
        paths = sorted(glob.glob(os.path.join(RUTA_IMAGENES, PATRON)))
        if not paths:
            self.logs.append("ERROR: No se encontraron imágenes.")
            return

        results = {
            "t_ms": [], "cx_m": [], "cy_m": [], 
            "diam_base": [], "altura": [], "vol": [], "masa": [],
            "frame_idx": [],
            # NUEVAS COLUMNAS PARA INCISO 2
            "angL_spline": [], "angR_spline": [],
            "angL_poly": [], "angR_poly": [],
            # NUEVAS COLUMNAS PARA INCISO 3 (ESTO FALTABA)
            "per_izq": [], "per_der": [], "Sf": []
        }

        # --- EL TRUQUITO (Valores fijos del Notebook) ---
        # Estos valores son la "verdad absoluta" para los primeros frames.
        SUST_FIX = {
            20: 127, 21: 129, 22: 130, 23: 130, 
            24: 130, 25: 129, 26: 128, 27: 126
        }
        
        # Establecemos la referencia inicial con el valor fijo del frame 20 (aprox 127)
        # Esto evita que el detector automatico se vaya hacia el reflejo.
        y0_ref = 127 
        self.logs.append(f"Info: Referencia de sustrato fijada en Y={y0_ref} (Hardcoded seguro)")

        count = 0
        for i, path in enumerate(paths):
            k = i + 1
            
            # Procesamos del 10 en adelante
            if k < 10: continue

            img_bgr = cv2.imread(path)
            if img_bgr is None: continue
            img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

            # 1. Determinación ROBUSTA del sustrato (y_sustrato)
            if k in SUST_FIX:
                y_sustrato = int(SUST_FIX[k])
            else:
                y_det = detectar_y0(img_gray)
                # Si la detección difiere más de 20px de la referencia, es un reflejo.
                # Usamos la referencia.
                if abs(y_det - y0_ref) > 20:
                    y_sustrato = y0_ref
                else:
                    y_sustrato = y_det

            # 2. Recorte SUPERIOR (Elimina el reflejo)
            # Cortamos desde 0 hasta y_sustrato. Todo lo de abajo se ignora.
            top_area = recorte_superior(img_gray, y_sustrato)
            
            # 3. Segmentación y Contornos
            binv = pre_segmentar(top_area)
            cont = extraer_contorno(binv)

            if cont is None: continue

            # Guardar visualización (Frame 28 es bueno para ver si funcionó el fix)
            if k == 28:
                self.visualization_data = {
                    "original": img_gray,
                    "binaria": binv, # Esto ahora solo tendrá la parte de arriba
                    "contorno": cont,
                    "y_sustrato": y_sustrato,
                    "cx": 0, "cy": 0
                }
            # --- INCISO 2: CÁLCULO DE ÁNGULOS ---
            # 1. Shiftear contorno para que Y=0 sea el sustrato
            # (En CV2 Y crece hacia abajo, pero aquí Y=0 es arriba del recorte...
            # Para simplificar la matemática de pendientes, invertimos Y para que apunte "arriba")
            
            # Coordenadas físicas locales (x, y positivos)
            # x: tal cual. y: distancia desde el sustrato hacia arriba.
            # En la imagen recortada, el sustrato está en la fila 'y_sustrato' (aprox final).
            # NO, espera. Recorte superior devuelve img[:y_sustrato]. El sustrato es la última fila.
            
            H_recorte, W_recorte = top_area.shape
            # Sustrato está en H_recorte - 1 (aprox)
            
            cont_fisico = cont.copy()
            # Invertir Y: 0 en sustrato, crece hacia arriba
            cont_fisico[:, 1] = (H_recorte - 1) - cont_fisico[:, 1] 
            
            # Buscar índices de contacto (donde y ~ 0)
            idx_L, idx_R = encontrar_puntos_contacto(cont_fisico, y_base_tolerancia=10)
            
            # Calcular Ángulos
            al_s, ar_s, al_p, ar_p = np.nan, np.nan, np.nan, np.nan
            
            if idx_L is not None:
                # Spline
                pend_s = calcular_pendiente_spline(cont_fisico, idx_L, window=15)
                al_s = corregir_angulo_contacto(pend_s, "izq")
                # Poly
                pend_p = calcular_pendiente_poly(cont_fisico, idx_L, window=15, deg=2)
                al_p = corregir_angulo_contacto(pend_p, "izq")
                
            if idx_R is not None:
                # Spline
                pend_s = calcular_pendiente_spline(cont_fisico, idx_R, window=15)
                ar_s = corregir_angulo_contacto(pend_s, "der")
                # Poly
                pend_p = calcular_pendiente_poly(cont_fisico, idx_R, window=15, deg=2)
                ar_p = corregir_angulo_contacto(pend_p, "der")

            results["angL_spline"].append(al_s)
            results["angR_spline"].append(ar_s)
            results["angL_poly"].append(al_p)
            results["angR_poly"].append(ar_p)

            # 4. Centroide y Física
            (cx_px, cy_px), area_px = centroide(cont)
            
            # FÍSICA:
            # y_sustrato es el 0 físico.
            # cy_px es la coord en la imagen recortada (desde arriba).
            # Altura real = y_sustrato - cy_px
            
            t = k * DT * 1e3 # ms
            cx_real = cx_px * ESCALA_M_POR_PX
            cy_real = (y_sustrato - cy_px) * ESCALA_M_POR_PX
            
            # Geometría
            xs = cont[:, 0]
            ys = cont[:, 1]
            d_px = np.max(xs) - np.min(xs)
            h_px = np.max(ys) - np.min(ys)
            
            # Cálculos adicionales para Inciso 3
            # Perímetros (Izquierdo y Derecho)
            # Dividimos el contorno por el centroide X
            mask_izq = cont[:, 0] < cx_px
            mask_der = cont[:, 0] >= cx_px
            
            # Función simple para longitud de arco
            def arco(pts):
                if len(pts) < 2: return 0.0
                # Ordenar por Y o X para medir distancia consecutiva (aprox)
                # En un contorno general es complejo, pero para mitades verticales:
                # La suma de distancias euclidianas entre puntos consecutivos del contorno original
                # es la mejor aprox. Pero aquí tenemos puntos filtrados.
                # Usamos la longitud del contorno completo y dividimos por 2 aprox, 
                # o mejor: cv2.arcLength sobre el contorno original dividido.
                return 0.0 # Placeholder si no se quiere complejidad extrema
            
            # Para simplificar y no re-implementar lógica geométrica compleja:
            # Usaremos el perímetro total dividido por 2 como referencia, 
            # o si querés implementar la lógica de "perimetros_por_lado" del notebook original:
            
            def perimetros_por_lado(cnt, cx):
                izq = cnt[cnt[:, 0] < cx]
                der = cnt[cnt[:, 0] >= cx]
                
                def calc_len(pts):
                    if len(pts) < 2: return 0.0
                    # Ordenamos por ángulo o simplemente sumamos distancias
                    # (Aprox simple: suma de distancias entre puntos crudos)
                    return np.sum(np.sqrt(np.sum(np.diff(pts, axis=0)**2, axis=1))) * ESCALA_M_POR_PX
                
                return calc_len(izq), calc_len(der)

            p_izq, p_der = perimetros_por_lado(cont, cx_px)
            
            # Factor de esparcimiento (D/H)
            # Evitar división por cero
            sf = (d_px / h_px) if h_px > 0 else 0.0

            results["per_izq"].append(p_izq)
            results["per_der"].append(p_der)
            results["Sf"].append(sf)

            # Volumen (Revolución)
            vol = 0.0
            dy = ESCALA_M_POR_PX
            H_bin, W_bin = binv.shape
            for y_row in range(H_bin):
                x_row = np.where(binv[y_row, :] > 0)[0]
                if x_row.size > 1:
                    diam = (x_row[-1] - x_row[0] + 1) * ESCALA_M_POR_PX
                    vol += np.pi * (diam/2)**2 * dy
            
            masa = vol * RHO

            results["t_ms"].append(t)
            results["cx_m"].append(cx_real)
            results["cy_m"].append(cy_real)
            results["diam_base"].append(d_px * ESCALA_M_POR_PX)
            results["altura"].append(h_px * ESCALA_M_POR_PX)
            results["vol"].append(vol)
            results["masa"].append(masa)
            results["frame_idx"].append(k)
            
            if k == 28:
                self.visualization_data["cx"] = cx_px
                self.visualization_data["cy"] = cy_px
            
            count += 1

        self.logs.append(f"OK: Procesados {count} frames con filtrado de reflejo.")
        self.data = pd.DataFrame(results)

    def get_ajuste_detalle(self, frame_obj=28):
        """
        Recupera y procesa 'on-demand' un frame específico para mostrar el detalle del ajuste.
        Re-lee la imagen para asegurar frescura y no guardar contornos pesados en memoria.
        """
        path = sorted(glob.glob(os.path.join(RUTA_IMAGENES, PATRON)))[frame_obj - 1]
        
        # Procesamiento estándar (copiado de process_images pero solo para este frame)
        img_bgr = cv2.imread(path)
        img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        
        # Valores fijos sustrato (para consistencia)
        SUST_FIX = {20: 127, 21: 129, 22: 130, 23: 130, 24: 130, 25: 129, 26: 128, 27: 126}
        
        y_sustrato = SUST_FIX.get(frame_obj, detectar_y0(img_gray))
        # Ajuste "truquito" si aplica
        if frame_obj >= 20 and frame_obj <= 27: # Rango critico aprox
             pass # Ya lo toma del dict
        elif abs(y_sustrato - 127) > 20: 
             y_sustrato = 127

        top_area = recorte_superior(img_gray, y_sustrato)
        binv = pre_segmentar(top_area)
        cont = extraer_contorno(binv)
        
        if cont is None: return None

        # Shift físico
        H_rec, _ = top_area.shape
        cont_fisico = cont.copy()
        cont_fisico[:, 1] = (H_rec - 1) - cont_fisico[:, 1]
        
        # Buscar contacto
        from .utils import encontrar_puntos_contacto, obtener_curvas_ajuste
        idx_L, idx_R = encontrar_puntos_contacto(cont_fisico, y_base_tolerancia=10)
        
        data_L = obtener_curvas_ajuste(cont_fisico, idx_L, window=15) if idx_L else None
        data_R = obtener_curvas_ajuste(cont_fisico, idx_R, window=15) if idx_R else None
        
        return {"L": data_L, "R": data_R, "frame": frame_obj}    
       
processor = TP4DataProcessor()