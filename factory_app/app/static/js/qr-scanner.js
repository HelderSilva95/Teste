/**
 * QR Code Scanner - Component reusável para scan de QR codes
 * Usa html5-qrcode library
 */

class QRScanner {
    constructor(options = {}) {
        this.scannerId = options.scannerId || 'qr-reader';
        this.targetInputId = options.targetInputId;
        this.onSuccess = options.onSuccess || this.defaultOnSuccess.bind(this);
        this.onError = options.onError || this.defaultOnError.bind(this);
        this.config = {
            fps: 10,
            qrbox: { width: 250, height: 250 },
            ...options.config
        };
        this.html5QrCode = null;
        this.isScanning = false;
    }

    /**
     * Inicializa o scanner
     */
    async start() {
        if (this.isScanning) {
            console.warn('Scanner já está ativo');
            return;
        }

        try {
            // Criar elemento reader se não existir
            let readerElement = document.getElementById(this.scannerId);
            if (!readerElement) {
                console.error(`Elemento com ID "${this.scannerId}" não encontrado`);
                return;
            }

            this.html5QrCode = new Html5Qrcode(this.scannerId);

            await this.html5QrCode.start(
                { facingMode: "environment" }, // Usa câmera traseira se disponível
                this.config,
                (decodedText, decodedResult) => {
                    this.onSuccess(decodedText, decodedResult);
                },
                (errorMessage) => {
                    // Ignorar erros de scan contínuo
                    if (!errorMessage.includes('NotFoundException')) {
                        this.onError(errorMessage);
                    }
                }
            );

            this.isScanning = true;
            console.log('Scanner QR iniciado com sucesso');

        } catch (err) {
            console.error('Erro ao iniciar scanner:', err);
            alert('Erro ao iniciar câmera. Verifique as permissões.');
        }
    }

    /**
     * Para o scanner
     */
    async stop() {
        if (!this.isScanning || !this.html5QrCode) {
            return;
        }

        try {
            await this.html5QrCode.stop();
            this.isScanning = false;
            console.log('Scanner QR parado');
        } catch (err) {
            console.error('Erro ao parar scanner:', err);
        }
    }

    /**
     * Handler padrão de sucesso
     */
    defaultOnSuccess(decodedText, decodedResult) {
        console.log(`QR Code detectado: ${decodedText}`);

        // Se tem input target, preenche automaticamente
        if (this.targetInputId) {
            const input = document.getElementById(this.targetInputId);
            if (input) {
                input.value = decodedText;
                input.dispatchEvent(new Event('change'));

                // Feedback visual
                input.classList.add('is-valid');
                setTimeout(() => input.classList.remove('is-valid'), 2000);
            }
        }

        // Para scanner após sucesso
        this.stop();

        // Feedback sonoro
        this.playBeep();
    }

    /**
     * Handler padrão de erro
     */
    defaultOnError(errorMessage) {
        console.warn('Erro no scanner:', errorMessage);
    }

    /**
     * Toca um beep de feedback
     */
    playBeep() {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.frequency.value = 800;
        oscillator.type = 'sine';

        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.2);
    }
}

/**
 * Inicializa scanner simples com botão
 */
function initSimpleScanner(buttonId, readerId, inputId) {
    const button = document.getElementById(buttonId);
    const reader = document.getElementById(readerId);
    let scanner = null;

    if (!button || !reader) {
        return;
    }

    button.addEventListener('click', async function() {
        if (!scanner || !scanner.isScanning) {
            // Mostrar reader
            reader.style.display = 'block';

            // Iniciar scanner
            scanner = new QRScanner({
                scannerId: readerId,
                targetInputId: inputId,
                onSuccess: (decodedText) => {
                    // Preencher input
                    const input = document.getElementById(inputId);
                    if (input) {
                        input.value = decodedText;
                        input.classList.add('is-valid');
                        setTimeout(() => input.classList.remove('is-valid'), 2000);
                    }

                    // Esconder reader
                    reader.style.display = 'none';

                    // Parar scanner
                    scanner.stop();

                    // Feedback
                    button.innerHTML = '<i class="bi bi-check-circle"></i> Código Lido!';
                    button.classList.remove('btn-primary');
                    button.classList.add('btn-success');

                    setTimeout(() => {
                        button.innerHTML = '<i class="bi bi-qr-code-scan"></i> Escanear QR';
                        button.classList.remove('btn-success');
                        button.classList.add('btn-primary');
                    }, 2000);
                }
            });

            await scanner.start();

            // Mudar botão
            button.innerHTML = '<i class="bi bi-x-circle"></i> Cancelar';
            button.classList.remove('btn-primary');
            button.classList.add('btn-danger');

        } else {
            // Parar scanner
            await scanner.stop();

            // Esconder reader
            reader.style.display = 'none';

            // Restaurar botão
            button.innerHTML = '<i class="bi bi-qr-code-scan"></i> Escanear QR';
            button.classList.remove('btn-danger');
            button.classList.add('btn-primary');
        }
    });
}

/**
 * Scanner de QR com busca automática
 */
function initQRSearch(buttonId, readerId, searchFunction) {
    const button = document.getElementById(buttonId);
    const reader = document.getElementById(readerId);
    let scanner = null;

    if (!button || !reader) {
        return;
    }

    button.addEventListener('click', async function() {
        if (!scanner || !scanner.isScanning) {
            reader.style.display = 'block';

            scanner = new QRScanner({
                scannerId: readerId,
                onSuccess: async (decodedText) => {
                    reader.style.display = 'none';
                    await scanner.stop();

                    // Executar função de busca
                    if (searchFunction && typeof searchFunction === 'function') {
                        await searchFunction(decodedText);
                    } else {
                        // Busca padrão - redirecionar
                        window.location.href = `/inventory/search/qr?qr=${encodeURIComponent(decodedText)}`;
                    }
                }
            });

            await scanner.start();
            button.innerHTML = '<i class="bi bi-x-circle"></i> Cancelar';
            button.classList.remove('btn-primary');
            button.classList.add('btn-danger');

        } else {
            await scanner.stop();
            reader.style.display = 'none';
            button.innerHTML = '<i class="bi bi-qr-code-scan"></i> Escanear';
            button.classList.remove('btn-danger');
            button.classList.add('btn-primary');
        }
    });
}
