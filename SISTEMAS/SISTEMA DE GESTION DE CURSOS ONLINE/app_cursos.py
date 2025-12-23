import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import sqlite3
import os
from datetime import datetime, timedelta
import io
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
import time
import functools

# ------------------------------------------------------------
# Configuración y Estilos
# ------------------------------------------------------------
st.set_page_config(page_title="Sistema de Gestión de Cursos Online", page_icon="🎓", layout="wide")

# Custom CSS for Professional Look
st.markdown("""
    <style>
    /* Global Font */
    .stApp {
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-weight: 600;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-weight: bold;
        color: #2980b9; 
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #2980b9;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #3498db;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    /* Tables */
    [data-testid="stDataFrame"] {
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------
# Base de Datos
# ------------------------------------------------------------
DB_PATH = "cursos_online.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS estudiantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                telefono TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cursos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                duracion_horas INTEGER,
                nivel TEXT,
                activo INTEGER DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inscripciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estudiante_id INTEGER NOT NULL,
                curso_id INTEGER NOT NULL,
                fecha_inscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                estado TEXT DEFAULT 'Activo',
                nota_final REAL,
                UNIQUE(estudiante_id, curso_id),
                FOREIGN KEY(estudiante_id) REFERENCES estudiantes(id),
                FOREIGN KEY(curso_id) REFERENCES cursos(id)
            )
        """)
        # Nuevas tablas para Exámenes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS examenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                curso_id INTEGER NOT NULL,
                titulo TEXT NOT NULL,
                descripcion TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(curso_id) REFERENCES cursos(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS preguntas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                examen_id INTEGER NOT NULL,
                texto_pregunta TEXT NOT NULL,
                tipo_pregunta TEXT NOT NULL, -- 'multiple', 'abierta', 'verdadero_falso'
                opciones TEXT, -- JSON o texto separado por pipes para opciones
                respuesta_correcta TEXT,
                FOREIGN KEY(examen_id) REFERENCES examenes(id)
            )
        """)
        # Tabla para métricas de rendimiento
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                accion TEXT NOT NULL,
                tiempo_ejecucion REAL NOT NULL,
                fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                detalles TEXT
            )
        """)
        conn.commit()

init_db()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ------------------------------------------------------------
# Sistema de Medición de Tiempo
# ------------------------------------------------------------

def guardar_metrica_rendimiento(accion, tiempo_ejecucion, detalles=""):
    """Guarda una métrica de rendimiento en la base de datos"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO performance_metrics (accion, tiempo_ejecucion, detalles) VALUES (?, ?, ?)",
                (accion, tiempo_ejecucion, detalles)
            )
            conn.commit()
    except Exception as e:
        print(f"Error guardando métrica: {e}")

def measure_time(accion_nombre):
    """Decorador para medir el tiempo de ejecución de funciones"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            inicio = time.time()
            resultado = func(*args, **kwargs)
            fin = time.time()
            tiempo_ejecucion = (fin - inicio) * 1000  # Convertir a milisegundos
            
            # Guardar métrica
            detalles = f"Función: {func.__name__}"
            guardar_metrica_rendimiento(accion_nombre, tiempo_ejecucion, detalles)
            
            # Mostrar notificación en Streamlit si está disponible
            if tiempo_ejecucion > 1000:  # Si tarda más de 1 segundo
                st.toast(f"⏱️ {accion_nombre}: {tiempo_ejecucion:.2f}ms", icon="⚠️")
            else:
                st.toast(f"✅ {accion_nombre}: {tiempo_ejecucion:.2f}ms", icon="⚡")
            
            return resultado
        return wrapper
    return decorator

def obtener_metricas_rendimiento(limite=100):
    """Obtiene las métricas de rendimiento de la base de datos"""
    conn = get_db_connection()
    query = f"""
        SELECT * FROM performance_metrics 
        ORDER BY fecha_hora DESC 
        LIMIT {limite}
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def obtener_estadisticas_rendimiento():
    """Obtiene estadísticas agregadas de rendimiento por acción"""
    conn = get_db_connection()
    query = """
        SELECT 
            accion,
            COUNT(*) as total_ejecuciones,
            AVG(tiempo_ejecucion) as tiempo_promedio,
            MIN(tiempo_ejecucion) as tiempo_minimo,
            MAX(tiempo_ejecucion) as tiempo_maximo,
            SUM(tiempo_ejecucion) as tiempo_total
        FROM performance_metrics
        GROUP BY accion
        ORDER BY tiempo_promedio DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ------------------------------------------------------------
