const board = document.getElementById("sudoku-board");
let originalPuzzle = [];
let currentLevel = "easy";
let solution = [];
let puzzle = [];
let timerInterval = null;
let startTime = 0;
let score = 0;
let mistakes = 0;


const levelScores = {
    easy: 35,
    medium: 45,
    hard: 55
};

/* ---------------- SUDOKU LOGIC ---------------- */

function emptyBoard() {
    return Array.from({ length: 9 }, () => Array(9).fill(0));
}

function isSafe(board, r, c, n) {
    for (let i = 0; i < 9; i++) {
        if (board[r][i] === n || board[i][c] === n) return false;
    }
    let sr = r - r % 3;
    let sc = c - c % 3;
    for (let i = 0; i < 3; i++)
        for (let j = 0; j < 3; j++)
            if (board[sr + i][sc + j] === n) return false;
    return true;
}

function shuffledNumbers() {
    const nums = [1,2,3,4,5,6,7,8,9];
    for (let i = nums.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [nums[i], nums[j]] = [nums[j], nums[i]];
    }
    return nums;
}


function solveSudoku(board) {
    for (let r = 0; r < 9; r++) {
        for (let c = 0; c < 9; c++) {
            if (board[r][c] === 0) {
                const nums = shuffledNumbers();
                for (let n of nums) {
                    if (isSafe(board, r, c, n)) {
                        board[r][c] = n;
                        if (solveSudoku(board)) return true;
                        board[r][c] = 0;
                    }
                }
                return false;
            }
        }
    }
    return true;
}


function generateSolution() {
    let b = emptyBoard();
    solveSudoku(b);
    return b;
}

function generatePuzzle(sol, level) {
    let p = sol.map(r => r.slice());
    let remove = levelScores[level];
    while (remove > 0) {
        let r = Math.floor(Math.random() * 9);
        let c = Math.floor(Math.random() * 9);
        if (p[r][c] !== 0) {
            p[r][c] = 0;
            remove--;
        }
    }
    return p;
}

/* ---------------- UI ---------------- */

// function createBoard() {
//     board.innerHTML = "";

//     for (let r = 0; r < 9; r++) {
//         for (let c = 0; c < 9; c++) {
//             const cell = document.createElement("input");
//             cell.type = "text";
//             cell.maxLength = 1;

//             if (puzzle[r][c] !== 0) {
//                 cell.value = puzzle[r][c];
//                 cell.disabled = true;
//             }

//             // 3x3 borders
//             if (c % 3 === 0) cell.style.borderLeft = "3px solid white";
//             if (r % 3 === 0) cell.style.borderTop = "3px solid white";
//             if (c === 8) cell.style.borderRight = "3px solid white";
//             if (r === 8) cell.style.borderBottom = "3px solid white";

//             board.appendChild(cell);
//         }
//     }
// }

function createBoard() {
    board.innerHTML = "";

    for (let r = 0; r < 9; r++) {
        for (let c = 0; c < 9; c++) {

            const cell = document.createElement("input");
            cell.type = "text";
            cell.maxLength = 1;

            cell.dataset.solution = solution[r][c];
            cell.dataset.row = r;
            cell.dataset.col = c;
            cell.dataset.correct = "false";
            cell.dataset.mistake = "false";

            if (puzzle[r][c] !== 0) {
                cell.value = puzzle[r][c];
                cell.disabled = true;
            }

            cell.addEventListener("input", () => {
                if (cell.disabled) return;

                const val = Number(cell.value);

                cell.classList.remove("correct", "wrong");

                if (!val || val < 1 || val > 9) {
                    cell.value = "";
                    return;
                }

                if (val === solution[r][c]) {
                    if (cell.dataset.correct === "false") {
                        score += levelScores[currentLevel];
                        document.getElementById("score").textContent = score;
                        cell.dataset.correct = "true";
                    }
                    cell.dataset.mistake = "false";
                    cell.classList.add("correct");
                } else {
                    if (cell.dataset.mistake === "false") {
                        mistakes++;
                        document.getElementById("mistakes").textContent = mistakes;
                        cell.dataset.mistake = "true";
                    }
                    cell.dataset.correct = "false";
                    cell.classList.add("wrong");
                }
            });

            cell.addEventListener("focus", () => {
                highlightRowCol(r, c);
                cell.classList.add("active");
            });

            // 3x3 borders
            if (c % 3 === 0) cell.style.borderLeft = "3px solid white";
            if (r % 3 === 0) cell.style.borderTop = "3px solid white";
            if (c === 8) cell.style.borderRight = "3px solid white";
            if (r === 8) cell.style.borderBottom = "3px solid white";

            board.appendChild(cell);
        }
    }
}


function highlightRowCol(row, col) {
    const cells = board.querySelectorAll("input");

    cells.forEach(cell => {
        cell.classList.remove("highlight", "active");

        if (
            cell.dataset.row === row ||
            cell.dataset.col === col
        ) {
            cell.classList.add("highlight");
        }
    });
}



/* ---------------- GAME FLOW ---------------- */

function startGame() {
    currentLevel = document.getElementById("level").value;
    score = 0;
    mistakes = 0;
    document.getElementById("mistakes").textContent = "0";


    solution = generateSolution();
    puzzle = generatePuzzle(solution, currentLevel);

    // 🔒 Save original puzzle for reset
    originalPuzzle = puzzle.map(row => row.slice());

    createBoard();
    startTimer();

    document.getElementById("score").textContent = score;
    document.getElementById("timer").textContent = "00:00";
}

function resetGame() {
    puzzle = originalPuzzle.map(row => row.slice());
    createBoard();
}


/* 🔁 Reload grid when difficulty changes */
document.getElementById("level").addEventListener("change", startGame);

function checkSolution() {
    const cells = board.querySelectorAll("input");
    let correctCount = 0;
    let index = 0;

    for (let r = 0; r < 9; r++) {
        for (let c = 0; c < 9; c++) {
            const cell = cells[index];

            if (cell.disabled || Number(cell.value) === solution[r][c]) {
                correctCount++;
            }
            index++;
        }
    }

    clearInterval(timerInterval);
    showResult(correctCount);
}

/* ---------------- TIMER ---------------- */

function startTimer() {
    clearInterval(timerInterval);
    startTime = Date.now();

    timerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const minutes = String(Math.floor(elapsed / 60)).padStart(2, "0");
        const seconds = String(elapsed % 60).padStart(2, "0");
        document.getElementById("timer").textContent = `${minutes}:${seconds}`;
    }, 1000);
}


/* ---------------- MODAL ---------------- */
function showResult(correctCount) {
    const modal = document.getElementById("resultModal");

    const finalScore = Number(document.getElementById("score").textContent);
    const finalTime = Math.floor((Date.now() - startTime) / 1000);
    const result = correctCount === 81 ? "Win" : "Loss";

    fetch("/save_game", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            difficulty: currentLevel,
            score: finalScore,
            time: finalTime,
            mistakes: mistakes,
            result: result
        })
    });

    document.getElementById("resultText").textContent =
        result === "Win" ? "🎉 You solved the Sudoku!" : "Game Completed";

    document.getElementById("finalScore").textContent = finalScore;
    document.getElementById("finalTime").textContent =
        document.getElementById("timer").textContent;

    modal.style.display = "flex";
}



function closeModal() {
    document.getElementById("resultModal").style.display = "none";
}



/* Initial load */
startGame();
