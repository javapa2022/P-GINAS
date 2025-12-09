// ==================== GAME STATE ====================
let cards = [];
let flippedCards = [];
let matchedPairs = 0;
let moves = 0;
let timer = 0;
let timerInterval = null;
let gameStarted = false;
let bestTime = localStorage.getItem('bestTime') || null;

// Card symbols
const symbols = ['🎮', '🎨', '🎭', '🎪', '🎯', '🎲', '🎸', '🎹', '🎺', '🎻', '🎬', '🎤', '🏀', '⚽', '🎾', '🏐', '🎳', '🏆'];

// ==================== DOM ELEMENTS ====================
const gameBoard = document.getElementById('gameBoard');
const startBtn = document.getElementById('startBtn');
const resetBtn = document.getElementById('resetBtn');
const difficultySelect = document.getElementById('difficulty');
const timerDisplay = document.getElementById('timer');
const movesDisplay = document.getElementById('moves');
const pairsDisplay = document.getElementById('pairs');
const bestTimeDisplay = document.getElementById('bestTime');
const winModal = document.getElementById('winModal');
const playAgainBtn = document.getElementById('playAgainBtn');
const finalTimeDisplay = document.getElementById('finalTime');
const finalMovesDisplay = document.getElementById('finalMoves');

// ==================== INITIALIZE GAME ====================
function initGame() {
    const difficulty = difficultySelect.value;
    let pairCount;

    switch (difficulty) {
        case 'easy':
            pairCount = 8;
            gameBoard.className = 'game-board';
            break;
        case 'medium':
            pairCount = 12;
            gameBoard.className = 'game-board medium';
            break;
        case 'hard':
            pairCount = 18;
            gameBoard.className = 'game-board hard';
            break;
    }

    // Reset game state
    cards = [];
    flippedCards = [];
    matchedPairs = 0;
    moves = 0;
    timer = 0;
    gameStarted = false;

    // Create card pairs
    const selectedSymbols = symbols.slice(0, pairCount);
    const cardSymbols = [...selectedSymbols, ...selectedSymbols];

    // Shuffle cards
    cardSymbols.sort(() => Math.random() - 0.5);

    // Create card elements
    gameBoard.innerHTML = '';
    cardSymbols.forEach((symbol, index) => {
        const card = createCard(symbol, index);
        gameBoard.appendChild(card);
        cards.push(card);
    });

    // Update displays
    updateDisplay();

    // Stop timer if running
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }

    // Show best time
    if (bestTime) {
        bestTimeDisplay.textContent = formatTime(bestTime);
    }
}

function createCard(symbol, index) {
    const card = document.createElement('div');
    card.className = 'card';
    card.dataset.symbol = symbol;
    card.dataset.index = index;

    card.innerHTML = `
        <div class="card-face card-front">${symbol}</div>
        <div class="card-face card-back"></div>
    `;

    card.addEventListener('click', () => flipCard(card));

    return card;
}

// ==================== GAME LOGIC ====================
function flipCard(card) {
    // Don't flip if game hasn't started
    if (!gameStarted) {
        startGame();
    }

    // Don't flip if card is already flipped or matched
    if (card.classList.contains('flipped') || card.classList.contains('matched')) {
        return;
    }

    // Don't flip if two cards are already flipped
    if (flippedCards.length >= 2) {
        return;
    }

    // Flip the card
    card.classList.add('flipped');
    flippedCards.push(card);

    // Check for match if two cards are flipped
    if (flippedCards.length === 2) {
        moves++;
        updateDisplay();
        checkMatch();
    }
}

function checkMatch() {
    const [card1, card2] = flippedCards;

    if (card1.dataset.symbol === card2.dataset.symbol) {
        // Match found
        setTimeout(() => {
            card1.classList.add('matched');
            card2.classList.add('matched');
            matchedPairs++;
            updateDisplay();
            flippedCards = [];

            // Check if game is won
            const totalPairs = cards.length / 2;
            if (matchedPairs === totalPairs) {
                winGame();
            }
        }, 500);
    } else {
        // No match
        setTimeout(() => {
            card1.classList.remove('flipped');
            card2.classList.remove('flipped');
            flippedCards = [];
        }, 1000);
    }
}

