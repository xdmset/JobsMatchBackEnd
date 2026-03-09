from enum import Enum


class NombreRol(str, Enum):
    admin = "admin"
    estudiante = "estudiante"
    empresa = "empresa"
