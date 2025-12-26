// Função para executar sequência de uma TV específica
async function executarSequencia(tvNome) {
    const statusElement = document.getElementById(`status-${tvNome}`);
    const button = event.target.closest('button');
    
    // Desabilita o botão e mostra loading
    button.disabled = true;
    statusElement.className = 'status loading';
    statusElement.innerHTML = '<span class="loading-spinner"></span>Executando sequência...';
    
    try {
        const response = await fetch(`/api/executar/${tvNome}`);
        const data = await response.json();
        
        if (data.success) {
            statusElement.className = 'status success';
            statusElement.textContent = '✅ ' + data.message;
            
            // Simula o tempo de execução (aproximadamente 30-60 segundos)
            setTimeout(() => {
                statusElement.className = 'status success';
                statusElement.textContent = '✅ Sequência concluída!';
                button.disabled = false;
            }, 45000);
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        statusElement.className = 'status error';
        statusElement.textContent = '❌ Erro: ' + error.message;
        button.disabled = false;
    }
}

// Função para executar todas as TVs simultaneamente
async function executarTodasSequencias() {
    const statusElement = document.getElementById('status-todas');
    const button = event.target.closest('button');
    const allButtons = document.querySelectorAll('.btn');
    
    // Desabilita todos os botões
    allButtons.forEach(btn => btn.disabled = true);
    
    // Mostra loading
    statusElement.className = 'status loading';
    statusElement.innerHTML = '<span class="loading-spinner"></span>Executando todas as sequências simultaneamente...';
    
    try {
        const response = await fetch('/api/executar/todas');
        const data = await response.json();
        
        if (data.success) {
            statusElement.className = 'status success';
            statusElement.textContent = '✅ ' + data.message;
            
            // Atualiza status de todas as TVs
            const tvs = ['TI01', 'TI02', 'TI03', 'TV-ATLAS', 'TV-JURIDICO'];
            tvs.forEach(tv => {
                const tvStatus = document.getElementById(`status-${tv}`);
                tvStatus.className = 'status loading';
                tvStatus.innerHTML = '<span class="loading-spinner"></span>Em execução...';
            });
            
            // Simula o tempo de execução (aproximadamente 45-60 segundos)
            setTimeout(() => {
                statusElement.className = 'status success';
                statusElement.textContent = '✅ Todas as sequências concluídas!';
                
                // Atualiza status individual
                tvs.forEach(tv => {
                    const tvStatus = document.getElementById(`status-${tv}`);
                    tvStatus.className = 'status success';
                    tvStatus.textContent = '✅ Concluída!';
                });
                
                // Reabilita todos os botões
                allButtons.forEach(btn => btn.disabled = false);
            }, 50000);
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        statusElement.className = 'status error';
        statusElement.textContent = '❌ Erro: ' + error.message;
        allButtons.forEach(btn => btn.disabled = false);
    }
}

// Função para formatar o nome do app/conteúdo
function formatarConteudo(appName, inputSource) {
    if (!appName || appName === '') {
        return 'Nenhum conteúdo';
    }
    
    // Mapear apps conhecidos
    const appMap = {
        'com.samsung.tv.coba.pconscreen': 'Menu/Configurações',
        'org.tizen.browser': 'Navegador Web',
        'netflix': 'Netflix',
        'youtube': 'YouTube',
        '111299001912': 'YouTube',
        '3201512006785': 'Netflix',
        'com.samsung.tv.gallery': 'Galeria',
        'dtv': 'TV'
    };
    
    return appMap[appName] || appName.split('.').pop() || 'Desconhecido';
}

// Função para alternar ligar/desligar TV
async function togglePower(tvNome) {
    const statusElement = document.getElementById(`status-${tvNome}`);
    const button = document.getElementById(`power-${tvNome}`);
    
    // Desabilita o botão e mostra loading
    button.disabled = true;
    statusElement.className = 'status loading';
    statusElement.innerHTML = '<span class="loading-spinner"></span>Processando...';
    
    try {
        const response = await fetch(`/api/executar/${tvNome}`, { method: 'POST' });
        const data = await response.json();
        
        if (data.success || data.sucesso) {
            statusElement.className = 'status success';
            statusElement.textContent = '✓ Comando enviado';
            
            // Aguarda 2 segundos e atualiza status
            setTimeout(() => {
                atualizarStatusTVs();
                statusElement.textContent = '';
                statusElement.className = 'status';
            }, 2000);
        } else {
            throw new Error(data.message || data.mensagem || 'Erro desconhecido');
        }
    } catch (error) {
        statusElement.className = 'status error';
        statusElement.textContent = '✗ Erro: ' + error.message;
        setTimeout(() => {
            statusElement.textContent = '';
            statusElement.className = 'status';
        }, 3000);
    } finally {
        button.disabled = false;
    }
}

// Função para atualizar o status das TVs
async function atualizarStatusTVs() {
    try {
        const response = await fetch('/api/status/todas');
        const data = await response.json();
        
        if (data.success) {
            for (const [tvNome, status] of Object.entries(data.status)) {
                const badge = document.getElementById(`badge-${tvNome}`);
                const glow = document.getElementById(`glow-${tvNome}`);
                const wifi = document.getElementById(`wifi-${tvNome}`);
                const powerBtn = document.getElementById(`power-${tvNome}`);
                
                // Atualiza status LIGADA/DESLIGADA
                if (badge && glow) {
                    if (status.is_on) {
                        badge.textContent = 'LIGADA';
                        badge.className = 'status-badge on';
                        glow.className = 'screen-glow on';
                    } else {
                        badge.textContent = 'DESLIGADA';
                        badge.className = 'status-badge off';
                        glow.className = 'screen-glow off';
                    }
                }

                // Atualiza botão power
                if (powerBtn) {
                    if (status.is_on) {
                        powerBtn.className = 'power-btn on';
                    } else {
                        powerBtn.className = 'power-btn';
                    }
                }

                // Atualiza status de REDE (Online/Offline)
                if (wifi) {
                    if (status.is_online) {
                        wifi.className = 'wifi-icon online';
                        wifi.title = 'Conectada à rede';
                    } else {
                        wifi.className = 'wifi-icon offline';
                        wifi.title = 'Sem conexão de rede';
                    }
                }
            }
        }
    } catch (error) {
        console.error('Erro ao atualizar status:', error);
    }
}

// Atualiza status a cada 30 segundos
setInterval(atualizarStatusTVs, 30000);

// Limpa mensagens de status antigas ao carregar a página
window.addEventListener('DOMContentLoaded', () => {
    console.log('Sistema de Controle de TVs Samsung carregado');
    console.log('Versão: 1.2.0');
    atualizarStatusTVs();
});
