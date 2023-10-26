from .constants import *

SEXO = (
    ('M', 'Masculino'),
    ('F', 'Femenino'),
    ('X', 'Otro'),
)

TIPO = (
    (DNI, 'D.N.I.'),
    (PASAPORTE, 'Pasaporte'),
    (LIBRETACIVICA, 'libreta civica'),
    (LIBRETAENROLAMIENTO, 'libreta enrolamiento'),
)

SITUACION =(('Activo', 'ACTIVO'),
            ('Jubilado', 'JUBILADO'),
            )

OPCIONES = (
    (ARCHIVO, 'Archivo'),
    (TEXTO, 'Texto'),
    (NUMERO, 'Número')
)

ESTADOS = (
    (ACTIVA, 'activa'),
    (INACTIVA, 'inactiva'),
    (TRAMITE, 'tramite'),
    (EJECUTADA, 'ejecutada'),
)