# Funciones CRUD y Lógica
# ------------------------------------------------------------

def ejecutar_query(query, params=(), commit=False):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        if commit:
            conn.commit()
        return True, cursor
    except Exception as e:
        return False, str(e)
    finally:
        if 'conn' in locals():
            conn.close()

# --- Estudiantes ---
@measure_time("Crear Estudiante")
def crear_estudiante(nombre, email, telefono):
    return ejecutar_query("INSERT INTO estudiantes (nombre, email, telefono) VALUES (?, ?, ?)", 
                          (nombre, email, telefono), commit=True)

def obtener_estudiantes():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM estudiantes", conn)
    conn.close()
    return df

def obtener_estudiante_por_id(id):
    conn = get_db_connection()
    res = conn.execute("SELECT * FROM estudiantes WHERE id = ?", (id,)).fetchone()
    conn.close()
    return dict(res) if res else None

@measure_time("Actualizar Estudiante")
def actualizar_estudiante(id, nombre, email, telefono):
    return ejecutar_query("UPDATE estudiantes SET nombre = ?, email = ?, telefono = ? WHERE id = ?", 
                          (nombre, email, telefono, id), commit=True)

@measure_time("Eliminar Estudiante")
def eliminar_estudiante(id):
    return ejecutar_query("DELETE FROM estudiantes WHERE id = ?", (id,), commit=True)

# --- Cursos ---
@measure_time("Crear Curso")
def crear_curso(nombre, descripcion, duracion, nivel):
    return ejecutar_query("INSERT INTO cursos (nombre, descripcion, duracion_horas, nivel) VALUES (?, ?, ?, ?)", 
                          (nombre, descripcion, duracion, nivel), commit=True)

def obtener_cursos():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM cursos", conn)
    conn.close()
    return df

def obtener_curso_por_id(id):
    conn = get_db_connection()
    res = conn.execute("SELECT * FROM cursos WHERE id = ?", (id,)).fetchone()
    conn.close()
    return dict(res) if res else None

@measure_time("Actualizar Curso")
def actualizar_curso(id, nombre, descripcion, duracion, nivel):
    return ejecutar_query("UPDATE cursos SET nombre = ?, descripcion = ?, duracion_horas = ?, nivel = ? WHERE id = ?", 
                          (nombre, descripcion, duracion, nivel, id), commit=True)

@measure_time("Eliminar Curso")
def eliminar_curso(id):
    conn = get_db_connection()
    count = conn.execute("SELECT COUNT(*) FROM inscripciones WHERE curso_id = ?", (id,)).fetchone()[0]
    conn.close()
    if count > 0:
        return False, "No se puede eliminar: Hay estudiantes inscritos."
    return ejecutar_query("DELETE FROM cursos WHERE id = ?", (id,), commit=True)

# --- Inscripciones ---
@measure_time("Matricular Estudiante")
def matricular_estudiante(estudiante_id, curso_id):
    return ejecutar_query("INSERT INTO inscripciones (estudiante_id, curso_id) VALUES (?, ?)", 
                          (estudiante_id, curso_id), commit=True)

def obtener_inscripciones():
    conn = get_db_connection()
    query = """
        SELECT i.id, e.nombre as estudiante, c.nombre as curso, i.fecha_inscripcion, i.estado
        FROM inscripciones i
        JOIN estudiantes e ON i.estudiante_id = e.id
        JOIN cursos c ON i.curso_id = c.id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@measure_time("Eliminar Inscripción")
def eliminar_inscripcion(id):
    return ejecutar_query("DELETE FROM inscripciones WHERE id = ?", (id,), commit=True)

# --- Exámenes ---
@measure_time("Crear Examen")
def crear_examen(curso_id, titulo, descripcion):
    return ejecutar_query("INSERT INTO examenes (curso_id, titulo, descripcion) VALUES (?, ?, ?)", 
                          (curso_id, titulo, descripcion), commit=True)

def agregar_pregunta(examen_id, texto, tipo, opciones, correcta):
    return ejecutar_query("INSERT INTO preguntas (examen_id, texto_pregunta, tipo_pregunta, opciones, respuesta_correcta) VALUES (?, ?, ?, ?, ?)",
                          (examen_id, texto, tipo, opciones, correcta), commit=True)

def obtener_examenes():
    conn = get_db_connection()
    query = """
        SELECT e.id, c.nombre as curso, e.titulo, e.descripcion, e.fecha_creacion,
               (SELECT COUNT(*) FROM preguntas p WHERE p.examen_id = e.id) as num_preguntas
        FROM examenes e
        JOIN cursos c ON e.curso_id = c.id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ------------------------------------------------------------
