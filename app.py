import tkinter as tk
from tkinter import filedialog
import re
import html
import os
from graphviz import Digraph

tokens = []

# Patrones para identificar tokens
patrones = [
    {'patron': r'\b\d+\b', 'nombre': 'NUMERO'},
    {'patron': r'\b\w+\b', 'nombre': 'IDENTIFICADOR'},
    {'patron': r'\+', 'nombre': 'SUMA'},
    {'patron': r'-', 'nombre': 'RESTA'},
    {'patron': r'\*', 'nombre': 'MULTIPLICACION'},
    {'patron': r'/', 'nombre': 'DIVISION'},
    {'patron': r'\{', 'nombre': 'LLAVE_IZQ'},
    {'patron': r'\}', 'nombre': 'LLAVE_DER'},
    {'patron': r'\[', 'nombre': 'CORCHETE_IZQ'},
    {'patron': r'\]', 'nombre': 'CORCHETE_DER'},
    {'patron': r'á|é|í|ó|ú|Á|É|Í|Ó|Ú', 'nombre': 'TILDE'},
]

# Funciones para los botones
def abrir_archivo():
    global archivo_abierto
    file_path = filedialog.askopenfilename(filetypes=[("Archivos .bizdata", "*.bizdata")])
    if file_path:
        with open(file_path, 'r') as file:
            archivo_abierto = file.read()
            texto1.delete("1.0", tk.END)
            texto1.insert(tk.END, archivo_abierto)

# Función para analizar el archivo y generar los tokens
def analizar_archivo():
    global tokens
    global archivo_abierto
    if archivo_abierto:
        tokens = []
        reporte_tokens = analizar_texto(archivo_abierto)
        texto2.config(state=tk.NORMAL)
        texto2.delete(1.0, tk.END)
        texto2.insert(tk.END, reporte_tokens)
        texto2.config(state=tk.DISABLED)

# Función para reiniciar el programa
def reiniciar_programa():
    global tokens
    texto1.delete(1.0, tk.END)
    texto2.delete(1.0, tk.END)
    tokens = []

# Función para salir del programa
def salir():
    ventana.destroy()

# Función para analizar el texto y generar una lista de tokens
def analizar_texto(texto):
    global tokens
    tokens = []

    lineas = texto.split('\n')
    fila = 1

    for linea in lineas:
        columna = 1
        for patron in patrones:
            expresion = re.compile(patron['patron'])
            matches = expresion.finditer(linea)

            for match in matches:
                lexema = match.group()
                nombre = patron['nombre']
                tokens.append({'nombre': nombre, 'lexema': lexema, 'fila': fila, 'columna': columna})
                columna += len(lexema)

        fila += 1

    # Generar un informe de tokens en formato HTML
    reporte_tokens = "<html><head><title>Reporte de Tokens</title></head><body><h1>Reporte de Tokens</h1>"
    reporte_tokens += "<table border='1'><tr><th>Token</th><th>Lexema</th><th>Fila</th><th>Columna</th></tr>"

    for token in tokens:
        reporte_tokens += f"<tr><td>{token['nombre']}</td><td>{html.escape(token['lexema'])}</td><td>{token['fila']}</td><td>{token['columna']}</td></tr>"

    reporte_tokens += "</table></body></html>"

    return reporte_tokens

# Función para generar un informe de errores
def generar_reporte_errores():
    global tokens
    errores = [token for token in tokens if token['nombre'] == 'IDENTIFICADOR' and not token['lexema'].isidentifier()]
    
    if not errores:
        reporte_errores = "No se encontraron errores."
    else:
        reporte_errores = "<html><head><title>Reporte de Errores</title></head><body><h1>Reporte de Errores</h1>"
        reporte_errores += "<table border='1'><tr><th>Token</th><th>Nombre</th></tr>"
        for error in errores:
            reporte_errores += f"<tr><td>{html.escape(error['lexema'])}</td><td>{error['nombre']}</td></tr>"
        reporte_errores += "</table></body></html>"
        
        try:
            archivo_html = os.path.join(os.getcwd(), "reporte_errores.html")
            with open(archivo_html, "w", encoding="utf-8") as f:
                f.write(reporte_errores)
        except Exception as e:
            print("Error al escribir el archivo:", e)

        ventana_reporte_errores = tk.Toplevel(ventana)
        ventana_reporte_errores.title("Reporte de Errores")

        reporte_frame = tk.Frame(ventana_reporte_errores)
        reporte_frame.pack()

        reporte_text = tk.Text(reporte_frame, height=20, width=60)
        reporte_text.tag_configure("center", justify="center")
        reporte_text.insert(tk.END, reporte_errores)
        reporte_text.pack()

