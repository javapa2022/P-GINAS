// ==================== CALCULATOR STATE ====================
let currentValue = '0';
let previousValue = '';
let operation = null;
let shouldResetDisplay = false;
let history = [];

// ==================== DOM ELEMENTS ====================
const display = document.getElementById('display');
const historyDisplay = document.getElementById('history');
const historyList = document.getElementById('historyList');
const clearHistoryBtn = document.getElementById('clearHistory');

// ==================== NUMBER BUTTONS ====================
const numberButtons = document.querySelectorAll('[data-number]');
numberButtons.forEach(button => {
    button.addEventListener('click', () => {
        appendNumber(button.dataset.number);
        animateButton(button);
    });
});

function appendNumber(number) {
    if (shouldResetDisplay) {
        currentValue = '';
        shouldResetDisplay = false;
    }

    if (number === '.' && currentValue.includes('.')) return;

    if (currentValue === '0' && number !== '.') {
        currentValue = number;
    } else {
        currentValue += number;
    }

    updateDisplay();
}

// ==================== OPERATOR BUTTONS ====================
const operatorButtons = document.querySelectorAll('[data-operator]');
operatorButtons.forEach(button => {
    button.addEventListener('click', () => {
        handleOperator(button.dataset.operator);
        animateButton(button);
    });
});

function handleOperator(op) {
    if (operation !== null && !shouldResetDisplay) {
        calculate();
    }

    operation = op;
    previousValue = currentValue;
    shouldResetDisplay = true;

    updateHistory(`${currentValue} ${getOperatorSymbol(op)}`);
}

function getOperatorSymbol(op) {
    const symbols = {
        '+': '+',
        '-': '−',
        '*': '×',
        '/': '÷'
    };
    return symbols[op] || op;
}

// ==================== CALCULATE ====================
function calculate() {
    if (operation === null || previousValue === '') return;

    const prev = parseFloat(previousValue);
    const current = parseFloat(currentValue);

    if (isNaN(prev) || isNaN(current)) return;

    let result;

    switch (operation) {
        case '+':
            result = prev + current;
            break;
        case '-':
            result = prev - current;
            break;
        case '*':
            result = prev * current;
            break;
        case '/':
            if (current === 0) {
                showError('No se puede dividir por cero');
                return;
            }
            result = prev / current;
            break;
        default:
            return;
    }

    const expression = `${previousValue} ${getOperatorSymbol(operation)} ${currentValue}`;
    addToHistory(expression, result);

    currentValue = roundResult(result).toString();
    operation = null;
    previousValue = '';
    shouldResetDisplay = true;

    updateDisplay();
    updateHistory('');
}

function roundResult(num) {
    return Math.round((num + Number.EPSILON) * 100000000) / 100000000;
}

// ==================== ACTION BUTTONS ====================
const actionButtons = document.querySelectorAll('[data-action]');
actionButtons.forEach(button => {
    button.addEventListener('click', () => {
        handleAction(button.dataset.action);
        animateButton(button);
    });
});

function handleAction(action) {
    switch (action) {
        case 'clear':
            clear();
            break;
        case 'delete':
            deleteLastDigit();
            break;
        case 'percent':
            percent();
            break;
        case 'equals':
            calculate();
            break;
    }
}

function clear() {
    currentValue = '0';
    previousValue = '';
    operation = null;
    shouldResetDisplay = false;
    updateDisplay();
    updateHistory('');
}

function deleteLastDigit() {
    if (currentValue.length === 1) {
        currentValue = '0';
    } else {
        currentValue = currentValue.slice(0, -1);
    }
    updateDisplay();
}

function percent() {
    currentValue = (parseFloat(currentValue) / 100).toString();
    updateDisplay();
}

// ==================== SCIENTIFIC FUNCTIONS ====================
const scientificButtons = document.querySelectorAll('[data-scientific]');
scientificButtons.forEach(button => {
    button.addEventListener('click', () => {
        handleScientific(button.dataset.scientific);
        animateButton(button);
    });
});

