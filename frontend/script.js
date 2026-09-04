let selectedPosition = null;
let gameState = null;
let gameStartTime = Date.now();
let aiThinking = false;
let selectedAlgorithmChoice = null;

const NODE_COORDINATES = {
    'a7': [20, 20],   'd7': [200, 20],  'g7': [380, 20],
    'b6': [80, 80],   'd6': [200, 80],  'f6': [320, 80],
    'c5': [140, 140], 'd5': [200, 140], 'e5': [260, 140],
    'a4': [20, 200],  'b4': [80, 200],  'c4': [140, 200],
    'e4': [260, 200], 'f4': [320, 200], 'g4': [380, 200],
    'c3': [140, 260], 'd3': [200, 260], 'e3': [260, 260],
    'b2': [80, 320],  'd2': [200, 320], 'f2': [320, 320],
    'a1': [20, 380],  'd1': [200, 380], 'g1': [380, 380]
};

const REVERSE_NOTATION = {
    'a7': 0, 'd7': 1, 'g7': 2,
    'b6': 3, 'd6': 4, 'f6': 5,
    'c5': 6, 'd5': 7, 'e5': 8,
    'a4': 9, 'b4': 10, 'c4': 11,
    'e4': 12, 'f4': 13, 'g4': 14,
    'c3': 15, 'd3': 16, 'e3': 17,
    'b2': 18, 'd2': 19, 'f2': 20,
    'a1': 21, 'd1': 22, 'g1': 23
};

document.addEventListener('DOMContentLoaded', () => {
    loadAlgorithmChoices();
});

function loadAlgorithmChoices() {
    fetch('/api/algorithms')
        .then(res => res.json())
        .then(data => {
            renderAlgorithmOptions(data.algorithms, data.selected);
        })
        .catch(err => console.error("Error loading algorithms:", err));
}

function renderAlgorithmOptions(algorithms, defaultKey) {
    const container = document.getElementById('algo-options');
    if (!container) return;
    container.innerHTML = '';

    selectedAlgorithmChoice = defaultKey || (algorithms[0] && algorithms[0].key);

    algorithms.forEach(algo => {
        const label = document.createElement('label');
        label.className = 'algo-option' + (algo.key === selectedAlgorithmChoice ? ' selected' : '');

        const radio = document.createElement('input');
        radio.type = 'radio';
        radio.name = 'algo-choice';
        radio.value = algo.key;
        radio.checked = algo.key === selectedAlgorithmChoice;
        radio.addEventListener('change', () => {
            selectedAlgorithmChoice = algo.key;
            document.querySelectorAll('.algo-option').forEach(el => el.classList.remove('selected'));
            label.classList.add('selected');
        });

        const text = document.createElement('span');
        text.textContent = algo.label;

        label.appendChild(radio);
        label.appendChild(text);
        container.appendChild(label);
    });
}

function openAlgorithmModal() {
    document.getElementById('algo-modal-overlay')?.classList.remove('hidden');
}

function closeAlgorithmModal() {
    document.getElementById('algo-modal-overlay')?.classList.add('hidden');
}

function startGameWithAlgorithm() {
    if (!selectedAlgorithmChoice) return;
    resetGame(selectedAlgorithmChoice);
}

function fetchGameState() {
    fetch('/api/state')
        .then(res => res.json())
        .then(data => {
            gameState = data;
            render();
        })
        .catch(err => console.error("Error fetching state:", err));
}

function handleNodeClick(posStr) {
    if (!gameState || gameState.winner !== null || aiThinking) return;
    if (gameState.currentPlayer === gameState.aiPlayer) return;

    const posIndex = REVERSE_NOTATION[posStr];

    if (gameState.remove) {
        sendAction({ type: "remove", position: posIndex });
        return;
    }

    const unplaced = gameState.unplacedMen[gameState.currentPlayer];
    if (unplaced > 0) {
        sendAction({ type: "place", position: posIndex });
    } else {
        if (selectedPosition === null) {
            if (gameState.board[posIndex] === gameState.currentPlayer) {
                selectedPosition = posIndex;
                render();
            }
        } else {
            if (posIndex === selectedPosition) {
                selectedPosition = null;
                render();
            } else {
                sendAction({ type: "move", start: selectedPosition, end: posIndex });
                selectedPosition = null;
            }
        }
    }
}

