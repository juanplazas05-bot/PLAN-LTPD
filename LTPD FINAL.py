# -----------------------------------------------------------
# APP: Plan de Muestreo LTPD (c variable) - cálculo hipergeométrico
# Autor: Juan Camilo Plazas
# Descripción:
# Calcula planes de muestreo LTPD (Límite de Calidad Tolerable del Proceso)
# -----------------------------------------------------------

import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
from math import comb

# -----------------------------------------------------------
# CONFIGURACIÓN VISUAL DE LA APLICACIÓN
# -----------------------------------------------------------
st.set_page_config(page_title="Plan de Muestreo LTPD", layout="centered")

# Estilo visual general (CSS embebido)
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

def prob_aceptacion(N, D, n, c):
    """
    Calcula la probabilidad de aceptación Pₐ para un plan (N, n, c)
    usando la distribución HIPERGEOMÉTRICA:
        Pₐ = Σ [C(D, x) * C(N-D, n-x)] / C(N, n)
    equivalente a DISTR.HIPERGEOM.N(...;1) en Excel.
    """
    Pa = 0.0
    for x in range(0, c + 1):
        if 0 <= x <= D and 0 <= n - x <= (N - D):  # Evita valores inválidos
            Pa += comb(D, x) * comb(N - D, n - x) / comb(N, n)
    return Pa


def encontrar_n_hipergeometrica(N, pL, beta, c):
    """
    Encuentra el tamaño mínimo de muestra (n) que cumple:
        Pₐ(LTPD) ≤ β
    para un valor de c (número de aceptación) dado.
    """
    D = math.ceil(N * pL)  # Número esperado de defectuosos en el lote límite
    for n in range(1, N + 1):
        Pa = prob_aceptacion(N, D, n, c)
        if Pa <= beta:
            return n, D, Pa
    return N, D, prob_aceptacion(N, D, N, c)


def curva_CO(N, n, c, p_max=0.08, puntos=200):
    """
    Calcula la Curva CO (Característica de Operación)
    mostrando la probabilidad de aceptación frente al % de defectuosos.
    """
    p_vals = np.linspace(0, p_max, puntos)
    Pa_vals = []
    for p in p_vals:
        D = math.ceil(N * p)
        Pa_vals.append(prob_aceptacion(N, D, n, c) * 100)
    return p_vals * 100, np.array(Pa_vals)


def aoql_aprox(N, n):
    """
    Calcula el AOQL aproximado según la fórmula empírica:
        AOQL ≈ 0.3679 / (N · f)
    donde f = n / N es la fracción inspeccionada.
    (Fórmula válida principalmente para planes con c = 0)
    """
    f = n / N
    return 0.3679 / (N * f) if f > 0 else float('nan')

# -----------------------------------------------------------
# ENTRADAS DEL USUARIO
# -----------------------------------------------------------
st.title("📘 Plan de Muestreo LTPD (Límite de Calidad Tolerable del Proceso)")

st.sidebar.header("🔹 Parámetros de entrada")
N = st.sidebar.number_input("Tamaño del lote (N)", min_value=1, value=600, step=100)
pL_percent = st.sidebar.number_input("LTPD (% defectuosos límite)", min_value=0.01, value=2.5, step=0.1, format="%.3f")
beta = st.sidebar.number_input("β (Riesgo del consumidor)", min_value=0.001, max_value=0.5, value=0.10, step=0.01, format="%.3f")
c = st.sidebar.number_input("Número de aceptación (c)", min_value=0, value=0, step=1)

pL = pL_percent / 100.0