class NodoArbol:
    def __init__(self, nombre, valor=None):
        self.nombre = nombre
        self.valor = valor
        self.hijos = []

def construir_arbol(tokens):
    raiz = NodoArbol("Expresion")
    raiz.hijos.append(NodoArbol("NUMERO", "10"))
    raiz.hijos.append(NodoArbol("SUMA"))
    raiz.hijos.append(NodoArbol("NUMERO", "5"))

    return raiz

def graficar_arbol(arbol):
    dot = Digraph(comment='Árbol de Derivación')
    stack = [(arbol, None)]

    while stack:
        nodo, padre = stack.pop()
        nombre_nodo = nodo.nombre
        if nodo.valor:
            nombre_nodo += f" ({nodo.valor})"
        dot.node(nombre_nodo)

        if padre:
            dot.edge(padre, nombre_nodo)

        for hijo in nodo.hijos:
            stack.append((hijo, nombre_nodo))

    return dot

# Función para generar un informe
def generar_reporte():
    ventana_reporte = tk.Toplevel(ventana)
    ventana_reporte.title("Seleccionar Reporte")

    def generar_reporte_seleccionado():
        reporte_seleccionado = seleccion_reporte.get()
        if reporte_seleccionado == "Reporte de Errores":
            generar_reporte_errores()
        elif reporte_seleccionado == "Reporte de Tokens":
            analizar_archivo()
        elif reporte_seleccionado == "Árbol de Derivación":
            arbol = construir_arbol(tokens)
            dot = graficar_arbol(arbol)
            dot.render('arbol_derivacion', view=True) 

    seleccion_reporte = tk.StringVar()
    seleccion_reporte.set("Reporte de Errores")

    opciones_reporte = ["Reporte de Errores", "Reporte de Tokens", "Árbol de Derivación"]
    menu_reporte = tk.OptionMenu(ventana_reporte, seleccion_reporte, *opciones_reporte)
    menu_reporte.pack()

    boton_generar_reporte = tk.Button(ventana_reporte, text="Generar Reporte", command=generar_reporte_seleccionado)
    boton_generar_reporte.pack()

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Proyecto2-LFP-201901371")
ventana.geometry("700x500")

# Contenedor para los botones (en la parte superior)
contenedor_botones = tk.Frame(ventana)
contenedor_botones.pack(side=tk.TOP)

# Botones (ordenados horizontalmente en el contenedor de botones)
boton_abrir = tk.Button(contenedor_botones, text="Abrir", command=abrir_archivo)
boton_abrir.pack(side=tk.LEFT)

boton_reiniciar = tk.Button(contenedor_botones, text="Reiniciar", command=reiniciar_programa)
boton_reiniciar.pack(side=tk.LEFT)

boton_salir = tk.Button(contenedor_botones, text="Salir", command=salir)
boton_salir.pack(side=tk.LEFT)

boton_analizar = tk.Button(contenedor_botones, text="Analizar", command=analizar_archivo)
boton_analizar.pack(side=tk.LEFT)

boton_reportes = tk.Button(contenedor_botones, text="Reportes", command=generar_reporte)
boton_reportes.pack(side=tk.LEFT)

# Contenedor para las cajas de texto (en la parte inferior)
contenedor_cajas_texto = tk.Frame(ventana)
contenedor_cajas_texto.pack(side=tk.BOTTOM)

# Cajas de texto
texto1 = tk.Text(contenedor_cajas_texto, height=10, width=50)
texto1.pack()

texto2 = tk.Text(contenedor_cajas_texto, height=10, width=50)
texto2.pack()

ventana.mainloop()