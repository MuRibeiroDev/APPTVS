"""
Mapeador de Sequências
Responsável por mapear TVs às suas sequências de inicialização
"""

from utils import log
from sequences import (
    sequencia_ti,
    sequencia_atlas,
    sequencia_juridico,
    sequencia_operacao1_tv1,
    sequencia_operacao2_tv2,
    sequencia_tv1_painel_tv3,
    sequencia_reuniao,
    sequencia_financeiro,
    sequencia_tv4,
    sequencia_tv5,
    sequencia_tv6,
    sequencia_gestao_industria,
    sequencia_antifraude,
    sequencia_controladoria,
    sequencia_cobranca,
    sequencia_cadastro,
    sequencia_cozinha,
    sequencia_recepcao
)


class SequenceMapper:
    """Mapeia TVs para suas sequências de inicialização"""
    
    def executar_sequencia(self, tv, tv_id, tv_nome):
        """Executa a sequência correta para uma TV"""
        
        # TI
        if tv_nome in ["TI01", "TI02", "TI03"]:
            sequencia_ti(tv, tv_id, tv_nome)
        
        # Operação
        elif tv_nome == "Operação 1 - TV1":
            sequencia_operacao1_tv1(tv, tv_id)
        elif tv_nome == "Operação 2 - TV2":
            sequencia_operacao2_tv2(tv, tv_id)
        elif tv_nome == "TV 1 Painel - TV3":
            sequencia_tv1_painel_tv3(tv, tv_id)
        elif tv_nome == "TV 2 Painel - TV4":
            sequencia_tv4(tv, tv_id)
        elif tv_nome == "TV 3 Painel - TV5":
            sequencia_tv5(tv, tv_id)
        elif tv_nome == "TV 4 Painel - TV6":
            sequencia_tv6(tv, tv_id)
        
        # Setores específicos
        elif tv_nome in ["FINANCEIRO", "Financeiro"]:
            sequencia_financeiro(tv, tv_id)
        elif tv_nome == "TV-JURIDICO":
            sequencia_juridico(tv, tv_id)
        elif tv_nome in ["GESTÃO-INDUSTRIA", "Gestão Industria"]:
            sequencia_gestao_industria(tv, tv_id)
        elif tv_nome in ["ANTIFRAUDE", "Antifraude"]:
            sequencia_antifraude(tv, tv_id)
        elif tv_nome in ["CONTROLADORIA", "Controladoria"]:
            sequencia_controladoria(tv, tv_id)
        elif tv_nome in ["COBRANÇA", "Cobrança"]:
            sequencia_cobranca(tv, tv_id)
        elif tv_nome in ["TVCADASTRO", "TvCadastro"]:
            sequencia_cadastro(tv, tv_id)
        elif tv_nome == "TV-ATLAS":
            sequencia_atlas(tv, tv_id)
        elif tv_nome == "Cozinha Entrada":
            sequencia_cozinha(tv, tv_id)
        elif tv_nome == "Recepção":
            sequencia_recepcao(tv, tv_id)
        
        # Reunião (apenas liga)
        elif tv_nome in ["TV-DIA D", "TV-MOSSAD", "TV-GEO-FOREST"] or "REUNIÃO" in tv_nome.upper() or "REUNIAO" in tv_nome.upper():
            sequencia_reuniao(tv, tv_id, tv_nome)
        
        else:
            log(f"[{tv_nome}] Nenhuma sequência definida para esta TV", "WARNING")
