// Atualiza status de todas as TVs
async function checkAllStatus() {
    try {
        const response = await fetch('/api/status/todas');
        const data = await response.json();
        
        if (data.success) {
            updateStatusIndicators(data.status);
        }
    } catch (error) {
        console.error('Erro ao verificar status:', error);
    }
}

// Atualiza indicadores de status na sidebar
function updateStatusIndicators(statusData) {
    for (const [tvName, info] of Object.entries(statusData)) {
        const card = document.getElementById(`card-${tvName}`);
        const powerIcon = document.getElementById(`power-${tvName}`);
        const sectorSpan = card ? card.querySelector('.tv-setor') : null;

        if (card && powerIcon && sectorSpan) {
            // Reset classes
            powerIcon.classList.remove('on', 'off', 'loading');
            card.classList.remove('offline-mode');
            
            const originalSector = sectorSpan.getAttribute('data-original-setor') || sectorSpan.textContent;

            if (info.is_online) {
                sectorSpan.textContent = originalSector;
                if (info.is_on) {
                    powerIcon.classList.add('on');
                } else {
                    powerIcon.classList.add('off');
                }
            } else {
                sectorSpan.textContent = `${originalSector} - Offline`;
                powerIcon.classList.add('off');
                card.classList.add('offline-mode');
            }
        }
    }
}

// Toggle power de uma TV específica (SEMPRE sem webhook)
async function togglePower(tvName) {
    const powerIcon = document.getElementById(`power-${tvName}`);
    let wasOn = false;

    if (powerIcon) {
        wasOn = powerIcon.classList.contains('on');
        powerIcon.classList.remove('on', 'off');
        powerIcon.classList.add('loading');
    }
    
    try {
        // Liga SEM webhook (BI já deve estar ligado)
        const response = await fetch(`/api/ligar-sem-bi/${tvName}`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            // Atualização Otimista: muda a cor imediatamente
            if (powerIcon) {
                powerIcon.classList.remove('loading');
                if (wasOn) {
                    powerIcon.classList.add('off'); // Estava ligado, desligou
                } else {
                    powerIcon.classList.add('on'); // Estava desligado, ligou
                }
            }
            
            // Verifica o status real depois de um tempo para garantir
            setTimeout(() => checkAllStatus(), 5000);
        }
    } catch (error) {
        console.error('Erro:', error);
        checkAllStatus();
    }
}

// Toggle todas as TVs (COM webhook - primeira vez)
async function toggleAllTVs() {
    document.querySelectorAll('.power-icon').forEach(icon => {
        icon.classList.remove('on', 'off');
        icon.classList.add('loading');
    });
    
    try {
        const response = await fetch(`/api/executar/todas`, { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            // Aguarda mais tempo pois são múltiplas requisições
            setTimeout(() => checkAllStatus(), 12000);
        }
    } catch (error) {
        console.error('Erro:', error);
        checkAllStatus();
    }
}

// Religar todas as TVs (SEM webhook - BIs já ligados)
async function religarAllTVs() {
    document.querySelectorAll('.power-icon').forEach(icon => {
        icon.classList.remove('on', 'off');
        icon.classList.add('loading');
    });
    
    try {
        const response = await fetch(`/api/religar/todas`, { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            // Aguarda mais tempo pois são múltiplas requisições
            setTimeout(() => checkAllStatus(), 12000);
        }
    } catch (error) {
        console.error('Erro:', error);
        checkAllStatus();
    }
}

// Verifica status do token
async function verificarStatusToken() {
    try {
        const response = await fetch('/api/token/status');
        const data = await response.json();
        
        if (data.success && data.status) {
            const status = data.status;
            
            // Se houve erro na última tentativa de renovação
            if (status.sucesso === false && status.erro) {
                mostrarPopupErroToken(status.erro);
            }
        }
    } catch (error) {
        console.error('Erro ao verificar status do token:', error);
    }
}

// Mostra popup de erro de token
function mostrarPopupErroToken(mensagemErro) {
    const popup = document.getElementById('tokenErrorPopup');
    const messageElement = document.getElementById('tokenErrorMessage');
    
    messageElement.textContent = mensagemErro || 'Falha na renovação automática';
    popup.style.display = 'block';
}

// Fecha popup de erro
function fecharPopupErro() {
    const popup = document.getElementById('tokenErrorPopup');
    popup.style.display = 'none';
}

// Tenta renovar o token manualmente
async function retryTokenRenewal() {
    const btn = document.querySelector('.btn-retry-token');
    const originalText = btn.innerHTML;
    
    btn.disabled = true;
    btn.innerHTML = 'Tentando...';
    
    try {
        const response = await fetch('/api/token/renovar', { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            btn.innerHTML = 'Iniciado!';
            setTimeout(() => {
                fecharPopupErro();
                btn.disabled = false;
                btn.innerHTML = originalText;
            }, 2000);
        } else {
            btn.innerHTML = 'Erro ao iniciar';
            setTimeout(() => {
                btn.disabled = false;
                btn.innerHTML = originalText;
            }, 2000);
        }
    } catch (error) {
        console.error('Erro:', error);
        btn.innerHTML = 'Erro de conexão';
        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = originalText;
        }, 2000);
    }
}

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    // Carrega status inicial
    checkAllStatus();
    
    // Atualiza a cada 30 segundos
    setInterval(checkAllStatus, 30000);
    
    // Verifica status do token a cada 5 segundos (Feedback instantâneo)
    setInterval(verificarStatusToken, 5000);
    verificarStatusToken();
});