function handleScientific(func) {
    const value = parseFloat(currentValue);

    if (isNaN(value) && func !== 'pi' && func !== 'e') {
        showError('Valor inválido');
        return;
    }

    let result;
    let expression;

    switch (func) {
        case 'sin':
            result = Math.sin(value * Math.PI / 180);
            expression = `sin(${value}°)`;
            break;
        case 'cos':
            result = Math.cos(value * Math.PI / 180);
            expression = `cos(${value}°)`;
            break;
        case 'tan':
            result = Math.tan(value * Math.PI / 180);
            expression = `tan(${value}°)`;
            break;
        case 'log':
            if (value <= 0) {
                showError('Logaritmo de número no positivo');
                return;
            }
            result = Math.log10(value);
            expression = `log(${value})`;
            break;
        case 'sqrt':
            if (value < 0) {
                showError('Raíz cuadrada de número negativo');
                return;
            }
            result = Math.sqrt(value);
            expression = `√${value}`;
            break;
        case 'square':
            result = value * value;
            expression = `${value}²`;
            break;
        case 'cube':
            result = value * value * value;
            expression = `${value}³`;
            break;
        case 'power':
            previousValue = currentValue;
            operation = '**';
            shouldResetDisplay = true;
            updateHistory(`${currentValue}^`);
            return;
        case 'pi':
            result = Math.PI;
            expression = 'π';
            break;
        case 'e':
            result = Math.E;
            expression = 'e';
            break;
        case 'factorial':
            if (value < 0 || !Number.isInteger(value)) {
                showError('Factorial solo para enteros positivos');
                return;
            }
            result = factorial(value);
            expression = `${value}!`;
            break;
        case 'inverse':
            if (value === 0) {
                showError('No se puede dividir por cero');
                return;
            }
            result = 1 / value;
            expression = `1/${value}`;
            break;
        default:
            return;
    }

    if (expression) {
        addToHistory(expression, result);
    }

    currentValue = roundResult(result).toString();
    shouldResetDisplay = true;
    updateDisplay();
}

function factorial(n) {
    if (n === 0 || n === 1) return 1;
    let result = 1;
    for (let i = 2; i <= n; i++) {
        result *= i;
    }
    return result;
}

// ==================== DISPLAY UPDATE ====================
function updateDisplay() {
    display.textContent = currentValue;
    display.classList.remove('error');
}

function updateHistory(text) {
    historyDisplay.textContent = text;
}

function showError(message) {
    display.textContent = message;
    display.classList.add('error');

    setTimeout(() => {
        currentValue = '0';
        updateDisplay();
    }, 2000);
}

// ==================== HISTORY MANAGEMENT ====================
function addToHistory(expression, result) {
    const historyItem = {
        expression,
        result: roundResult(result),
        timestamp: new Date().toLocaleTimeString()
    };

    history.unshift(historyItem);

    if (history.length > 20) {
        history = history.slice(0, 20);
    }

    renderHistory();
}

function renderHistory() {
    if (history.length === 0) {
        historyList.innerHTML = `
            <div class="history-empty">
                <span class="empty-icon">📊</span>
                <p>No hay cálculos en el historial</p>
            </div>
        `;
        return;
    }

    historyList.innerHTML = history.map(item => `
        <div class="history-item">
            <div class="history-expression">${item.expression}</div>
            <div class="history-result">= ${item.result}</div>
        </div>
    `).join('');
}

clearHistoryBtn.addEventListener('click', () => {
    history = [];
    renderHistory();
    animateButton(clearHistoryBtn);
});

// ==================== KEYBOARD SUPPORT ====================
document.addEventListener('keydown', (e) => {
    e.preventDefault();

    if (e.key >= '0' && e.key <= '9' || e.key === '.') {
        appendNumber(e.key);
    } else if (e.key === '+' || e.key === '-' || e.key === '*' || e.key === '/') {
        handleOperator(e.key);
    } else if (e.key === 'Enter' || e.key === '=') {
        calculate();
    } else if (e.key === 'Escape') {
        clear();
    } else if (e.key === 'Backspace') {
        deleteLastDigit();
    } else if (e.key === '%') {
        percent();
    }
});

// ==================== ANIMATIONS ====================
function animateButton(button) {
    button.classList.add('pressed');
    setTimeout(() => {
        button.classList.remove('pressed');
    }, 200);
}

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', () => {
    updateDisplay();
    renderHistory();

    // Add entrance animation
    const calculator = document.querySelector('.calculator');
    const scientificCalc = document.querySelector('.scientific-calc');

    calculator.style.opacity = '0';
    calculator.style.transform = 'translateY(30px)';
    scientificCalc.style.opacity = '0';
    scientificCalc.style.transform = 'translateY(30px)';

    setTimeout(() => {
        calculator.style.transition = 'all 0.6s ease';
        calculator.style.opacity = '1';
        calculator.style.transform = 'translateY(0)';
    }, 100);

    setTimeout(() => {
        scientificCalc.style.transition = 'all 0.6s ease';
        scientificCalc.style.opacity = '1';
        scientificCalc.style.transform = 'translateY(0)';
    }, 300);
});

// ==================== CONSOLE MESSAGE ====================
console.log('%c🧮 Calculadora Avanzada', 'color: #6366f1; font-size: 20px; font-weight: bold;');
console.log('%cCaracterísticas:', 'color: #ec4899; font-size: 14px; font-weight: bold;');
console.log('✓ Operaciones básicas: +, -, ×, ÷');
console.log('✓ Funciones científicas: sin, cos, tan, log, √, x², x³, xʸ');
console.log('✓ Constantes matemáticas: π, e');
console.log('✓ Funciones especiales: factorial, inverso');
console.log('✓ Historial de cálculos con timestamps');
console.log('✓ Soporte completo de teclado');
console.log('✓ Manejo de errores y validaciones');
console.log('%cPrueba a usar el teclado para cálculos más rápidos!', 'color: #14b8a6; font-size: 12px;');
