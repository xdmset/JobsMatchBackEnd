from enum import Enum


class NombreRol(str, Enum):
    Admin = "Admin"
    Estudiante = "Estudiante"
    Empresa = "Empresa"