# Generación de Datos Sintéticos para KPIs
# ------------------------------------------------------------
def generar_datos_kpi():
    np.random.seed(42)
    fechas = [datetime.now().date() - timedelta(days=i) for i in range(30)]
    fechas.reverse()
    
    data = []
    for fecha in fechas:
        # KPI-01: Rendimiento (Pretest vs Postest)
        pretest = np.random.normal(loc=60, scale=10, size=1)[0]
        postest = pretest + np.random.normal(loc=25, scale=5, size=1)[0]
        postest = min(100, max(0, postest))
        pretest = min(100, max(0, pretest))
        
        # KPI-02: Eficiencia (Tiempo de generación en segundos)
        tiempo_antes = np.random.normal(loc=45, scale=5, size=1)[0]
        tiempo_despues = np.random.normal(loc=15, scale=2, size=1)[0]
        
        # KPI-03: Satisfacción (1-5)
        satisfaccion_pre = np.random.randint(2, 5)
        satisfaccion_post = min(5, satisfaccion_pre + np.random.randint(0, 3))
        
        data.append({
            "Fecha": fecha,
            "KPI-01 Pretest": round(pretest, 1),
            "KPI-01 Postest": round(postest, 1),
            "KPI-02 Tiempo Antes (s)": round(tiempo_antes, 1),
            "KPI-02 Tiempo Después (s)": round(tiempo_despues, 1),
            "KPI-03 Satisfacción Pre": satisfaccion_pre,
            "KPI-03 Satisfacción Post": satisfaccion_post
        })
    return pd.DataFrame(data)

