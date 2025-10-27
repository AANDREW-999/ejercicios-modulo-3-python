import pytest

from src.bloque1.ejercicio_2_generador_perfiles import crear_perfil


def test_perfil_completo() -> None:
    resultado = crear_perfil("Ana", 28,
                             "leer", "programar", twitter="@ana", github="ana28")
    esperado = (
        "Perfil de Usuario\n"
        "Nombre: Ana\n"
        "Edad: 28\n"
        "Hobbies: leer, programar\n"
        "Redes sociales: github=ana28, twitter=@ana"
    )
    assert resultado == esperado


def test_perfil_sin_hobbies_ni_redes() -> None:
    resultado = crear_perfil("Andres", 19)
    esperado = (
        "Perfil de Usuario\n"
        "Nombre: Andres\n"
        "Edad: 19\n"
        "Hobbies: Ninguno\n"
        "Redes sociales: Ninguna"
    )
    assert resultado == esperado


def test_perfil_solo_hobbies() -> None:
    resultado = crear_perfil("Lucía", 22, "ajedrez", "running")
    esperado = (
        "Perfil de Usuario\n"
        "Nombre: Lucía\n"
        "Edad: 22\n"
        "Hobbies: ajedrez, running\n"
        "Redes sociales: Ninguna"
    )
    assert resultado == esperado


def test_perfil_solo_redes() -> None:
    # Orden de kwargs no está garantizado, por eso se ordenan por clave en la función
    resultado = crear_perfil("Miguel", 30, instagram="@mike", twitter="@miguel30")
    esperado = (
        "Perfil de Usuario\n"
        "Nombre: Miguel\n"
        "Edad: 30\n"
        "Hobbies: Ninguno\n"
        "Redes sociales: instagram=@mike, twitter=@miguel30"
    )
    assert resultado == esperado


@pytest.mark.parametrize("nombre_invalido", ["", "   ", "\n\t"])
def test_nombre_invalido_levanta_error(nombre_invalido: str) -> None:
    with pytest.raises(ValueError):
        crear_perfil(nombre_invalido, 25)


def test_edad_negativa_levanta_error() -> None:
    with pytest.raises(ValueError):
        crear_perfil("Sofía", -1)


@pytest.mark.parametrize("edad", [0, 120])
def test_edad_limite_valida(edad: int) -> None:
    resultado = crear_perfil("Luis", edad)
    esperado = (
        "Perfil de Usuario\n"
        "Nombre: Luis\n"
        f"Edad: {edad}\n"
        "Hobbies: Ninguno\n"
        "Redes sociales: Ninguna"
    )
    assert resultado == esperado


def test_edad_fuera_de_rango_superior() -> None:
    with pytest.raises(ValueError):
        crear_perfil("Laura", 121)


@pytest.mark.parametrize("nombre", ["Álvaro", "O'Connor", "María-José"])
def test_nombre_acentos_y_apostrofo(nombre: str) -> None:
    resultado = crear_perfil(nombre, 25)
    assert f"Nombre: {nombre}" in resultado


def test_nombre_recorta_espacios() -> None:
    resultado = crear_perfil("  Ana   María  ", 20)
    esperado = (
        "Perfil de Usuario\n"
        "Nombre: Ana María\n"
        "Edad: 20\n"
        "Hobbies: Ninguno\n"
        "Redes sociales: Ninguna"
    )
    assert resultado == esperado


def test_nombre_muy_largo_levanta_error() -> None:
    nombre = "a" * 61
    with pytest.raises(ValueError):
        crear_perfil(nombre, 30)


def test_hobbies_deduplicados_y_filtrados() -> None:
    resultado = crear_perfil("Diego", 26, "leer", " Leer ", "LEER", "música!", "jugar")
    esperado = (
        "Perfil de Usuario\n"
        "Nombre: Diego\n"
        "Edad: 26\n"
        "Hobbies: leer, jugar\n"
        "Redes sociales: Ninguna"
    )
    assert resultado == esperado


def test_hobbies_todos_invalidos_resulta_en_ninguno() -> None:
    resultado = crear_perfil("Eva", 31, "!" * 3, "x" * 31)
    esperado = (
        "Perfil de Usuario\n"
        "Nombre: Eva\n"
        "Edad: 31\n"
        "Hobbies: Ninguno\n"
        "Redes sociales: Ninguna"
    )
    assert resultado == esperado


def test_redes_agrega_arroba_y_ordenadas() -> None:
    # instagram/twitter sin '@' deben normalizarse
    resultado = crear_perfil("Nora", 29, instagram="nora", twitter="norita")
    esperado = (
        "Perfil de Usuario\n"
        "Nombre: Nora\n"
        "Edad: 29\n"
        "Hobbies: Ninguno\n"
        "Redes sociales: instagram=@nora, twitter=@norita"
    )
    assert resultado == esperado


def test_redes_descarta_invalida_y_valor_largo() -> None:
    valor_largo = "a" * 51
    resultado = crear_perfil(
        "Pablo",
        34,
        github="pablo34",
        **{"1canal": "tv", "twitter": "pablo", "otro": valor_largo},
    )
    esperado = (
        "Perfil de Usuario\n"
        "Nombre: Pablo\n"
        "Edad: 34\n"
        "Hobbies: Ninguno\n"
        "Redes sociales: github=pablo34, twitter=@pablo"
    )
    assert resultado == esperado


def test_edad_como_cadena_es_valida() -> None:
    resultado = crear_perfil("Rosa", int("25"))
    esperado = (
        "Perfil de Usuario\n"
        "Nombre: Rosa\n"
        "Edad: 25\n"
        "Hobbies: Ninguno\n"
        "Redes sociales: Ninguna"
    )
    assert resultado == esperado


def test_hobby_no_string_se_descarta() -> None:
    resultado = crear_perfil("Leo", 40, "leer", 123)  # 123 se descarta
    esperado = (
        "Perfil de Usuario\n"
        "Nombre: Leo\n"
        "Edad: 40\n"
        "Hobbies: leer\n"
        "Redes sociales: Ninguna"
    )
    assert resultado == esperado