# -----------------------------------------------------------
# CÁLCULO PRINCIPAL
# -----------------------------------------------------------
if st.sidebar.button("Calcular Plan LTPD"):
    # 1️⃣ Cálculo principal
    n, D, Pa = encontrar_n_hipergeometrica(N, pL, beta, c)

    # 2️⃣ Cálculos derivados
    K = N * pL
    f = n / N
    AOQL = aoql_aprox(N, n)

    # -------------------------------------------------------
    # RESULTADOS
    # -------------------------------------------------------
    st.markdown("## 📊 Resultados del plan")
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.write(f"**Tamaño del lote (N):** {N:,}")
    st.write(f"**LTPD (pL):** {pL_percent:.3f}%")
    st.write(f"**β (Riesgo del consumidor):** {beta:.3f}")
    st.markdown("---")
    st.write(f"**Defectuosos en el lote límite (K = N·pL):** {D}")
    st.write(f"**Tamaño de muestra (n):** {n}")
    st.write(f"**Número de aceptación (c):** {c}")
    st.write(f"**Fracción inspeccionada (f = n/N):** {f*100:.2f}%")
    st.write(f"**Probabilidad de aceptación (Pₐ):** {Pa*100:.2f}%")
    st.write(f"**AOQL aproximado:** {AOQL*100:.3f}%")
    st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------------------------------
    # CURVA CO
    # -------------------------------------------------------
    st.markdown("### 📈 Curva CO (Característica de Operación)")
    p_vals, Pa_vals = curva_CO(N, n, c, p_max=max(0.05, pL*3))
    fig, ax = plt.subplots(figsize=(7,4))
    ax.plot(p_vals, Pa_vals, color="#2563eb", lw=2, label=f"Curva CO (c={c})")
    ax.axvline(pL_percent, color="green", linestyle="--", label=f"LTPD = {pL_percent:.2f}%")
    ax.axhline(beta*100, color="red", linestyle="--", label=f"β = {beta*100:.1f}%")
    ax.set_xlabel("% de unidades defectuosas en el lote")
    ax.set_ylabel("Probabilidad de aceptación (%)")
    ax.set_title(f"Curva CO — Plan (n={n}, c={c})")
    ax.legend()
    ax.grid(alpha=0.4, linestyle="--")
    st.pyplot(fig)

    # -------------------------------------------------------
    # INTERPRETACIÓN AUTOMÁTICA
    # -------------------------------------------------------
    st.markdown("### 🧠 Interpretación del resultado")

    texto = f"""
El plan de muestreo calculado tiene un tamaño de muestra de **n = {n}** unidades, tomadas de un lote de **N = {N}** piezas (una fracción de **{f*100:.2f}%**).  
Si en esa muestra se encuentran **hasta {c} defectuosos**, el lote se acepta.

Con este diseño, un lote que contenga una proporción de defectuosos igual al límite de calidad tolerable 
**LTPD = {pL_percent:.2f}%** tendrá una **probabilidad de aceptación de aproximadamente {Pa*100:.2f}%**, 
lo cual corresponde al riesgo del consumidor **β = {beta:.2f}**.

Esto significa que, en promedio, solo **{beta*100:.0f}%** de los lotes “malos” (con calidad igual al LTPD) 
serán aceptados, protegiendo adecuadamente al cliente.

Por otro lado, la **calidad promedio de salida esperada (AOQL)** se estima en **{AOQL*100:.3f}%** de defectuosos.  
Este valor representa el **peor nivel promedio de calidad** que puede llegar al cliente después de aplicar 
el plan de inspección y rectificación de los lotes rechazados.  
Un AOQL más bajo indica un proceso de inspección más estricto y una mejor protección del consumidor.
"""
    st.info(texto)

else:
    st.markdown("""
    ### 🧭 Instrucciones
    1. Ingrese los parámetros en la barra lateral:
       - Tamaño del lote (N)
       - LTPD (% de defectuosos límite)
       - β (riesgo del consumidor)
       - Número de aceptación (c)
    2. Presione **Calcular Plan LTPD**.
    
    El programa calculará automáticamente el tamaño mínimo de muestra **n**
    que garantiza que la probabilidad de aceptar un lote con calidad LTPD
    sea igual o menor al riesgo del consumidor **β**.
    """)
