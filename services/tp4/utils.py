import cv2
import numpy as np
from scipy.interpolate import UnivariateSpline


def normalize_contour(c):
    """Asegura que el contorno tenga la forma (N, 2) para numpy."""
    a = np.asarray(c)
    if a.ndim == 3 and a.shape[1] == 1:
        a = a[:,0,:]
    return a.reshape(-1,2).astype(float)

def detectar_y0(img_gray):
    """Detecta la línea del sustrato usando HoughLinesP o proyección."""
    h, w = img_gray.shape
    edges = cv2.Canny(img_gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=60,
                            minLineLength=w//3, maxLineGap=10)
    if lines is not None and len(lines) > 0:
        lines = lines[:, 0, :]
        y_coords = lines[:, [1, 3]].flatten()
        return int(round(np.median(y_coords)))
    y_proj = np.mean(edges, axis=1)
    return int(np.argmax(y_proj))

def recorte_superior(img, y0):
    """Corta la imagen desde el sustrato hacia arriba."""
    y0 = int(np.clip(y0, 1, img.shape[0]-1))
    return img[:y0, :]

def pre_segmentar(img_gray, gauss_kernel=(5,5)):
    """Aplica Blur + Otsu + Morph Close."""
    blur = cv2.GaussianBlur(img_gray, gauss_kernel, 0)
    _, binv = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    return cv2.morphologyEx(binv, cv2.MORPH_CLOSE, kernel, iterations=1)

def extraer_contorno(binv, area_min=100):
    """Extrae el contorno más grande."""
    contornos, _ = cv2.findContours(binv.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contornos:
        return None
    cont = max(contornos, key=cv2.contourArea)
    if cv2.contourArea(cont) < area_min:
        return None
    return normalize_contour(cont)

def centroide(cont):
    """Calcula el centro de masa del contorno."""
    M = cv2.moments(cont.astype(np.int32))
    if M.get("m00", 0) == 0:
        return (np.nan, np.nan), 0.0
    return (M["m10"]/M["m00"], M["m01"]/M["m00"]), M["m00"]
 

# === NUEVAS FUNCIONES PARA ÁNGULOS (PUNTO 2) ===

def get_window_indices(N, idx, window=10):
    """Obtiene índices vecinos sin salirse del array."""
    start = max(0, idx - window)
    end = min(N-1, idx + window)
    return np.arange(start, end+1, dtype=int)

def calcular_pendiente_spline(contour, idx, window=12, s=0.0):
    """Ajuste Spline Cúbico Paramétrico."""
    inds = get_window_indices(len(contour), idx, window)
    pts = contour[inds]
    if len(pts) < 4: return None
    
    # Parámetro t normalizado
    t = np.linspace(0, 1, len(pts))
    # Posición relativa del punto de interés
    rel_pos = np.where(inds == idx)[0][0]
    t0 = t[rel_pos]

    try:
        # Splines x(t), y(t)
        sx = UnivariateSpline(t, pts[:,0], k=3, s=s)
        sy = UnivariateSpline(t, pts[:,1], k=3, s=s)
        
        dx = sx.derivative()(t0)
        dy = sy.derivative()(t0)
        
        if abs(dx) < 1e-6: return 90.0 # Vertical
        return np.degrees(np.arctan(dy/dx))
    except:
        return None

def calcular_pendiente_poly(contour, idx, window=12, deg=3):
    """Ajuste Polinómico Paramétrico (Mínimos Cuadrados)."""
    inds = get_window_indices(len(contour), idx, window)
    pts = contour[inds]
    if len(pts) < 4: return None
    
    t = np.linspace(0, 1, len(pts))
    rel_pos = np.where(inds == idx)[0][0]
    t0 = t[rel_pos]

    try:
        # Ajuste x(t), y(t)
        px = np.polyfit(t, pts[:,0], min(deg, len(pts)-1))
        py = np.polyfit(t, pts[:,1], min(deg, len(pts)-1))
        
        # Derivadas
        dpx = np.polyder(px)
        dpy = np.polyder(py)
        
        dx = np.polyval(dpx, t0)
        dy = np.polyval(dpy, t0)
        
        if abs(dx) < 1e-6: return 90.0
        return np.degrees(np.arctan(dy/dx))
    except:
        return None

def corregir_angulo_contacto(angulo_tangente, lado="izq"):
    """
    Convierte el ángulo de la tangente (matemático) al ángulo de contacto físico (interno).
    """
    if angulo_tangente is None: return np.nan
    
    # Lógica geométrica basada en la pendiente hacia afuera/adentro
    theta = np.nan
    if lado == "izq":
        # Izquierda: pendiente positiva = agudo, negativa = obtuso
        if angulo_tangente > 0: theta = angulo_tangente
        else: theta = 180.0 + angulo_tangente
    else:
        # Derecha: pendiente negativa = agudo, positiva = obtuso
        if angulo_tangente < 0: theta = abs(angulo_tangente)
        else: theta = 180.0 - angulo_tangente
        
    return theta

def encontrar_puntos_contacto(contour, y_base_tolerancia=5):
    """Encuentra los índices del contorno más cercanos al sustrato (y=0)."""
    # Asumimos que el contorno ya está shifteado (y=0 es sustrato)
    # Buscamos puntos donde y ~ 0
    
    # Filtramos puntos cercanos al suelo
    mask_base = np.abs(contour[:, 1]) < y_base_tolerancia
    idxs_base = np.where(mask_base)[0]
    
    if len(idxs_base) == 0: return None, None
    
    # El de menor X es izquierda, mayor X es derecha
    # Ojo: el contorno en CV2 suele ser circular.
    # Buscamos el min X y max X dentro de los que tocan el suelo
    
    pts_base = contour[idxs_base]
    idx_L = idxs_base[np.argmin(pts_base[:, 0])]
    idx_R = idxs_base[np.argmax(pts_base[:, 0])]
    
    return idx_L, idx_R 

def obtener_curvas_ajuste(contour, idx, window=15, s=0.0, deg=2):
    """
    Devuelve los puntos usados para el ajuste y las curvas evaluadas (Spline y Poly).
    Útil para visualización detallada.
    """
    inds = get_window_indices(len(contour), idx, window)
    pts = contour[inds]
    
    if len(pts) < 4: return None

    # Normalizar t
    t = np.linspace(0, 1, len(pts))
    
    # Rango denso para graficar curvas suaves
    t_plot = np.linspace(0, 1, 100)
    
    res = {"pts": pts}

    try:
        # Spline
        sx = UnivariateSpline(t, pts[:,0], k=3, s=s)
        sy = UnivariateSpline(t, pts[:,1], k=3, s=s)
        res["spline_x"] = sx(t_plot)
        res["spline_y"] = sy(t_plot)
    except:
        res["spline_x"] = res["spline_y"] = None

    try:
        # Poly
        px = np.polyfit(t, pts[:,0], min(deg, len(pts)-1))
        py = np.polyfit(t, pts[:,1], min(deg, len(pts)-1))
        res["poly_x"] = np.polyval(px, t_plot)
        res["poly_y"] = np.polyval(py, t_plot)
    except:
        res["poly_x"] = res["poly_y"] = None
        
    return res

def pts_xy(cont):
    """
    Convierte un contorno de OpenCV a un array (N, 2) de float.
    Alias conveniente para normalize_contour usado en notebooks.
    """
    return normalize_contour(cont)