// ==================== GAME CONTROLS ====================
function startGame() {
    if (gameStarted) return;

    gameStarted = true;
    timerInterval = setInterval(() => {
        timer++;
        updateDisplay();
    }, 1000);
}

function resetGame() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }

    initGame();
}

function winGame() {
    clearInterval(timerInterval);

    // Update best time
    if (!bestTime || timer < bestTime) {
        bestTime = timer;
        localStorage.setItem('bestTime', bestTime);
        bestTimeDisplay.textContent = formatTime(bestTime);
    }

    // Show win modal
    finalTimeDisplay.textContent = formatTime(timer);
    finalMovesDisplay.textContent = moves;

    setTimeout(() => {
        winModal.classList.add('active');

        // Confetti effect
        createConfetti();
    }, 500);
}

// ==================== DISPLAY UPDATES ====================
function updateDisplay() {
    timerDisplay.textContent = formatTime(timer);
    movesDisplay.textContent = moves;
    const totalPairs = cards.length / 2;
    pairsDisplay.textContent = `${matchedPairs}/${totalPairs}`;
}

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// ==================== CONFETTI EFFECT ====================
function createConfetti() {
    const colors = ['#6366f1', '#ec4899', '#14b8a6', '#f59e0b', '#8b5cf6'];
    const confettiCount = 50;

    for (let i = 0; i < confettiCount; i++) {
        const confetti = document.createElement('div');
        confetti.style.cssText = `
            position: fixed;
            width: 10px;
            height: 10px;
            background: ${colors[Math.floor(Math.random() * colors.length)]};
            left: ${Math.random() * 100}vw;
            top: -10px;
            opacity: 1;
            transform: rotate(${Math.random() * 360}deg);
            animation: confettiFall ${2 + Math.random() * 2}s linear forwards;
            z-index: 10001;
            border-radius: 2px;
        `;

        document.body.appendChild(confetti);

        setTimeout(() => {
            confetti.remove();
        }, 4000);
    }
}

// Add confetti animation
const style = document.createElement('style');
style.textContent = `
    @keyframes confettiFall {
        to {
            top: 100vh;
            opacity: 0;
            transform: translateX(${Math.random() * 200 - 100}px) rotate(${Math.random() * 720}deg);
        }
    }
`;
document.head.appendChild(style);

// ==================== EVENT LISTENERS ====================
startBtn.addEventListener('click', () => {
    if (!gameStarted) {
        startGame();
    }
});

resetBtn.addEventListener('click', resetGame);

playAgainBtn.addEventListener('click', () => {
    winModal.classList.remove('active');
    resetGame();
});

difficultySelect.addEventListener('change', resetGame);

// Close modal on click outside
winModal.addEventListener('click', (e) => {
    if (e.target === winModal) {
        winModal.classList.remove('active');
    }
});

// ==================== KEYBOARD SUPPORT ====================
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && winModal.classList.contains('active')) {
        winModal.classList.remove('active');
    }
});

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', () => {
    initGame();

    // Add entrance animation
    const statBoxes = document.querySelectorAll('.stat-box');
    statBoxes.forEach((box, index) => {
        box.style.opacity = '0';
        box.style.transform = 'translateY(20px)';
        setTimeout(() => {
            box.style.transition = 'all 0.5s ease';
            box.style.opacity = '1';
            box.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Animate cards entrance
    setTimeout(() => {
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'scale(0.8)';
            setTimeout(() => {
                card.style.transition = 'all 0.5s ease';
                card.style.opacity = '1';
                card.style.transform = 'scale(1)';
            }, index * 50);
        });
    }, 500);
});

// ==================== CONSOLE MESSAGE ====================
console.log('%c🎮 Juego de Memoria', 'color: #6366f1; font-size: 20px; font-weight: bold;');
console.log('%cCaracterísticas:', 'color: #ec4899; font-size: 14px; font-weight: bold;');
console.log('✓ Tres niveles de dificultad');
console.log('✓ Sistema de puntuación y tiempo');
console.log('✓ Almacenamiento de mejor tiempo');
console.log('✓ Animaciones fluidas y efectos visuales');
console.log('✓ Efecto de confetti al ganar');
console.log('✓ Diseño responsive');
console.log('%c¡Diviértete jugando!', 'color: #14b8a6; font-size: 12px;');