function sendAction(actionData) {
    fetch('/api/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(actionData)
    })
    .then(res => res.json())
    .then(data => {
        gameState = data;
        render();
    })
    .catch(err => console.error("Error sending action:", err));
}

function resetGame(algorithm) {
    selectedPosition = null;
    aiThinking = false;
    gameStartTime = Date.now();

    const algoToUse = algorithm || selectedAlgorithmChoice;

    fetch('/api/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(algoToUse ? { algorithm: algoToUse } : {})
    })
        .then(res => res.json())
        .then(data => {
            gameState = data;
            closeHelpModal();
            closeAlgorithmModal();
            const winModal = document.getElementById('modal-overlay');
            if (winModal) winModal.classList.add('hidden');
            render();
        });
}

function render() {
    if (!gameState) return;

    updatePlayerCards();
    renderBoard();
    renderStatus();
    renderMoves();
    checkGameOver();
    maybeTriggerAI();
}

function maybeTriggerAI() {
    if (!gameState || aiThinking) return;
    if (gameState.winner !== null && gameState.winner !== undefined) return;
    if (gameState.currentPlayer !== gameState.aiPlayer) return;

    aiThinking = true;
    const statusBar = document.getElementById('status-bar');
    if (statusBar) statusBar.innerText = 'AI is thinking...';

    setTimeout(() => {
        fetch('/api/ai_move', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                aiThinking = false;
                gameState = data;
                render();
            })
            .catch(err => {
                console.error("Error on AI move:", err);
                aiThinking = false;
            });
    }, 400);
}

function updatePlayerCards() {
    const p1Hand = gameState.unplacedMen[1];
    const p2Hand = gameState.unplacedMen[2];

    const p1Mills = gameState.mills ? gameState.mills[1] : 0;
    const p2Mills = gameState.mills ? gameState.mills[2] : 0;
    document.getElementById('p1-mills').innerText = p1Mills;
    document.getElementById('p2-mills').innerText = p2Mills;

    const p1Tokens = document.getElementById('p1-tokens');
    if (p1Tokens) {
        p1Tokens.innerHTML = '';
        for (let i = 0; i < 9; i++) {
            const dot = document.createElement('div');
            dot.className = `token-dot token-p1 ${i < p1Hand ? '' : 'token-empty'}`;
            p1Tokens.appendChild(dot);
        }
    }
    document.getElementById('p1-hand').innerText = p1Hand;
    const p1Phase = p1Hand > 0 ? 1 : (gameState.placedMen[1] > 3 ? 2 : 3);
    document.getElementById('p1-phase').innerText = `Phase ${p1Phase}: ${getPhaseName(p1Phase)}`;

    const p2Tokens = document.getElementById('p2-tokens');
    if (p2Tokens) {
        p2Tokens.innerHTML = '';
        for (let i = 0; i < 9; i++) {
            const dot = document.createElement('div');
            dot.className = `token-dot token-p2 ${i < p2Hand ? '' : 'token-empty'}`;
            p2Tokens.appendChild(dot);
        }
    }
    document.getElementById('p2-hand').innerText = p2Hand;
    const p2Phase = p2Hand > 0 ? 1 : (gameState.placedMen[2] > 3 ? 2 : 3);
    document.getElementById('p2-phase').innerText = `Phase ${p2Phase}: ${getPhaseName(p2Phase)}`;

    document.getElementById('panel-p1').classList.toggle('active', gameState.currentPlayer === 1);
    document.getElementById('panel-p2').classList.toggle('active', gameState.currentPlayer === 2);
}

