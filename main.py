import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from ttkthemes import ThemedTk #biblioteca para temas 

class HotelApp:
    def __init__(self, conn):
        self.conn = conn
        self.c = self.conn.cursor() #abrir coneccion a la base de datos

        self.root = ThemedTk(theme="equilux")  # Cambia el tema según tus preferencias
        self.root.title("Gestión de Hotel")

        # Crear el contenedor de pestañas (Notebook)
        self.notebook = ttk.Notebook(self.root)

        # Estilos
        style = ttk.Style(self.root)
        style.configure('TLabel', font=('Arial', 12), background='#1e1e1e', foreground='#ffffff') #estilos de los titlos
        style.configure('TButton', font=('Arial', 12), background='#4CAF50', foreground='white') #estilos de los botones

        # Pestaña para Habitaciones Disponibles y Nuevo Cliente
        self.frame_habitaciones_disponibles = ttk.Frame(self.notebook)

        self.label_habitaciones = ttk.Label(self.frame_habitaciones_disponibles, text="Habitaciones Disponibles:") #titulo de la pagina (leabel)
        self.listbox_habitaciones = tk.Listbox(self.frame_habitaciones_disponibles, selectmode=tk.SINGLE, exportselection=False, width=30, height=10) #añadir la listbox (la caja de las listas)
        self.actualizar_habitaciones() #ejecuta la funcion que trae las habitaciones de la base de datos, a medida que se ejecuta se actualizan 

        #coniguaracion del listbox
        self.label_habitaciones.pack(side=tk.TOP, anchor=tk.CENTER, padx=10, pady=5)
        self.listbox_habitaciones.pack(side=tk.TOP, padx=10, pady=5)

        self.label_cliente = ttk.Label(self.frame_habitaciones_disponibles, text="Nuevo Cliente:") #leabel de nuevos clientes
        self.entry_cliente = ttk.Entry(self.frame_habitaciones_disponibles) #input para nuevos clientes
        self.btn_ocupar = ttk.Button(self.frame_habitaciones_disponibles, text="Ocupar Habitación", command=self.ocupar_habitacion) #boton para ejecutar la funcion para ocuoar las habitaciones
        self.btn_desocupar = ttk.Button(self.frame_habitaciones_disponibles, text="Desocupar Habitación", command=self.desocupar_habitacion) #boton para ejecutar la funcion para desocupar las habitaciones

        # configuracion y estilos para los btns 
        self.label_cliente.pack(side=tk.TOP, anchor=tk.CENTER, padx=10, pady=5) 
        self.entry_cliente.pack(side=tk.TOP, padx=10, pady=5)
        self.btn_ocupar.pack(side=tk.TOP, pady=5)
        self.btn_desocupar.pack(side=tk.TOP, pady=5)

        # Añadir pestañas al Notebook
        self.notebook.add(self.frame_habitaciones_disponibles, text="Habitaciones Disponibles y Nuevo Cliente") #añade la pestaña creada al notebook (el notebook es la ventana con las pestañas)

        # Pestaña para Añadir Habitación Nueva
        self.frame_nueva_habitacion = ttk.Frame(self.notebook)

        self.label_nueva_habitacion = ttk.Label(self.frame_nueva_habitacion, text="Añadir Habitación Nueva:")
        self.label_numero_nueva_habitacion = ttk.Label(self.frame_nueva_habitacion, text="Número:")
        self.entry_numero_nueva_habitacion = ttk.Entry(self.frame_nueva_habitacion)
        self.btn_anadir_habitacion = ttk.Button(self.frame_nueva_habitacion, text="Añadir", command=self.anadir_habitacion)

        self.label_nueva_habitacion.pack(side=tk.TOP, anchor=tk.CENTER, pady=5)
        self.label_numero_nueva_habitacion.pack(side=tk.TOP, anchor=tk.CENTER, pady=5)
        self.entry_numero_nueva_habitacion.pack(side=tk.TOP, pady=5)
        self.btn_anadir_habitacion.pack(side=tk.TOP, pady=10)

        # Pestaña para Gestionar Usuarios
        self.frame_gestion_usuarios = ttk.Frame(self.notebook)

        self.btn_cerrar_sesion = ttk.Button(self.frame_gestion_usuarios, text="Cerrar Sesión", command=self.cerrar_sesion)
        self.btn_cerrar_sesion.pack(side=tk.TOP, pady=10)

        # Añadir pestañas al Notebook
        self.notebook.add(self.frame_nueva_habitacion, text="Añadir Habitación")
        self.notebook.add(self.frame_gestion_usuarios, text="Gestionar Usuarios")

        # Posicionar el Notebook en la ventana
        self.notebook.pack(padx=10, pady=10)

        # Cerrar la conexión a la base de datos al cerrar la aplicación
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_app)

    # Métodos de HotelApp
    def cerrar_app(self):
        self.conn.close()
        self.root.destroy()

    def cerrar_sesion(self):
        self.root.destroy()
        root_login = ThemedTk(theme="equilux")
        app_login = LoginApp(root_login)
        root_login.mainloop()

    def actualizar_habitaciones(self):
        self.listbox_habitaciones.delete(0, tk.END)
        self.c.execute("SELECT * FROM habitaciones")
        habitaciones = self.c.fetchall()
        for habitacion in habitaciones:
            self.listbox_habitaciones.insert(tk.END, f"Habitación {habitacion[0]}: {habitacion[1]}")

    def ocupar_habitacion(self):
        selected_index = self.listbox_habitaciones.curselection()
        if selected_index:
            habitacion_numero = int(self.listbox_habitaciones.get(selected_index[0]).split()[1][:-1])
            self.c.execute("SELECT estado FROM habitaciones WHERE numero=?", (habitacion_numero,))
            estado_habitacion = self.c.fetchone()[0]
            if estado_habitacion == 'Disponible':
                cliente_nombre = self.entry_cliente.get()
                if cliente_nombre:
                    self.c.execute("UPDATE habitaciones SET estado='Ocupada' WHERE numero=?", (habitacion_numero,))
                    self.c.execute("INSERT INTO clientes VALUES (?, ?)", (habitacion_numero, cliente_nombre))
                    self.conn.commit()
                    self.actualizar_habitaciones()
                    self.mostrar_mensaje(f"{cliente_nombre} ha ocupado la Habitación {habitacion_numero}")
                else:
                    self.mostrar_mensaje("Ingrese el nombre del cliente.")
            else:
                self.mostrar_mensaje("La habitación ya está ocupada.")
        else:
            self.mostrar_mensaje("Seleccione una habitación.")

    def desocupar_habitacion(self):
        selected_index = self.listbox_habitaciones.curselection()
        if selected_index:
            habitacion_numero = int(self.listbox_habitaciones.get(selected_index[0]).split()[1][:-1])
            self.c.execute("SELECT estado FROM habitaciones WHERE numero=?", (habitacion_numero,))
            estado_habitacion = self.c.fetchone()[0]
            if estado_habitacion == 'Ocupada':
                self.c.execute("UPDATE habitaciones SET estado='Disponible' WHERE numero=?", (habitacion_numero,))
                self.c.execute("DELETE FROM clientes WHERE habitacion_numero=?", (habitacion_numero,))
                self.conn.commit()
                self.actualizar_habitaciones()
                self.mostrar_mensaje(f"Habitación {habitacion_numero} desocupada con éxito.")
            else:
                self.mostrar_mensaje("La habitación no está ocupada.")
        else:
            self.mostrar_mensaje("Seleccione una habitación.")

    def anadir_habitacion(self):
        numero_nueva_habitacion = self.entry_numero_nueva_habitacion.get()
        if numero_nueva_habitacion:
            self.c.execute("INSERT INTO habitaciones (numero, estado) VALUES (?, ?)", (numero_nueva_habitacion, 'Disponible'))
            self.conn.commit()
            self.actualizar_habitaciones()
            self.mostrar_mensaje(f"Habitación {numero_nueva_habitacion} añadida con éxito.")
        else:
            self.mostrar_mensaje("Ingrese el número de la nueva habitación.")

    def mostrar_mensaje(self, mensaje):
        messagebox.showinfo("Mensaje", mensaje)

    def correr_aplicacion(self):
        self.root.mainloop()

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")

        # Estilos
        style = ttk.Style(self.root)
        style.configure('TLabel', font=('Arial', 12), background='#1e1e1e', foreground='#ffffff')
        style.configure('TButton', font=('Arial', 12), background='#4CAF50', foreground='white')

        self.frame = ttk.Frame(self.root, padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Agregar un logo
        self.logo_image = tk.PhotoImage(file="images.png")  # Cambia la ruta de la imagen
        self.label_logo = ttk.Label(self.frame, image=self.logo_image)
        self.label_logo.grid(row=0, column=0, columnspan=2, pady=10)

        self.label_usuario = ttk.Label(self.frame, text="Usuario:")
        self.entry_usuario = ttk.Entry(self.frame, font=("Arial", 12))
        self.label_contrasena = ttk.Label(self.frame, text="Contraseña:")
        self.entry_contrasena = ttk.Entry(self.frame, show="*", font=("Arial", 12))
        self.btn_login = ttk.Button(self.frame, text="Iniciar Sesión", command=self.iniciar_sesion)
        self.btn_crear_usuario = ttk.Button(self.frame, text="Crear Usuario", command=self.abrir_ventana_crear_usuario)

        self.label_usuario.grid(row=1, column=0, pady=5)
        self.entry_usuario.grid(row=1, column=1, pady=5)
        self.label_contrasena.grid(row=2, column=0, pady=5)
        self.entry_contrasena.grid(row=2, column=1, pady=5)
        self.btn_login.grid(row=3, column=0, columnspan=2, pady=5)
        self.btn_crear_usuario.grid(row=4, column=0, columnspan=2, pady=5)

        self.conn = sqlite3.connect('hotel.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS usuarios
                        (usuario TEXT PRIMARY KEY, contrasena TEXT)''')
        self.c.execute("SELECT * FROM usuarios WHERE usuario=? AND contrasena=?", ('root', 'root'))
        if not self.c.fetchone():
            self.c.execute("INSERT INTO usuarios VALUES (?, ?)", ('root', 'root'))
            self.conn.commit()

    def iniciar_sesion(self):
        usuario = self.entry_usuario.get()
        contrasena = self.entry_contrasena.get()
        if usuario and contrasena:
            self.c.execute("SELECT * FROM usuarios WHERE usuario=? AND contrasena=?", (usuario, contrasena))
            if self.c.fetchone():
                self.root.destroy()
                hotel_app = HotelApp(self.conn)
                hotel_app.correr_aplicacion()
            else:
                self.mostrar_mensaje("Usuario o contraseña incorrectos.")
        else:
            self.mostrar_mensaje("Ingrese un usuario y una contraseña.")

    def abrir_ventana_crear_usuario(self):
        ventana_crear_usuario = tk.Toplevel(self.root)
        app_crear_usuario = CrearUsuarioApp(ventana_crear_usuario, self.conn)

    def mostrar_mensaje(self, mensaje):
        messagebox.showinfo("Mensaje", mensaje)

class CrearUsuarioApp:
    def __init__(self, root, conn):
        self.root = root
        self.root.title("Crear Usuario")
        self.frame = ttk.Frame(root, padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Estilos
        style = ttk.Style(self.root)
        style.configure('TLabel', font=('Arial', 12), background='#1e1e1e', foreground='#ffffff')
        style.configure('TButton', font=('Arial', 12), background='#4CAF50', foreground='white')

        self.label_usuario = ttk.Label(self.frame, text="Nuevo Usuario:")
        self.entry_usuario = ttk.Entry(self.frame, font=("Arial", 12))
        self.label_contrasena = ttk.Label(self.frame, text="Contraseña:")
        self.entry_contrasena = ttk.Entry(self.frame, show="*", font=("Arial", 12))
        self.btn_crear = ttk.Button(self.frame, text="Crear Usuario", command=self.crear_usuario)

        self.label_usuario.grid(row=0, column=0, pady=5)
        self.entry_usuario.grid(row=0, column=1, pady=5)
        self.label_contrasena.grid(row=1, column=0, pady=5)
        self.entry_contrasena.grid(row=1, column=1, pady=5)
        self.btn_crear.grid(row=2, column=0, columnspan=2, pady=5)

        self.conn = conn
        self.c = self.conn.cursor()

    def crear_usuario(self):
        usuario = self.entry_usuario.get()
        contrasena = self.entry_contrasena.get()
        if usuario and contrasena:
            self.c.execute("INSERT INTO usuarios VALUES (?, ?)", (usuario, contrasena))
            self.conn.commit()
            self.mostrar_mensaje(f"Usuario {usuario} creado con éxito.")
            self.root.destroy()
        else:
            self.mostrar_mensaje("Ingrese un usuario y una contraseña.")

    def mostrar_mensaje(self, mensaje):
        messagebox.showinfo("Mensaje", mensaje)

if __name__ == "__main__":
    root_login = ThemedTk(theme="equilux")
    app_login = LoginApp(root_login)
    root_login.mainloop()
