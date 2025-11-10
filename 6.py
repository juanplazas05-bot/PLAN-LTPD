# -----------------------------------------------------------
# APP: Plan de Muestreo LTPD (c = 0) - cálculo hipergeométrico
# Autor: Juan Camilo Plazas & ChatGPT
# Basado en: Gutiérrez Pulido, "Control Estadístico de la Calidad y Seis Sigma" (pp. 331–333)
# -----------------------------------------------------------

import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt

# -----------------------------------------------------------
# CONFIGURACIÓN VISUAL DE LA APLICACIÓN
# -----------------------------------------------------------
st.set_page_config(page_title="Plan LTPD (c = 0) - cálculo hipergeométrico", layout="centered")

# Pequeño bloque de estilo visual
st.markdown("""
<style>
body { background-color: #f8fafc; color: #111827; font-family: 'Segoe UI', sans-serif; }
.result-card {
  background-color: white;
  padding: 1rem 1.4rem;
  border-radius: 10px;
  box-shadow: 0px 3px 8px rgba(0,0,0,0.1);
  margin-top: 1rem;
}
.stButton>button {
  width: 100%;
  background-color: #2563eb;
  color: white;
  border-radius: 8px;
  padding: 0.6rem;
  font-size: 1rem;
}
.stButton>button:hover {
  background-color: #1e40af;
  color: white;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# FUNCIONES AUXILIARES
# -----------------------------------------------------------

def prob_zero_defects(N, D, n):
    """
    Calcula la probabilidad de aceptar un lote con c = 0 (sin defectos encontrados)
    usando el modelo HIPERGEOMÉTRICO (sin reemplazo):
        P0 = C(N-D, n) / C(N, n)
    Se calcula como un producto acumulado para evitar overflow.
    """
    if n == 0: return 1.0
    if D <= 0: return 1.0
    if n > N: return 0.0
    p0 = 1.0
    for i in range(n):
        p0 *= (N - D - i) / (N - i)
    return max(min(p0, 1.0), 0.0)


def encontrar_n_hipergeometrica(N, pL, beta):
    """
    Encuentra el tamaño mínimo de muestra n tal que:
        P0 = P(0 defectos en n muestras | N, D, n) ≤ β
    donde D = ceil(N·pL).
    """
    D = math.ceil(N * pL)
    for n in range(1, N + 1):
        P0 = prob_zero_defects(N, D, n)
        if P0 <= beta:
            return n, D, P0
    return N, D, prob_zero_defects(N, D, N)


def aoql_aproximado(N, n):
    """Calcula AOQL ≈ 0.3679 / (N·f) según el libro (para c = 0)."""
    f = n / N if N > 0 else 0
    return 0.3679 / (N * f) if f > 0 else float('nan')


def curva_OC_hipergeometrica(N, n, p_max=0.08, puntos=200):
    """
    Calcula la Curva OC exacta para un rango de proporciones de defectuosos (p).
    Devuelve: porcentajes de p y probabilidad de aceptación (%) para graficar.
    """
    p_vals = np.linspace(0, p_max, puntos)
    Pa = []
    for p in p_vals:
        D = math.ceil(N * p)
        Pa.append(prob_zero_defects(N, D, n) * 100)
    return p_vals * 100, np.array(Pa)

# -----------------------------------------------------------
# ENTRADAS DEL USUARIO
# -----------------------------------------------------------
st.title("📘 Plan de Muestreo LTPD (c = 0)")
st.caption("Cálculo exacto mediante modelo hipergeométrico — basado en Gutiérrez Pulido, pp. 331–333")

st.sidebar.header("🔹 Parámetros de entrada")
N = st.sidebar.number_input("Tamaño del lote (N)", min_value=1, value=600, step=100)
pL_percent = st.sidebar.number_input("LTPD (% de defectuosos límite)", min_value=0.01, value=2.5, step=0.1, format="%.3f")
beta = st.sidebar.number_input("β (Riesgo del consumidor)", min_value=0.001, max_value=0.5, value=0.10, step=0.01, format="%.3f")

pL = pL_percent / 100.0

# -----------------------------------------------------------
# CÁLCULO PRINCIPAL
# -----------------------------------------------------------
if st.sidebar.button("Calcular Plan LTPD (c = 0)"):
    
    # 1️⃣ Cálculo del tamaño de muestra (n)
    n, D, P0 = encontrar_n_hipergeometrica(N, pL, beta)

    # 2️⃣ Cálculo de otros indicadores
    K = N * pL
    f = n / N
    AOQL = aoql_aproximado(N, n)

    # -------------------------------------------------------
    # RESULTADOS
    # -------------------------------------------------------
    st.markdown("## 📊 Resultados del plan")
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.write(f"**Tamaño del lote (N):** {N:,}")
    st.write(f"**LTPD (pL):** {pL_percent:.3f}%")
    st.write(f"**β (riesgo del consumidor):** {beta:.3f}")
    st.markdown("---")
    st.write(f"**Defectuosos en el lote límite (D = ceil(N·pL)):** {D}")
    st.write(f"**K (esperado = N·pL):** {K:.2f}")
    st.write(f"**Tamaño de muestra (n):** {n}")
    st.write(f"**Número de aceptación (c):** 0")
    st.write(f"**Fracción inspeccionada (f = n/N):** {f*100:.2f}%")
    st.write(f"**Probabilidad de aceptación en LTPD (Pₐ):** {P0*100:.2f}%")
    st.write(f"**AOQL aproximado:** {AOQL*100:.3f}%")
    st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------------------------------
    # CURVA OC
    # -------------------------------------------------------
    st.markdown("### 📈 Curva OC (Probabilidad de aceptación)")
    p_vals, Pa_vals = curva_OC_hipergeometrica(N, n, p_max=max(0.05, pL*3))
    fig, ax = plt.subplots(figsize=(7,4))
    ax.plot(p_vals, Pa_vals, color="#2563eb", lw=2, label="Curva OC (hipergeométrica)")
    ax.axvline(pL_percent, color="green", linestyle="--", label=f"LTPD = {pL_percent:.2f}%")
    ax.axhline(beta*100, color="red", linestyle="--", label=f"β = {beta*100:.1f}%")
    ax.set_xlabel("% de unidades defectuosas en el lote")
    ax.set_ylabel("Probabilidad de aceptación (%)")
    ax.set_title(f"Curva OC — Plan (n={n}, c=0)")
    ax.legend()
    ax.grid(alpha=0.4, linestyle="--")
    st.pyplot(fig)

    # -------------------------------------------------------
    # INTERPRETACIÓN AUTOMÁTICA
    # -------------------------------------------------------
    st.markdown("### 🧠 Interpretación del resultado")

    texto = f"""
    El plan de muestreo calculado tiene un tamaño de muestra de **n = {n}** unidades, 
    tomadas de un lote de **N = {N}** piezas (una fracción de {f*100:.2f}%).  
    Si en esa muestra **no se detecta ningún defecto (c = 0)**, el lote se acepta.

    Con este diseño, un lote que contenga una proporción de defectuosos igual al límite de calidad tolerable 
    **LTPD = {pL_percent:.2f}%** tendrá una **probabilidad de aceptación de aproximadamente {P0*100:.2f}%**, 
    lo cual corresponde al riesgo del consumidor **β = {beta:.2f}**.

    Esto significa que, en promedio, **solo {beta*100:.0f}% de los lotes “malos” (con calidad igual al LTPD)** 
    serán aceptados, protegiendo adecuadamente al cliente.  
    La calidad promedio de salida esperada (AOQL) se estima en **{AOQL*100:.3f}%** de defectuosos.
    """
    st.info(texto)

else:
    st.markdown("""
    ### 🧭 Instrucciones
    1. Ingrese los parámetros en la barra lateral:
       - Tamaño del lote (N)
       - LTPD (% de defectuosos límite)
       - β (riesgo del consumidor)
    2. Presione **Calcular Plan LTPD (c = 0)**.
    
    El programa calculará automáticamente el tamaño mínimo de muestra **n**
    que cumple que la probabilidad de aceptar un lote con la calidad límite (LTPD)
    sea igual o menor al riesgo del consumidor **β**.
    """)