function renderBoard() {
    const container = document.getElementById('nodes-container');
    if (!container) return;
    container.innerHTML = '';

    const targets = gameState.targets;

    for (const [posStr, coords] of Object.entries(NODE_COORDINATES)) {
        const posIndex = REVERSE_NOTATION[posStr];
        const owner = gameState.board[posIndex];
        const [cx, cy] = coords;

        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', cx);
        circle.setAttribute('cy', cy);
        circle.setAttribute('data-pos', posStr);

        let cssClasses = [];

        if (owner === 0) {
            circle.setAttribute('r', '6');
            cssClasses.push('board-node');
        } else if (owner === 1) {
            circle.setAttribute('r', '11');
            cssClasses.push('piece-p1');
        } else if (owner === 2) {
            circle.setAttribute('r', '11');
            cssClasses.push('piece-p2');
        }

        if (selectedPosition === posIndex) {
            cssClasses.push('selected');
        }

        if (selectedPosition !== null && targets && targets.mode === 'move') {
            const isTarget = targets.moves.some(m => m[0] === selectedPosition && m[1] === posIndex);
            if (isTarget) cssClasses.push('valid-target');
        }

        if (gameState.remove && targets && targets.mode === 'remove') {
            if (targets.positions.includes(posIndex)) {
                cssClasses.push('piece-removable');
            }
        }

        circle.setAttribute('class', cssClasses.join(' '));
        circle.addEventListener('click', () => handleNodeClick(posStr));
        container.appendChild(circle);
    }
}

function renderStatus() {
    const statusBar = document.getElementById('status-bar');
    if (!statusBar) return;

    if (gameState.winner !== null && gameState.winner !== undefined) {
        statusBar.innerText = gameState.winner === 0 ? "Game Over! Draw!" : `Game Over! Player ${gameState.winner} Wins!`;
        return;
    }

    if (aiThinking) {
        statusBar.innerText = 'AI is thinking...';
        return;
    }

    if (gameState.remove) {
        statusBar.innerText = `MILL FORMED! Player ${gameState.currentPlayer}: Remove an opponent's piece!`;
        return;
    }

    const unplaced = gameState.unplacedMen[gameState.currentPlayer];
    const placed = gameState.placedMen[gameState.currentPlayer];
    const phaseNum = unplaced > 0 ? 1 : (placed > 3 ? 2 : 3);

    if (phaseNum === 1) {
        statusBar.innerText = `Player ${gameState.currentPlayer}'s turn - place a piece on the board`;
    } else if (phaseNum === 2) {
        statusBar.innerText = `Player ${gameState.currentPlayer}'s turn - select and move a piece`;
    } else {
        statusBar.innerText = `Player ${gameState.currentPlayer}'s turn - FLY anywhere on the board!`;
    }
}

function renderMoves() {
    const movesList = document.getElementById('moves-list');
    if (!movesList) return;
    movesList.innerHTML = '';

    if (!gameState.moveHistory) return;

    gameState.moveHistory.forEach((move, index) => {
        const row = document.createElement('div');
        row.className = 'move-row';
        row.innerHTML = `<span>${index + 1}. P${move.player}</span> <span>${move.text}</span>`;
        movesList.appendChild(row);
    });

    movesList.scrollTop = movesList.scrollHeight;
}

function checkGameOver() {
    if (gameState.winner !== null && gameState.winner !== undefined) {
        const modal = document.getElementById('modal-overlay');
        if (modal) {
            document.getElementById('modal-title').innerText = gameState.winner === 0 ? "IT'S A DRAW!" : `PLAYER ${gameState.winner} WINS!`;
            document.getElementById('stat-moves').innerText = gameState.moveHistory ? gameState.moveHistory.length : 0;

            const p1Mills = gameState.mills ? gameState.mills[1] : 0;
            const p2Mills = gameState.mills ? gameState.mills[2] : 0;
            document.getElementById('stat-mills-p1').innerText = p1Mills;
            document.getElementById('stat-mills-p2').innerText = p2Mills;

            const durationMs = Date.now() - gameStartTime;
            const totalSec = Math.floor(durationMs / 1000);
            const mins = Math.floor(totalSec / 60);
            const secs = totalSec % 60;
            document.getElementById('stat-duration').innerText = `${mins}:${secs < 10 ? '0' : ''}${secs}`;

            modal.classList.remove('hidden');
        }
    }
}

function getPhaseName(phase) {
    if (phase === 1) return 'Placing';
    if (phase === 2) return 'Moving';
    return 'Flying';
}

function openHelpModal() {
    document.getElementById('help-modal-overlay')?.classList.remove('hidden');
}

function closeHelpModal() {
    document.getElementById('help-modal-overlay')?.classList.add('hidden');
}