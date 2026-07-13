# ==========================================================
# SERVIÇOS ADICIONAIS
# ==========================================================

from math import ceil


def calcular_whisky(convidados, drinks_por_pessoa, produtos, regras):
    """
    Calcula um Bar Receptivo de Whisky.

    produtos = lista dos produtos vinculados ao serviço
    regras = dicionário das regras do pacote

    Retorna uma lista de bebidas calculadas.
    """

    percentual = float(regras.get("percentual_consumidores", 30))

    dose_ml = float(regras.get("dose_ml", 50))

    pessoas = convidados * percentual / 100

    doses = pessoas * drinks_por_pessoa

    ml_total = doses * dose_ml

    garrafas_total = ceil(ml_total / 1000)

    quantidade_marcas = max(len(produtos), 1)

    garrafas_por_marca = ceil(garrafas_total / quantidade_marcas)

    retorno = []

    for produto in produtos:

        retorno.append({

            "estoque_id": produto["id"],

            "marca": produto["marca"],

            "garrafas": garrafas_por_marca

        })

    return retorno

# ==========================================================
# MOTOR DOS SERVIÇOS
# ==========================================================

SERVICOS = {

    "whisky": calcular_whisky,

}