# ------------------------------------------------------------
# Reportes Avanzados
# ------------------------------------------------------------
def generar_reporte_completo():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    title_style = ParagraphStyle('MainTitle', parent=styles['Title'], fontSize=24, spaceAfter=20, textColor=colors.HexColor("#2c3e50"))
    elements.append(Paragraph("Reporte General del Sistema", title_style))
    elements.append(Paragraph(f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # 1. Resumen Estadístico
    estudiantes = obtener_estudiantes()
    cursos = obtener_cursos()
    inscripciones = obtener_inscripciones()
    
    elements.append(Paragraph("Resumen Ejecutivo", styles['Heading2']))
    data_resumen = [
        ['Métrica', 'Valor'],
        ['Total Estudiantes', len(estudiantes)],
        ['Total Cursos', len(cursos)],
        ['Matrículas Activas', len(inscripciones)]
    ]
    t_resumen = Table(data_resumen, colWidths=[200, 100], hAlign='LEFT')
    t_resumen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#34495e")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t_resumen)
    elements.append(Spacer(1, 20))
    
    # 2. Gráficos (Usando Matplotlib/Seaborn para estabilidad en PDF)
    elements.append(Paragraph("Análisis Gráfico", styles['Heading2']))
    
    # Configuración de estilo
    sns.set_theme(style="whitegrid")
    
    # Gráfico 1: Estudiantes por Curso
    if not inscripciones.empty:
        counts = inscripciones['curso'].value_counts().reset_index()
        counts.columns = ['curso', 'count']
        
        plt.figure(figsize=(6, 4))
        sns.barplot(data=counts, x='curso', y='count', palette="viridis")
        plt.title("Estudiantes por Curso")
        plt.xlabel("Curso")
        plt.ylabel("Cantidad")
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        img_buffer1 = io.BytesIO()
        plt.savefig(img_buffer1, format='png', dpi=100)
        plt.close()
        img_buffer1.seek(0)
        
        img1 = RLImage(img_buffer1, width=400, height=300)
        elements.append(img1)
    
    elements.append(Spacer(1, 10))
    
    # Gráfico 2: Distribución de Niveles de Curso
    if not cursos.empty:
        level_counts = cursos['nivel'].value_counts()
        
        plt.figure(figsize=(6, 4))
        plt.pie(level_counts, labels=level_counts.index, autopct='%1.1f%%', colors=sns.color_palette("pastel"))
        plt.title("Distribución de Niveles")
        plt.tight_layout()
        
        img_buffer2 = io.BytesIO()
        plt.savefig(img_buffer2, format='png', dpi=100)
        plt.close()
        img_buffer2.seek(0)
        
        img2 = RLImage(img_buffer2, width=400, height=300)
        elements.append(img2)
        
    elements.append(PageBreak())
    
    # 3. Detalle de Estudiantes
    elements.append(Paragraph("Listado de Estudiantes", styles['Heading2']))
    if not estudiantes.empty:
        data_est = [['ID', 'Nombre', 'Email', 'Teléfono']] + estudiantes[['id', 'nombre', 'email', 'telefono']].values.tolist()
        t_est = Table(data_est, repeatRows=1)
        t_est.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2980b9")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        elements.append(t_est)
    else:
        elements.append(Paragraph("No hay estudiantes registrados.", styles['Normal']))
        
    elements.append(Spacer(1, 20))
    
    # 4. Detalle de Cursos
    elements.append(Paragraph("Listado de Cursos", styles['Heading2']))
    if not cursos.empty:
        data_cur = [['ID', 'Nombre', 'Nivel', 'Duración (h)']] + cursos[['id', 'nombre', 'nivel', 'duracion_horas']].values.tolist()
        t_cur = Table(data_cur, repeatRows=1)
        t_cur.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#27ae60")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        elements.append(t_cur)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# ------------------------------------------------------------
# Interfaz de Usuario
# ------------------------------------------------------------

def main():
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2995/2995620.png", width=100)
    st.sidebar.title("Panel Administrativo")
    menu = st.sidebar.radio("Navegación", ["Dashboard", "Estudiantes", "Cursos", "Matrículas", "Evaluaciones & KPIs", "Rendimiento", "Reportes"])
    
    if menu == "Dashboard":
        st.title("📊 Dashboard Sistema de Gestión de Cursos Online")
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        estudiantes = obtener_estudiantes()
        cursos = obtener_cursos()
        inscripciones = obtener_inscripciones()
        
        col1.metric("Total Estudiantes", len(estudiantes), delta_color="normal")
        col2.metric("Total Cursos", len(cursos), delta_color="normal")
        col3.metric("Matrículas Activas", len(inscripciones), delta_color="normal")
        
        st.markdown("### 📈 Estadísticas")
        c1, c2 = st.columns(2)
        
        with c1:
            if not inscripciones.empty:
                counts = inscripciones['curso'].value_counts().reset_index()
                counts.columns = ['curso', 'count']
                fig = px.bar(counts, x='curso', y='count', title="Estudiantes por Curso", color='count')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sin datos de matrículas.")
                
        with c2:
            if not cursos.empty:
                level_counts = cursos['nivel'].value_counts().reset_index()
                level_counts.columns = ['nivel', 'count']
                fig = px.pie(level_counts, values='count', names='nivel', title="Distribución de Niveles", hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sin datos de cursos.")

    elif menu == "Estudiantes":
        st.title("👥 Gestión de Estudiantes")
        
        tab1, tab2 = st.tabs(["📋 Listado", "➕ Nuevo Estudiante"])
        
        with tab1:
            df = obtener_estudiantes()
            
            # Edición
            if 'edit_est_id' not in st.session_state:
                st.session_state.edit_est_id = None
            
            if st.session_state.edit_est_id:
                st.subheader("Editar Estudiante")
                est = obtener_estudiante_por_id(st.session_state.edit_est_id)
                if est:
                    with st.form("edit_est_form"):
                        n_nombre = st.text_input("Nombre", est['nombre'])
                        n_email = st.text_input("Email", est['email'])
                        n_telefono = st.text_input("Teléfono", est['telefono'])
                        c1, c2 = st.columns(2)
                        if c1.form_submit_button("Guardar Cambios"):
                            ok, msg = actualizar_estudiante(est['id'], n_nombre, n_email, n_telefono)
                            if ok:
                                st.success(msg)
                                st.session_state.edit_est_id = None
                                st.rerun()
                            else:
                                st.error(msg)
                        if c2.form_submit_button("Cancelar"):
                            st.session_state.edit_est_id = None
                            st.rerun()
            
            st.dataframe(df, use_container_width=True)
            
            c1, c2 = st.columns(2)
            with c1:
                id_to_edit = st.number_input("ID a Editar", min_value=1, step=1, key="edit_est_input")
                if st.button("✏️ Editar Seleccionado"):
                    st.session_state.edit_est_id = id_to_edit
                    st.rerun()
            
            with c2:
                id_to_del = st.number_input("ID a Eliminar", min_value=1, step=1, key="del_est_input")
                if st.button("🗑️ Eliminar Seleccionado"):
                    ok, msg = eliminar_estudiante(id_to_del)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        with tab2:
            with st.form("new_est_form"):
                nombre = st.text_input("Nombre Completo")
                email = st.text_input("Email")
                telefono = st.text_input("Teléfono")
                if st.form_submit_button("Registrar"):
                    if nombre and email:
                        ok, msg = crear_estudiante(nombre, email, telefono)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)
                    else:
                        st.warning("Nombre y Email requeridos")

    elif menu == "Cursos":
        st.title("📚 Gestión de Cursos")
        
        tab1, tab2 = st.tabs(["📋 Listado", "➕ Nuevo Curso"])
        
        with tab1:
            df = obtener_cursos()
            
            # Edición
            if 'edit_cur_id' not in st.session_state:
                st.session_state.edit_cur_id = None
                
            if st.session_state.edit_cur_id:
                st.subheader("Editar Curso")
                cur = obtener_curso_por_id(st.session_state.edit_cur_id)
                if cur:
                    with st.form("edit_cur_form"):
                        n_nombre = st.text_input("Nombre", cur['nombre'])
                        n_desc = st.text_area("Descripción", cur['descripcion'])
                        n_dur = st.number_input("Duración", value=cur['duracion_horas'])
                        n_nivel = st.selectbox("Nivel", ["Básico", "Intermedio", "Avanzado"], index=["Básico", "Intermedio", "Avanzado"].index(cur['nivel']))
                        
                        c1, c2 = st.columns(2)
                        if c1.form_submit_button("Guardar Cambios"):
                            ok, msg = actualizar_curso(cur['id'], n_nombre, n_desc, n_dur, n_nivel)
                            if ok:
                                st.success(msg)
                                st.session_state.edit_cur_id = None
                                st.rerun()
                            else:
                                st.error(msg)
                        if c2.form_submit_button("Cancelar"):
                            st.session_state.edit_cur_id = None
                            st.rerun()

            st.dataframe(df, use_container_width=True)
            
            c1, c2 = st.columns(2)
            with c1:
                id_to_edit = st.number_input("ID a Editar", min_value=1, step=1, key="edit_cur_input")
                if st.button("✏️ Editar Curso"):
                    st.session_state.edit_cur_id = id_to_edit
                    st.rerun()
            
            with c2:
                id_to_del = st.number_input("ID a Eliminar", min_value=1, step=1, key="del_cur_input")
                if st.button("🗑️ Eliminar Curso"):
                    ok, msg = eliminar_curso(id_to_del)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        with tab2:
            with st.form("new_cur_form"):
                nombre = st.text_input("Nombre del Curso")
                descripcion = st.text_area("Descripción")
                duracion = st.number_input("Duración (horas)", min_value=1)
                nivel = st.selectbox("Nivel", ["Básico", "Intermedio", "Avanzado"])
                if st.form_submit_button("Crear Curso"):
                    if nombre:
                        ok, msg = crear_curso(nombre, descripcion, duracion, nivel)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)
                    else:
                        st.warning("Nombre requerido")

    elif menu == "Matrículas":
        st.title("📝 Gestión de Matrículas")
        
        c1, c2 = st.columns([1, 2])
        
        with c1:
            st.markdown("### Nueva Inscripción")
            estudiantes = obtener_estudiantes()
            cursos = obtener_cursos()
            
            if not estudiantes.empty and not cursos.empty:
                est_map = {f"{r['id']} - {r['nombre']}": r['id'] for _, r in estudiantes.iterrows()}
                cur_map = {f"{r['id']} - {r['nombre']}": r['id'] for _, r in cursos.iterrows()}
                
                sel_est = st.selectbox("Estudiante", list(est_map.keys()))
                sel_cur = st.selectbox("Curso", list(cur_map.keys()))
                
                if st.button("✅ Matricular"):
                    ok, msg = matricular_estudiante(est_map[sel_est], cur_map[sel_cur])
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            else:
                st.warning("Registre estudiantes y cursos primero.")
                
        with c2:
            st.markdown("### Inscripciones Activas")
            df = obtener_inscripciones()
            st.dataframe(df, use_container_width=True)
            
            if not df.empty:
                id_del = st.number_input("ID Matrícula a Cancelar", min_value=1, step=1)
                if st.button("❌ Cancelar Matrícula"):
                    ok, msg = eliminar_inscripcion(id_del)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    elif menu == "Evaluaciones & KPIs":
        st.title("📊 Evaluaciones y Análisis KPI")
        
        tab1, tab2 = st.tabs(["📝 Gestión de Evaluaciones", "📈 Dashboard de KPIs"])
        
        with tab1:
            st.subheader("Crear Nueva Evaluación")
            cursos = obtener_cursos()
            if not cursos.empty:
                cur_map = {f"{r['id']} - {r['nombre']}": r['id'] for _, r in cursos.iterrows()}
                sel_cur_ex = st.selectbox("Curso para el examen", list(cur_map.keys()))
                
                with st.form("crear_examen_form"):
                    titulo_ex = st.text_input("Título del Examen")
                    desc_ex = st.text_area("Descripción")
                    
                    st.markdown("#### Preguntas")
                    # Simulación de agregar preguntas dinámicamente (en una app real sería más complejo con estados)
                    p1_txt = st.text_input("Pregunta 1")
                    p1_tipo = st.selectbox("Tipo P1", ["Opción Múltiple", "Verdadero/Falso", "Abierta"])
                    
                    p2_txt = st.text_input("Pregunta 2")
                    p2_tipo = st.selectbox("Tipo P2", ["Opción Múltiple", "Verdadero/Falso", "Abierta"])
                    
                    if st.form_submit_button("Guardar Examen"):
                        if titulo_ex:
                            ok, cursor = crear_examen(cur_map[sel_cur_ex], titulo_ex, desc_ex)
                            if ok:
                                ex_id = cursor.lastrowid
                                if p1_txt:
                                    agregar_pregunta(ex_id, p1_txt, p1_tipo, "", "")
                                if p2_txt:
                                    agregar_pregunta(ex_id, p2_txt, p2_tipo, "", "")
                                st.success("Examen creado exitosamente.")
                            else:
                                st.error("Error al crear examen.")
                        else:
                            st.warning("El título es obligatorio.")
            
            st.markdown("---")
            st.subheader("Exámenes Existentes")
            df_ex = obtener_examenes()
            st.dataframe(df_ex, use_container_width=True)

        with tab2:
            st.subheader("Análisis de KPIs (Últimos 30 días)")
            
            # Generar datos
            df_kpi = generar_datos_kpi()
            
            # 1. Tabla de Datos
            with st.expander("Ver Tabla de Datos Recopilados", expanded=True):
                st.dataframe(df_kpi, use_container_width=True)
            
            # 2. KPI-01: Rendimiento
            st.markdown("### KPI-01: Rendimiento Académico (Pretest vs Postest)")
            c1, c2 = st.columns(2)
            
            with c1:
                st.markdown("**Estadísticas Descriptivas**")
                desc = df_kpi[["KPI-01 Pretest", "KPI-01 Postest"]].describe().T
                st.dataframe(desc[["mean", "50%", "std"]].rename(columns={"50%": "mediana"}), use_container_width=True)
                
            with c2:
                st.markdown("**Prueba de Normalidad (Q-Q Plot) - Postest**")
                fig_qq, ax = plt.subplots()
                stats.probplot(df_kpi["KPI-01 Postest"], dist="norm", plot=ax)
                ax.set_title("Q-Q Plot: KPI-01 Postest")
                st.pyplot(fig_qq)
                
            # 3. KPI-02: Eficiencia
            st.markdown("### KPI-02: Eficiencia (Tiempo de Generación)")
            c3, c4 = st.columns(2)
            
            with c3:
                st.markdown("**Comparativa de Tiempos (Antes vs Después)**")
                avg_tiempos = df_kpi[["KPI-02 Tiempo Antes (s)", "KPI-02 Tiempo Después (s)"]].mean()
                fig_bar = px.bar(x=avg_tiempos.index, y=avg_tiempos.values, 
                                 labels={'x': 'Etapa', 'y': 'Tiempo Promedio (s)'},
                                 title="Tiempo Promedio de Generación", color=avg_tiempos.index)
                st.plotly_chart(fig_bar, use_container_width=True)
                
            with c4:
                st.markdown("**Prueba de Hipótesis (T-test)**")
                t_stat, p_val = stats.ttest_rel(df_kpi["KPI-02 Tiempo Antes (s)"], df_kpi["KPI-02 Tiempo Después (s)"])
                st.info(f"""
                **T-test Relacionado:**
                - Estadístico T: {t_stat:.4f}
                - Valor P: {p_val:.4e}
                
                Interpretación: {'Diferencia significativa (Rechaza H0)' if p_val < 0.05 else 'No hay diferencia significativa'}
                """)
                
            # 4. KPI-03: Satisfacción
            st.markdown("### KPI-03: Satisfacción del Usuario")
            df_melt = df_kpi.melt(value_vars=["KPI-03 Satisfacción Pre", "KPI-03 Satisfacción Post"], var_name="Etapa", value_name="Nivel")
            fig_box = px.box(df_melt, x="Etapa", y="Nivel", color="Etapa", title="Distribución de Satisfacción (Pre vs Post)")
            st.plotly_chart(fig_box, use_container_width=True)

    elif menu == "Rendimiento":
        st.title("⚡ Monitoreo de Rendimiento del Sistema")
        st.markdown("Visualiza el tiempo de ejecución de cada operación del sistema en tiempo real.")
        st.markdown("---")
        
        # Métricas principales
        try:
            df_metricas = obtener_metricas_rendimiento()
            df_stats = obtener_estadisticas_rendimiento()
            
            if not df_metricas.empty:
                # Estadísticas generales
                col1, col2, col3, col4 = st.columns(4)
                
                total_operaciones = len(df_metricas)
                tiempo_promedio_global = df_metricas['tiempo_ejecucion'].mean()
                tiempo_total = df_metricas['tiempo_ejecucion'].sum()
                operacion_mas_lenta = df_metricas.loc[df_metricas['tiempo_ejecucion'].idxmax(), 'accion'] if not df_metricas.empty else "N/A"
                
                col1.metric("Total Operaciones", f"{total_operaciones:,}")
                col2.metric("Tiempo Promedio", f"{tiempo_promedio_global:.2f} ms")
                col3.metric("Tiempo Total", f"{tiempo_total:.2f} ms")
                col4.metric("Más Lenta", operacion_mas_lenta)
                
                st.markdown("---")
                
                # Tabs para diferentes vistas
                tab1, tab2, tab3 = st.tabs(["📊 Estadísticas por Acción", "📈 Historial Reciente", "🔍 Análisis Detallado"])
                
                with tab1:
                    st.subheader("Estadísticas Agregadas por Tipo de Acción")
                    
                    if not df_stats.empty:
                        # Tabla de estadísticas
                        df_stats_display = df_stats.copy()
                        df_stats_display['tiempo_promedio'] = df_stats_display['tiempo_promedio'].round(2)
                        df_stats_display['tiempo_minimo'] = df_stats_display['tiempo_minimo'].round(2)
                        df_stats_display['tiempo_maximo'] = df_stats_display['tiempo_maximo'].round(2)
                        df_stats_display['tiempo_total'] = df_stats_display['tiempo_total'].round(2)
                        
                        st.dataframe(df_stats_display, use_container_width=True)
                        
                        # Gráfico de barras - Tiempo promedio por acción
                        st.markdown("### Tiempo Promedio de Ejecución por Acción")
                        fig_bar = px.bar(
                            df_stats, 
                            x='accion', 
                            y='tiempo_promedio',
                            title='Tiempo Promedio de Ejecución (ms)',
                            labels={'tiempo_promedio': 'Tiempo (ms)', 'accion': 'Acción'},
                            color='tiempo_promedio',
                            color_continuous_scale='RdYlGn_r'
                        )
                        fig_bar.update_layout(xaxis_tickangle=-45)
                        st.plotly_chart(fig_bar, use_container_width=True)
                        
                        # Gráfico de pastel - Distribución de tiempo total
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("### Distribución de Tiempo Total")
                            fig_pie = px.pie(
                                df_stats,
                                values='tiempo_total',
                                names='accion',
                                title='Distribución del Tiempo Total por Acción',
                                hole=0.4
                            )
                            st.plotly_chart(fig_pie, use_container_width=True)
                        
                        with col2:
                            st.markdown("### Número de Ejecuciones")
                            fig_exe = px.bar(
                                df_stats,
                                x='accion',
                                y='total_ejecuciones',
                                title='Total de Ejecuciones por Acción',
                                labels={'total_ejecuciones': 'Ejecuciones', 'accion': 'Acción'},
                                color='total_ejecuciones',
                                color_continuous_scale='Blues'
                            )
                            fig_exe.update_layout(xaxis_tickangle=-45)
                            st.plotly_chart(fig_exe, use_container_width=True)
                    else:
                        st.info("No hay estadísticas disponibles aún.")
                
                with tab2:
                    st.subheader("Historial de Operaciones Recientes")
                    
                    # Filtros
                    col1, col2 = st.columns(2)
                    with col1:
                        limite = st.slider("Número de registros", 10, 200, 50)
                    with col2:
                        acciones_unicas = df_metricas['accion'].unique().tolist()
                        filtro_accion = st.multiselect("Filtrar por acción", acciones_unicas, default=acciones_unicas)
                    
                    # Obtener datos filtrados
                    df_filtrado = obtener_metricas_rendimiento(limite)
                    if filtro_accion:
                        df_filtrado = df_filtrado[df_filtrado['accion'].isin(filtro_accion)]
                    
                    # Tabla de historial
                    st.dataframe(df_filtrado, use_container_width=True)
                    
                    # Gráfico de línea temporal
                    if not df_filtrado.empty:
                        st.markdown("### Evolución Temporal del Rendimiento")
                        fig_line = px.line(
                            df_filtrado.sort_values('fecha_hora'),
                            x='fecha_hora',
                            y='tiempo_ejecucion',
                            color='accion',
                            title='Tiempo de Ejecución a lo Largo del Tiempo',
                            labels={'tiempo_ejecucion': 'Tiempo (ms)', 'fecha_hora': 'Fecha/Hora'},
                            markers=True
                        )
                        st.plotly_chart(fig_line, use_container_width=True)
                
                with tab3:
                    st.subheader("Análisis Detallado de Rendimiento")
                    
                    if not df_stats.empty:
                        # Seleccionar acción para análisis
                        accion_seleccionada = st.selectbox("Selecciona una acción para análisis detallado", df_stats['accion'].tolist())
                        
                        if accion_seleccionada:
                            # Filtrar datos de la acción seleccionada
                            df_accion = df_metricas[df_metricas['accion'] == accion_seleccionada]
                            
                            if not df_accion.empty:
                                # Métricas específicas
                                col1, col2, col3, col4 = st.columns(4)
                                col1.metric("Ejecuciones", len(df_accion))
                                col2.metric("Promedio", f"{df_accion['tiempo_ejecucion'].mean():.2f} ms")
                                col3.metric("Mínimo", f"{df_accion['tiempo_ejecucion'].min():.2f} ms")
                                col4.metric("Máximo", f"{df_accion['tiempo_ejecucion'].max():.2f} ms")
                                
                                # Histograma de distribución
                                st.markdown("### Distribución de Tiempos de Ejecución")
                                fig_hist = px.histogram(
                                    df_accion,
                                    x='tiempo_ejecucion',
                                    nbins=20,
                                    title=f'Distribución de Tiempos - {accion_seleccionada}',
                                    labels={'tiempo_ejecucion': 'Tiempo (ms)', 'count': 'Frecuencia'}
                                )
                                st.plotly_chart(fig_hist, use_container_width=True)
                                
                                # Box plot
                                st.markdown("### Análisis de Dispersión")
                                fig_box = px.box(
                                    df_accion,
                                    y='tiempo_ejecucion',
                                    title=f'Box Plot - {accion_seleccionada}',
                                    labels={'tiempo_ejecucion': 'Tiempo (ms)'}
                                )
                                st.plotly_chart(fig_box, use_container_width=True)
                            else:
                                st.info("No hay datos para esta acción.")
                    else:
                        st.info("No hay datos suficientes para el análisis.")
                
                # Botón para limpiar métricas
                st.markdown("---")
                if st.button("🗑️ Limpiar Historial de Métricas"):
                    try:
                        with sqlite3.connect(DB_PATH) as conn:
                            conn.execute("DELETE FROM performance_metrics")
                            conn.commit()
                        st.success("Historial de métricas limpiado exitosamente.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al limpiar métricas: {e}")
                        
            else:
                st.info("📊 No hay métricas de rendimiento disponibles aún. Realiza algunas operaciones en el sistema para comenzar a recopilar datos.")
                st.markdown("""
                ### ¿Cómo funciona?
                
                El sistema automáticamente mide y registra el tiempo de ejecución de cada operación:
                - ✅ Crear, actualizar y eliminar estudiantes
                - ✅ Crear, actualizar y eliminar cursos
                - ✅ Matricular estudiantes
                - ✅ Crear exámenes
                - ✅ Y más...
                
                **Realiza algunas operaciones y vuelve aquí para ver las métricas!**
                """)
        
        except Exception as e:
            st.error(f"Error al cargar métricas de rendimiento: {e}")

    elif menu == "Reportes":
        st.title("📑 Generación de Reportes")
        st.markdown("Genera un reporte completo en PDF con estadísticas, gráficos y listados detallados.")
        
        if st.button("📄 Generar Reporte Completo (PDF)"):
            with st.spinner("Generando reporte..."):
                try:
                    pdf_buffer = generar_reporte_completo()
                    st.success("¡Reporte generado exitosamente!")
                    st.download_button(
                        label="⬇️ Descargar Reporte PDF",
                        data=pdf_buffer,
                        file_name="reporte_general.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"Error al generar el reporte: {e}")

if __name__ == "__main__":
    main()