// --- Log Modal Logic ---

let currentLogTvName = null;
let logUpdateInterval = null;

function openLogModal(tvName) {
    currentLogTvName = tvName;
    const modal = document.getElementById('logModal');
    const modalTitle = document.getElementById('logModalTitle');
    
    if (modal && modalTitle) {
        modalTitle.textContent = `Logs - ${tvName}`;
        modal.style.display = 'flex';
        
        atualizarLogsModal();
        // Update logs every 5 seconds while modal is open
        if (logUpdateInterval) clearInterval(logUpdateInterval);
        logUpdateInterval = setInterval(atualizarLogsModal, 5000);
    }
}

function fecharLogModal() {
    const modal = document.getElementById('logModal');
    if (modal) {
        modal.style.display = 'none';
    }
    if (logUpdateInterval) {
        clearInterval(logUpdateInterval);
        logUpdateInterval = null;
    }
    currentLogTvName = null;
}

async function atualizarLogsModal() {
    if (!currentLogTvName) return;
    
    const logContainer = document.getElementById('logContainer');
    if (!logContainer) return;
    
    try {
        const response = await fetch('/api/logs');
        const data = await response.json();
        
        if (data.logs) {
            // Filter logs for this TV (case insensitive)
            const filteredLogs = data.logs.filter(log => 
                log.mensagem.toLowerCase().includes(currentLogTvName.toLowerCase()) ||
                log.mensagem.toLowerCase().includes('todas') // Include global logs
            );
            
            // Sort by timestamp descending (newest first) - assuming logs are already appended in order, so reverse
            const sortedLogs = filteredLogs.reverse();
            
            if (sortedLogs.length === 0) {
                logContainer.innerHTML = '<div class="log-loading">Nenhum log encontrado para esta TV.</div>';
                return;
            }
            
            logContainer.innerHTML = sortedLogs.map(log => {
                let typeClass = 'info';
                if (log.tipo === 'ERROR') typeClass = 'error';
                if (log.tipo === 'SUCCESS') typeClass = 'success';
                if (log.tipo === 'WARNING') typeClass = 'warning';
                
                return `
                    <div class="log-entry ${typeClass}">
                        <span class="log-timestamp">[${log.timestamp}]</span>
                        <span class="log-message">${log.mensagem}</span>
                    </div>
                `;
            }).join('');
        }
    } catch (error) {
        console.error('Erro ao buscar logs:', error);
        logContainer.innerHTML = '<div class="log-entry error">Erro ao carregar logs.</div>';
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('logModal');
    if (event.target == modal) {
        fecharLogModal();
    }
}

let activeTvForMenu = null;

function openTvMenu(event, tvName) {
    const menu = document.getElementById('globalContextMenu');
    const btnReconnect = document.getElementById('btnReconnectGlobal');
    const btnLigarComBi = document.getElementById('btnLigarComBiGlobal');
    
    if (!menu || !btnReconnect || !btnLigarComBi) return;

    // Se clicar no mesmo botão e o menu estiver aberto, fecha
    if (activeTvForMenu === tvName && menu.classList.contains('show')) {
        closeContextMenu();
        return;
    }

    activeTvForMenu = tvName;
    
    // Configura a ação dos botões
    btnReconnect.onclick = () => reconnectTv(tvName);
    btnLigarComBi.onclick = () => ligarComBi(tvName);
    
    // Posicionamento
    const buttonRect = event.currentTarget.getBoundingClientRect();
    
    // Posiciona à direita do botão, garantindo que fique fora da sidebar (que tem ~300px)
    // Se o botão estiver muito à esquerda, usa a posição do botão + 10
    // Se estiver na sidebar, força para fora (305px)
    let left = Math.max(buttonRect.right + 10, 305);
    let top = buttonRect.top;
    
    // Ajuste se sair da tela (embora o usuário queira à direita, vamos garantir que não quebre o layout)
    // Mas como é fixed, ele vai ficar por cima de tudo.
    
    menu.style.display = 'block'; // Garante que está renderizado para transição
    
    // Pequeno delay para permitir que o display:block seja processado antes da classe show (para animação)
    requestAnimationFrame(() => {
        menu.style.left = `${left}px`;
        menu.style.top = `${top}px`;
        menu.classList.add('show');
    });
}

function closeContextMenu() {
    const menu = document.getElementById('globalContextMenu');
    if (menu) {
        menu.classList.remove('show');
        activeTvForMenu = null;
        // Aguarda animação para esconder
        setTimeout(() => {
            if (!menu.classList.contains('show')) {
                menu.style.display = 'none';
            }
        }, 200);
    }
}

// Close menus when clicking outside
document.addEventListener('click', (e) => {
    const menu = document.getElementById('globalContextMenu');
    // Se o clique não foi no menu nem no ícone que abriu (tratado no stopPropagation do HTML, mas bom garantir)
    if (menu && !e.target.closest('.tv-context-menu') && !e.target.closest('.menu-icon')) {
        closeContextMenu();
    }
});

// Scroll fecha o menu para evitar que ele fique flutuando fora de posição
document.addEventListener('scroll', () => {
    closeContextMenu();
}, true); // Capture phase para pegar scroll de qualquer elemento

async function reconnectTv(tvName) {
    const menu = document.getElementById('globalContextMenu');
    const icon = menu ? menu.querySelector('.refresh-icon') : null;
    
    // Add spinning animation
    if (icon) icon.classList.add('spinning');
    
    try {
        // Call reconnect endpoint
        const response = await fetch(`/api/reconnect/${tvName}`, { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            // Keep spinning for a bit to show activity, since the action is async
            setTimeout(() => {
                // Optional: Refresh status after sequence might be done (approx 12s)
                setTimeout(() => checkAllStatus(), 12000);
            }, 1000);
        } else {
            console.error('Erro ao reconectar:', data.message);
        }
    } catch (error) {
        console.error('Erro de conexão:', error);
    } finally {
        // Remove animation and close menu
        setTimeout(() => {
             if (icon) icon.classList.remove('spinning');
             closeContextMenu();
        }, 1000);
    }
}

// Ligar TV COM BI (envia webhook)
async function ligarComBi(tvName) {
    closeContextMenu();
    
    const powerIcon = document.getElementById(`power-${tvName}`);
    
    if (powerIcon) {
        powerIcon.classList.remove('on', 'off');
        powerIcon.classList.add('loading');
    }
    
    try {
        const response = await fetch(`/api/ligar-com-bi/${tvName}`, { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            setTimeout(() => checkAllStatus(), 8000);
        }
    } catch (error) {
        console.error('Erro:', error);
        if (powerIcon) {
            powerIcon.classList.remove('loading');
            powerIcon.classList.add('off');
        }
    }
}
