"""
Rotas Web - Páginas HTML
"""

from flask import Blueprint, render_template


def create_web_routes(tv_service):
    """Cria e retorna o blueprint com as rotas web"""
    
    web = Blueprint('web', __name__)
    
    @web.route('/')
    def index():
        """Página principal"""
        tvs = tv_service.obter_tvs()
        tvs_por_setor = tv_service.obter_tvs_por_setor()
        return render_template('index.html', tvs=tvs, tvs_por_setor=tvs_por_setor)
    
    return web
