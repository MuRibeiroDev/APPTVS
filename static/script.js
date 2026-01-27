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

// Abrir menu de ligar todas
function openGlobalLigarMenu(event) {
    event.stopPropagation();
    const menu = document.getElementById('globalLigarMenu');
    if (!menu) return;

    // Se o menu já está aberto, fecha
    if (menu.classList.contains('show')) {
        closeGlobalLigarMenu();
        return;
    }

    // Posicionamento
    const buttonRect = event.currentTarget.getBoundingClientRect();
    let left = Math.max(buttonRect.right + 10, 305);
    let top = buttonRect.top;

    menu.style.display = 'block';

    requestAnimationFrame(() => {
        menu.style.left = `${left}px`;
        menu.style.top = `${top}px`;
        menu.classList.add('show');
    });
}

function closeGlobalLigarMenu() {
    const menu = document.getElementById('globalLigarMenu');
    if (menu) {
        menu.classList.remove('show');
        setTimeout(() => {
            if (!menu.classList.contains('show')) {
                menu.style.display = 'none';
            }
        }, 200);
    }
}

// Ligar todas COM BI (envia webhook)
async function ligarTodasComBi() {
    closeGlobalLigarMenu();

    document.querySelectorAll('.power-icon').forEach(icon => {
        icon.classList.remove('on', 'off');
        icon.classList.add('loading');
    });

    try {
        const response = await fetch(`/api/executar/todas`, { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            setTimeout(() => checkAllStatus(), 12000);
        }
    } catch (error) {
        console.error('Erro:', error);
        checkAllStatus();
    }
}

// Ligar todas SEM BI (não envia webhook)
async function ligarTodasSemBi() {
    closeGlobalLigarMenu();

    document.querySelectorAll('.power-icon').forEach(icon => {
        icon.classList.remove('on', 'off');
        icon.classList.add('loading');
    });

    try {
        const response = await fetch(`/api/religar/todas`, { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            setTimeout(() => checkAllStatus(), 12000);
        }
    } catch (error) {
        console.error('Erro:', error);
        checkAllStatus();
    }
}

// Desligar todas as TVs exceto as de reunião
async function desligarTVsExcetoReunioes() {
    // Confirmar ação
    if (!confirm('Desligar todas as TVs exceto as de reunião?\n\nSerão desligadas 2 por vez com intervalo de 10 segundos.')) {
        return;
    }

    // Marcar apenas TVs que não são de reunião como loading
    document.querySelectorAll('.tv-card').forEach(card => {
        const setorSpan = card.querySelector('.tv-setor');
        const setor = setorSpan.getAttribute('data-original-setor') || setorSpan.textContent;

        if (!setor.toLowerCase().includes('reunião') && !setor.toLowerCase().includes('reuniao')) {
            const powerIcon = card.querySelector('.power-icon');
            if (powerIcon) {
                powerIcon.classList.remove('on', 'off');
                powerIcon.classList.add('loading');
            }
        }
    });

    try {
        const response = await fetch(`/api/desligar/exceto-reuniao`, { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            // Aguarda tempo suficiente para o desligamento em lote completar
            setTimeout(() => checkAllStatus(), 15000);
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
window.onclick = function (event) {
    const modal = document.getElementById('logModal');
    if (event.target == modal) {
        fecharLogModal();
    }
}

let activeTvForMenu = null;

function openTvMenu(event, tvName) {
    // Fecha menu de power se estiver aberto
    closePowerMenu();

    const menu = document.getElementById('globalContextMenu');
    const btnReconnect = document.getElementById('btnReconnectGlobal');

    if (!menu || !btnReconnect) return;

    // Se clicar no mesmo botão e o menu estiver aberto, fecha
    if (activeTvForMenu === tvName && menu.classList.contains('show')) {
        closeContextMenu();
        return;
    }

    activeTvForMenu = tvName;

    // Configura a ação dos botões
    btnReconnect.onclick = () => reconnectTv(tvName);

    // Configura botão de wallpaper
    const btnWallpaper = document.getElementById('btnWallpaperGlobal');
    if (btnWallpaper) {
        btnWallpaper.onclick = () => abrirWallpaperModal(tvName);
    }

    // Configura botão de listar BIs
    const btnListarBis = document.getElementById('btnListarBisGlobal');
    if (btnListarBis) {
        btnListarBis.onclick = () => abrirBisModal(tvName, false);
    }

    // Configura botão de editar BIs
    const btnEditarBis = document.getElementById('btnEditarBisGlobal');
    if (btnEditarBis) {
        btnEditarBis.onclick = () => abrirBisModal(tvName, true);
    }

    // Configura botão de abrir BI
    const btnAbrirBi = document.getElementById('btnAbrirBiGlobal');
    if (btnAbrirBi) {
        btnAbrirBi.onclick = () => abrirBiNaTv(tvName);
    }

    // Configura botão de fechar BI
    const btnFecharBi = document.getElementById('btnFecharBiGlobal');
    if (btnFecharBi) {
        btnFecharBi.onclick = () => fecharBiNaTv(tvName);
    }

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

// --- Menu de Power Individual ---
let activePowerTv = null;

function openPowerMenu(event, tvName) {
    // Fecha outros menus
    closeContextMenu();
    closeGlobalLigarMenu();
    closePowerMenu();

    activePowerTv = tvName;

    const menu = document.getElementById('powerMenu');
    if (!menu) return;

    // Configura botões
    const btnLigarSemBi = document.getElementById('btnLigarSemBi');
    const btnLigarComBi = document.getElementById('btnLigarComBi');

    if (btnLigarSemBi) {
        btnLigarSemBi.onclick = () => {
            closePowerMenu();
            togglePower(tvName);
        };
    }

    if (btnLigarComBi) {
        btnLigarComBi.onclick = () => {
            closePowerMenu();
            ligarComBi(tvName);
        };
    }

    // Posicionamento
    const buttonRect = event.currentTarget.getBoundingClientRect();
    let left = Math.max(buttonRect.right + 10, 305);
    let top = buttonRect.top;

    menu.style.display = 'block';

    requestAnimationFrame(() => {
        menu.style.left = `${left}px`;
        menu.style.top = `${top}px`;
        menu.classList.add('show');
    });
}

function closePowerMenu() {
    const menu = document.getElementById('powerMenu');
    if (menu) {
        menu.classList.remove('show');
        activePowerTv = null;
        setTimeout(() => {
            if (!menu.classList.contains('show')) {
                menu.style.display = 'none';
            }
        }, 200);
    }
}

// Close menus when clicking outside
document.addEventListener('click', (e) => {
    const contextMenu = document.getElementById('globalContextMenu');
    const ligarMenu = document.getElementById('globalLigarMenu');
    const powerMenu = document.getElementById('powerMenu');

    // Se o clique não foi no menu nem no ícone que abriu
    if (contextMenu && !e.target.closest('.tv-context-menu') && !e.target.closest('.menu-icon')) {
        closeContextMenu();
    }

    // Fecha menu de ligar todas
    if (ligarMenu && !e.target.closest('#globalLigarMenu') && !e.target.closest('#global-power-on')) {
        closeGlobalLigarMenu();
    }

    // Fecha menu de power individual
    if (powerMenu && !e.target.closest('#powerMenu') && !e.target.closest('.power-icon')) {
        closePowerMenu();
    }
});

// Scroll fecha o menu para evitar que ele fique flutuando fora de posição
document.addEventListener('scroll', () => {
    closeContextMenu();
    closePowerMenu();
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

// Abrir BI na TV
async function abrirBiNaTv(tvName) {
    closeContextMenu();

    try {
        const response = await fetch(`/api/bis/${tvName}/abrir`, { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            console.log(`BI aberto em ${tvName}`);
        } else {
            alert(`Erro ao abrir BI: ${data.error || data.message}`);
        }
    } catch (error) {
        console.error('Erro ao abrir BI:', error);
        alert('Erro ao abrir BI. Verifique a conexão.');
    }
}

// Fechar BI na TV
async function fecharBiNaTv(tvName) {
    closeContextMenu();

    try {
        const response = await fetch(`/api/bis/${tvName}/fechar`, { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            console.log(`BI fechado em ${tvName}`);
        } else {
            alert(`Erro ao fechar BI: ${data.error || data.message}`);
        }
    } catch (error) {
        console.error('Erro ao fechar BI:', error);
        alert('Erro ao fechar BI. Verifique a conexão.');
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

// --- Wallpaper Modal Logic ---

let currentWallpaperTvName = null;
let currentWallpaperBase64 = null;

function abrirWallpaperModal(tvName) {
    closeContextMenu();
    currentWallpaperTvName = tvName;
    currentWallpaperBase64 = null;

    const modal = document.getElementById('wallpaperModal');
    const modalTitle = document.getElementById('wallpaperModalTitle');
    const preview = document.getElementById('wallpaperPreview');
    const btnSend = document.getElementById('btnSendWallpaper');
    const fileInput = document.getElementById('wallpaperInput');

    if (modal && modalTitle) {
        modalTitle.textContent = `Alterar Wallpaper - ${tvName}`;

        // Reset preview
        preview.innerHTML = `
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <circle cx="8.5" cy="8.5" r="1.5"></circle>
                <polyline points="21 15 16 10 5 21"></polyline>
            </svg>
            <p>Selecione uma imagem</p>
        `;

        // Reset button and input
        btnSend.disabled = true;
        fileInput.value = '';

        modal.style.display = 'flex';
    }
}

function fecharWallpaperModal() {
    const modal = document.getElementById('wallpaperModal');
    if (modal) {
        modal.style.display = 'none';
    }
    currentWallpaperTvName = null;
    currentWallpaperBase64 = null;
}

function previewWallpaper(event) {
    const file = event.target.files[0];
    if (!file) return;

    const preview = document.getElementById('wallpaperPreview');
    const btnSend = document.getElementById('btnSendWallpaper');

    const reader = new FileReader();
    reader.onload = function (e) {
        // Extrai apenas o base64 (remove o prefixo data:image/xxx;base64,)
        const fullBase64 = e.target.result;
        currentWallpaperBase64 = fullBase64.split(',')[1];

        // Mostra preview
        preview.innerHTML = `<img src="${fullBase64}" alt="Preview do wallpaper">`;
        preview.classList.add('has-image');

        // Habilita botão de enviar
        btnSend.disabled = false;
    };
    reader.readAsDataURL(file);
}

async function enviarWallpaper() {
    if (!currentWallpaperTvName || !currentWallpaperBase64) {
        alert('Selecione uma imagem primeiro.');
        return;
    }

    const btnSend = document.getElementById('btnSendWallpaper');
    const originalText = btnSend.innerHTML;

    btnSend.disabled = true;
    btnSend.innerHTML = `
        <svg class="spinning" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/>
        </svg>
        Enviando...
    `;

    try {
        const response = await fetch(`/api/wallpaper/${currentWallpaperTvName}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ base64: currentWallpaperBase64 })
        });

        const data = await response.json();

        if (data.success) {
            btnSend.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                Enviado!
            `;
            setTimeout(() => {
                fecharWallpaperModal();
                btnSend.innerHTML = originalText;
                btnSend.disabled = false;
            }, 1500);
        } else {
            alert(`Erro: ${data.message}`);
            btnSend.innerHTML = originalText;
            btnSend.disabled = false;
        }
    } catch (error) {
        console.error('Erro ao enviar wallpaper:', error);
        alert('Erro ao enviar wallpaper. Verifique a conexão.');
        btnSend.innerHTML = originalText;
        btnSend.disabled = false;
    }
}

// Close wallpaper modal when clicking outside
window.addEventListener('click', function (event) {
    const wallpaperModal = document.getElementById('wallpaperModal');
    if (event.target === wallpaperModal) {
        fecharWallpaperModal();
    }

    const bisModal = document.getElementById('bisModal');
    if (event.target === bisModal) {
        fecharBisModal();
    }
});

// --- BIs Modal Logic ---

let currentBisTvName = null;
let currentBisEditMode = false;

async function abrirBisModal(tvName, editMode = false) {
    closeContextMenu();
    currentBisTvName = tvName;
    currentBisEditMode = editMode;

    const modal = document.getElementById('bisModal');
    const modalTitle = document.getElementById('bisModalTitle');
    const loading = document.getElementById('bisLoading');
    const content = document.getElementById('bisContent');
    const bisList = document.getElementById('bisList');
    const editSection = document.getElementById('bisEditSection');

    if (!modal || !modalTitle) return;

    modalTitle.textContent = editMode ? `Editar BIs - ${tvName}` : `BIs Atuais - ${tvName}`;

    // Reset
    loading.style.display = 'flex';
    content.style.display = 'none';
    bisList.innerHTML = '';
    editSection.style.display = editMode ? 'block' : 'none';

    modal.style.display = 'flex';

    // Carrega os BIs
    await carregarBis(tvName, editMode);
}

function fecharBisModal() {
    const modal = document.getElementById('bisModal');
    if (modal) {
        modal.style.display = 'none';
    }
    currentBisTvName = null;
    currentBisEditMode = false;
}

async function carregarBis(tvName, editMode) {
    const loading = document.getElementById('bisLoading');
    const content = document.getElementById('bisContent');
    const bisList = document.getElementById('bisList');
    const url1Input = document.getElementById('bisUrl1');
    const url2Input = document.getElementById('bisUrl2');

    try {
        const response = await fetch(`/api/bis/${tvName}`);
        const data = await response.json();

        loading.style.display = 'none';
        content.style.display = 'block';

        if (data.success && data.bis) {
            let urls = [];

            // A API retorna {currentcontent: ['url1', 'url2']} ou string ou array
            if (data.bis.currentcontent && Array.isArray(data.bis.currentcontent)) {
                // Formato: {currentcontent: ['url1', 'url2']}
                urls = data.bis.currentcontent;
            } else if (typeof data.bis === 'string') {
                try {
                    const parsed = JSON.parse(data.bis);
                    urls = parsed.currentcontent || parsed;
                } catch {
                    urls = [data.bis];
                }
            } else if (Array.isArray(data.bis)) {
                urls = data.bis;
            }

            // Mostra a lista de BIs
            if (urls.length === 0) {
                bisList.innerHTML = '<div class="no-bis">Nenhum BI configurado</div>';
            } else {
                bisList.innerHTML = urls.map((url, i) => `
                    <div class="bi-item">
                        <span class="bi-number">${i + 1}</span>
                        <a href="${url}" target="_blank" class="bi-url">${url || '(vazio)'}</a>
                    </div>
                `).join('');
            }

            // Preenche inputs se em modo edição
            if (editMode) {
                const container = document.getElementById('bisUrlsContainer');
                container.innerHTML = '';

                if (urls.length === 0) {
                    // Adiciona um campo vazio inicial
                    adicionarCampoUrl();
                } else {
                    // Adiciona campos para cada URL existente
                    urls.forEach((url, i) => {
                        criarCampoUrl(url, i + 1);
                    });
                }
            }
        } else {
            bisList.innerHTML = `<div class="bis-error">Erro: ${data.error || 'Não foi possível carregar'}</div>`;
        }
    } catch (error) {
        console.error('Erro ao carregar BIs:', error);
        loading.style.display = 'none';
        content.style.display = 'block';
        bisList.innerHTML = '<div class="bis-error">Erro ao carregar. Verifique a conexão.</div>';
    }
}

let bisUrlCounter = 0;

function criarCampoUrl(valor = '', numero = null) {
    const container = document.getElementById('bisUrlsContainer');
    bisUrlCounter++;
    const id = `bisUrl_${bisUrlCounter}`;
    const num = numero || container.children.length + 1;

    const div = document.createElement('div');
    div.className = 'bis-url-item';
    div.id = `${id}_container`;
    div.innerHTML = `
        <span class="bis-url-number">${num}</span>
        <input type="text" id="${id}" value="${valor}" placeholder="https://..." class="bis-input">
        <button class="btn-remove-url" onclick="removerCampoUrl('${id}_container')" title="Remover">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
        </button>
    `;
    container.appendChild(div);

    // Foca no novo input
    document.getElementById(id).focus();

    renumerarCampos();
}

function adicionarCampoUrl() {
    criarCampoUrl('');
}

function removerCampoUrl(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.remove();
        renumerarCampos();
    }
}

function removerTodasUrls() {
    const container = document.getElementById('bisUrlsContainer');
    container.innerHTML = '';
    // Adiciona um campo vazio
    adicionarCampoUrl();
}

function renumerarCampos() {
    const container = document.getElementById('bisUrlsContainer');
    const items = container.querySelectorAll('.bis-url-item');
    items.forEach((item, i) => {
        const numberSpan = item.querySelector('.bis-url-number');
        if (numberSpan) {
            numberSpan.textContent = i + 1;
        }
    });
}

async function salvarBis() {
    if (!currentBisTvName) return;

    // Coleta todas as URLs dos campos dinâmicos
    const container = document.getElementById('bisUrlsContainer');
    const inputs = container.querySelectorAll('.bis-input');
    const urls = [];

    inputs.forEach(input => {
        const valor = input.value.trim();
        if (valor) {
            urls.push(valor);
        }
    });

    const btnSave = document.getElementById('btnSaveBis');
    const originalText = btnSave.innerHTML;

    btnSave.disabled = true;
    btnSave.innerHTML = `
        <svg class="spinning" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/>
        </svg>
        Salvando...
    `;

    try {
        const response = await fetch(`/api/bis/${currentBisTvName}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ urls: urls })
        });

        const data = await response.json();

        if (data.success) {
            btnSave.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                Salvo!
            `;
            setTimeout(() => {
                fecharBisModal();
                btnSave.innerHTML = originalText;
                btnSave.disabled = false;
            }, 1500);
        } else {
            alert(`Erro: ${data.message}`);
            btnSave.innerHTML = originalText;
            btnSave.disabled = false;
        }
    } catch (error) {
        console.error('Erro ao salvar BIs:', error);
        alert('Erro ao salvar. Verifique a conexão.');
        btnSave.innerHTML = originalText;
        btnSave.disabled = false;
    }
}
