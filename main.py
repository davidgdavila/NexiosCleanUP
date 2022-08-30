import datetime
from timecode import Timecode
from kivy.config import Config
Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '400')
import json
import os
import subprocess
import threading
import time
from tkinter import filedialog as fd
import tkinter as tk
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty
from kivymd.app import MDApp
from kivy.factory import Factory
from kivy.uix.popup import Popup
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.config import Config
from kivymd.uix.screen import MDScreen



class LayoutPrincipal(MDScreen):
    cuenta = 1
    texto = []
    ruta_abrir_archivo=[]
    ruta_salvar_arhivo=""
    etiqueta=StringProperty("Paso 1. Carga o arrastra la MediaBase del Nexio-1.")
    ruta_inicio = os.path.expanduser("~") + "\\documents\\"
    operador=""
    activar = BooleanProperty(False)
    i=1


    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        Window.bind(on_drop_file=self.on_drop_file)

    def on_drop_file(self, Window, file_path, *args):

        self.ruta_abrir_archivo.append(file_path.decode(encoding="utf-8"))
        if self.i==2:
            self.seleccionar_salvar_archivo()
        else:
            self.i += 1
            self.ids.eti1.text = "Paso 1. Completado! \nPaso 2. Carga o arrastra la MediaBase del Nexio-2."

    def seleccionar_archivo(self):
        if self.cuenta == 3:
            self.ids.eti1.text = "Ya has elegido dos archivos"
        else:
            root = tk.Tk()
            root.withdraw()
            self.ruta_abrir_archivo.append(fd.askopenfilename(
                    title='Abrir archivo',
                    initialdir=self.ruta_inicio,
                    filetypes=(('text files', '*.txt'),('All files', '*.*'))))
            root.destroy()
            if self.ruta_abrir_archivo[0]:
                if self.i==2:
                    self.seleccionar_salvar_archivo()
                else:
                    self.i += 1
                    self.ids.eti1.text = "Paso 1. Completado! \nPaso 2. Carga o arrastra la MediaBase del Nexio-2."
            else:
                pass
        self.cuenta +=1

    def cargar_archivo(self,path):
        #self.texto = "START SMPTE" + "\t" + "DUR SMPTE" + "\t" + "Content" + "\t" + "Title" + "\t" + "ID" + "\n"

        fecha_actual = datetime.date.today()
        hace15dias = (fecha_actual - datetime.timedelta(days=15)).strftime('%m/%d/%Y')
        hace15dias = datetime.datetime.strptime(hace15dias, '%m/%d/%Y')
        try:
            with open(path,encoding='utf-16-le') as file:
                for lineas in file:
                    termino = lineas.split("\t", )
                    if termino[31] == "START SMPTE":
                        pass
                    else:
                        fechadelclip = datetime.datetime.strptime(termino[34], '%m/%d/%Y')
                        if fechadelclip < hace15dias:
                            if termino[2][:5].isnumeric() or "TX2" in termino[2]:
                                timecode=Timecode("29.97", termino[32])
                                if timecode >= Timecode("29.97","00:15:00:02"):
                                    if termino[2] in self.texto:
                                        pass
                                        #self.texto += termino[2]+ "\t" + termino[34] + "\t" + termino[32] + "\n"
                                    else:
                                        self.texto.append(termino[2])
                            else:
                                pass

        except IndexError:
            self.ids.eti1.text="El formato no es correcto. Vuelve a intentarlo."
        except UnicodeDecodeError:
            self.ids.eti1.text="Error: El archivo que intentas cargar no es un txt"
        except Exception as e:
            self.ids.eti1.text = repr(e) +"Ocurrio un error desconocido. Contacta al programador"

    def seleccionar_salvar_archivo(self):
        root = tk.Tk()
        root.withdraw()
        nombre_archivo=os.path.basename(self.ruta_abrir_archivo[1]) #nombre del archivo
        rutabase = os.path.dirname(self.ruta_abrir_archivo[1]) #ruta del archivo
        self.ruta_salvar_arhivo = fd.asksaveasfilename(
            initialfile = "PurgeList_" + str(datetime.date.today()) + ".txt",
            title = 'Salvar archivo',
            initialdir = rutabase,
            filetypes = (('text files', '*.txt'),('All files', '*.*')))
        #root.destroy()
        if self.ruta_salvar_arhivo:
            for i in range(2):
                self.cargar_archivo(self.ruta_abrir_archivo[i])
            self.guardar_archivo()
        else:
            pass

    def guardar_archivo(self):
        if ".txt" in self.ruta_salvar_arhivo:
            self.ruta_salvar_arhivo.replace(".txt","")
        else:
            self.ruta_salvar_arhivo += ".txt"
        clip=""
        for elemento in self.texto:
            clip += (elemento + "\n")
        with open(self.ruta_salvar_arhivo, 'w',encoding='ANSI') as stream:
            stream.write(clip)
        self.etiqueta = "¡Se ha convertido el archivo!\n"+self.ruta_salvar_arhivo

    def show_acerca_de(self):
        contenido = Acerca_de()
        self._popup = Popup(
            title='Acerca de Dub List Converter',
            content=contenido,
            size_hint=(None, None), size=(400, 400))
        self._popup.open()


class Acerca_de(MDBoxLayout):
    texto_etiqueta = StringProperty("Autor: David Israel González Dávila.\n\n"
                                "Versión: 1.0.1\n\n"
                                "Fecha: 03/julio/2022\n\n"
                                "Descripción: Generar el formato adecuado para\n"
                                "poder depurar los Nexios en el ADC client\n\n")
class NexiosCleanUPApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Config.set("kivy","window_icon","icono.ico")
        self.title = "Nexio's CleanUp"
        self.icon = "icono.ico"

    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.root= Builder.load_file("Nexios_Clean_UP.kv")

Factory.register('Acerca_de', cls=Acerca_de)

NexiosCleanUPApp().run()

