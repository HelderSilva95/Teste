/**
 * Production Timer - Timer em tempo real para produções
 */

class ProductionTimer {
    constructor(elementId, startTime) {
        this.element = document.getElementById(elementId);
        this.startTime = new Date(startTime);
        this.pauseTime = 0; // Tempo acumulado de pausas em segundos
        this.isPaused = false;
        this.pauseStartTime = null;
        this.interval = null;

        if (this.element) {
            this.start();
        }
    }

    start() {
        this.updateDisplay();
        this.interval = setInterval(() => this.updateDisplay(), 1000);
    }

    stop() {
        if (this.interval) {
            clearInterval(this.interval);
        }
    }

    pause() {
        this.isPaused = true;
        this.pauseStartTime = new Date();
    }

    resume() {
        if (this.isPaused && this.pauseStartTime) {
            const pauseDuration = Math.floor((new Date() - this.pauseStartTime) / 1000);
            this.pauseTime += pauseDuration;
            this.isPaused = false;
            this.pauseStartTime = null;
        }
    }

    updateDisplay() {
        const now = new Date();
        let elapsedSeconds = Math.floor((now - this.startTime) / 1000);

        // Subtrair tempo de pausas
        elapsedSeconds -= this.pauseTime;

        // Se está pausado, adicionar tempo da pausa atual
        if (this.isPaused && this.pauseStartTime) {
            const currentPauseDuration = Math.floor((now - this.pauseStartTime) / 1000);
            elapsedSeconds -= currentPauseDuration;
        }

        const hours = Math.floor(elapsedSeconds / 3600);
        const minutes = Math.floor((elapsedSeconds % 3600) / 60);
        const seconds = elapsedSeconds % 60;

        const timeString = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

        this.element.textContent = timeString;

        // Adicionar classe visual se está pausado
        if (this.isPaused) {
            this.element.classList.add('paused');
        } else {
            this.element.classList.remove('paused');
        }
    }

    getElapsedTime() {
        const now = new Date();
        let elapsedSeconds = Math.floor((now - this.startTime) / 1000);
        elapsedSeconds -= this.pauseTime;

        if (this.isPaused && this.pauseStartTime) {
            const currentPauseDuration = Math.floor((now - this.pauseStartTime) / 1000);
            elapsedSeconds -= currentPauseDuration;
        }

        return {
            hours: Math.floor(elapsedSeconds / 3600),
            minutes: Math.floor((elapsedSeconds % 3600) / 60),
            seconds: elapsedSeconds % 60,
            totalSeconds: elapsedSeconds
        };
    }
}

/**
 * Inicializar timers para todos os elementos com classe 'production-timer'
 */
function initializeProductionTimers() {
    document.querySelectorAll('.production-timer').forEach(element => {
        const startTime = element.dataset.startTime;
        const pauseTime = parseInt(element.dataset.pauseTime || '0');
        const isPaused = element.dataset.status === 'paused';

        if (startTime) {
            const timer = new ProductionTimer(element.id, startTime);

            // Adicionar tempo de pausa acumulado
            if (pauseTime > 0) {
                timer.pauseTime = pauseTime * 60; // Converter minutos para segundos
            }

            // Se está pausado, pausar o timer
            if (isPaused) {
                timer.pause();
            }

            // Guardar instância no elemento para acesso posterior
            element.timerInstance = timer;
        }
    });
}

/**
 * Timer compacto para dashboard
 */
function formatElapsedTime(startTime, pauseMinutes = 0) {
    const start = new Date(startTime);
    const now = new Date();
    let elapsedSeconds = Math.floor((now - start) / 1000);
    elapsedSeconds -= (pauseMinutes * 60);

    const hours = Math.floor(elapsedSeconds / 3600);
    const minutes = Math.floor((elapsedSeconds % 3600) / 60);

    if (hours > 0) {
        return `${hours}h ${minutes}m`;
    } else {
        return `${minutes}m`;
    }
}

// Auto-inicializar quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeProductionTimers);
} else {
    initializeProductionTimers();
}
