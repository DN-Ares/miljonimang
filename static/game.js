(function () {
    const POINTS = [
        100, 200, 300, 500, 1000,
        2000, 4000, 8000, 16000, 32000,
        64000, 125000, 250000, 500000, 1000000,
    ];

    const SAFE_LEVELS = { 4: 1000, 9: 32000, 14: 1000000 };

    const app = document.getElementById("game-app");
    if (!app) return;

    const assignmentId = app.dataset.assignmentId;
    const assignmentTitle = app.dataset.assignmentTitle || "";
    let questions = [];
    let currentQuestion = 0;
    let score = 0;
    let lifelines = { fifty_fifty: true, ask_ai: true, ask_audience: true };
    let gameOver = false;
    let gameWon = false;
    let isAnswering = false;

    const loadingScreen = document.getElementById("loading-screen");
    const questionScreen = document.getElementById("question-screen");
    const feedbackScreen = document.getElementById("feedback-screen");
    const gameoverScreen = document.getElementById("gameover-screen");
    const feedbackCard = document.getElementById("feedback-card");
    const pointsList = document.getElementById("points-list");
    const questionNumber = document.getElementById("question-number");
    const questionPoints = document.getElementById("question-points");
    const questionText = document.getElementById("question-text");
    const optionsGrid = document.getElementById("options-grid");
    const currentScoreDisplay = document.getElementById("current-score-display");
    const lifelineBtns = document.querySelectorAll(".lifeline-btn");
    const audienceModal = document.getElementById("audience-modal");
    const audienceBars = document.getElementById("audience-bars");
    const assignmentPanel = document.getElementById("assignment-panel");
    const assignmentContent = document.getElementById("assignment-content");
    const assignmentFiles = document.getElementById("assignment-files");

    function formatPoints(pts) {
        return pts.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
    }

    function renderScoreboard(currentIdx) {
        pointsList.innerHTML = "";
        for (let i = POINTS.length - 1; i >= 0; i--) {
            const row = document.createElement("div");
            row.className = "point-row";
            if (i in SAFE_LEVELS) row.classList.add("safe-level");
            if (i === currentIdx) row.classList.add("current");
            else if (i < currentIdx) row.classList.add("completed");

            const num = document.createElement("span");
            num.textContent = i + 1 === 15 ? "💰 " : "";
            num.textContent += `${i + 1}. küsimus`;

            const pts = document.createElement("span");
            pts.textContent = formatPoints(POINTS[i]);

            row.appendChild(num);
            row.appendChild(pts);
            pointsList.appendChild(row);
        }
    }

    function updateScoreDisplay() {
        if (currentScoreDisplay) {
            currentScoreDisplay.textContent = formatPoints(score);
        }
    }

    function loadQuestions() {
        loadingScreen.classList.remove("hidden");
        questionScreen.classList.add("hidden");
        feedbackScreen.classList.add("hidden");
        gameoverScreen.classList.add("hidden");

        fetch(`/api/questions/${assignmentId}`)
            .then((res) => res.json())
            .then((data) => {
                if (data.error) throw new Error(data.error);
                questions = data;
                currentQuestion = 0;
                score = 0;
                gameOver = false;
                gameWon = false;
                lifelines = { fifty_fifty: true, ask_ai: true, ask_audience: true };
                renderScoreboard(0);
                updateScoreDisplay();
                showQuestion(0);
            })
            .catch((err) => {
                loadingScreen.innerHTML = `
                    <p>Viga: ${err.message}</p>
                    <button class="btn btn-primary" onclick="location.reload()">Proovi uuesti</button>
                `;
            });
    }

    function showQuestion(index) {
        if (index >= questions.length) {
            gameWon = true;
            showGameOver();
            return;
        }

        loadingScreen.classList.add("hidden");
        questionScreen.classList.remove("hidden");
        feedbackScreen.classList.add("hidden");
        gameoverScreen.classList.add("hidden");

        const q = questions[index];
        questionNumber.textContent = `Küsimus ${index + 1}/${questions.length}`;
        questionPoints.textContent = `${formatPoints(POINTS[index])} punkti`;
        questionText.textContent = q.question;

        const labels = ["A", "B", "C", "D"];
        optionsGrid.innerHTML = "";
        isAnswering = false;

        q.options.forEach((opt, i) => {
            const btn = document.createElement("button");
            btn.className = "option-btn";
            btn.dataset.index = i;
            btn.innerHTML = `
                <span class="option-label">${labels[i]}</span>
                <span class="option-text">${opt}</span>
            `;
            btn.addEventListener("click", () => handleAnswer(index, i));
            optionsGrid.appendChild(btn);
        });

        renderScoreboard(index);
        updateLifelineState();
    }

    function updateLifelineState() {
        lifelineBtns.forEach((btn) => {
            const type = btn.dataset.type;
            btn.disabled = !lifelines[type];
        });
    }

    function handleAnswer(qIndex, selected) {
        if (isAnswering || gameOver) return;
        isAnswering = true;

        const btns = optionsGrid.querySelectorAll(".option-btn");
        btns.forEach((b) => (b.disabled = true));

        fetch("/api/answer", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question_num: qIndex, selected }),
        })
            .then((res) => res.json())
            .then((data) => {
                const q = questions[qIndex];
                btns.forEach((b, i) => {
                    if (i === q.correctIndex) b.classList.add("correct");
                    if (i === selected && !data.correct) b.classList.add("wrong");
                });

                setTimeout(() => {
                    if (data.game_over) {
                        score = data.score;
                        gameOver = true;
                        updateScoreDisplay();
                        showFeedback(data, qIndex, true);
                    } else if (data.game_won) {
                        score = data.score;
                        gameWon = true;
                        updateScoreDisplay();
                        showFeedback(data, qIndex, false);
                    } else {
                        score = data.score;
                        updateScoreDisplay();
                        showFeedback(data, qIndex, false);
                    }
                }, 1000);
            })
            .catch((err) => {
                isAnswering = false;
                btns.forEach((b) => (b.disabled = false));
            });
    }

    function showFeedback(data, qIndex, isGameOver) {
        questionScreen.classList.add("hidden");
        feedbackScreen.classList.remove("hidden");

        const correct = data.correct || false;

        feedbackCard.innerHTML = `
            <div class="${correct ? "feedback-correct" : "feedback-wrong"}">
                ${correct ? "Õige vastus!" : "Vale vastus!"}
            </div>
            <div class="feedback-explanation">${data.explanation}</div>
            <button class="feedback-next-btn" id="feedback-next">
                ${isGameOver ? "Vaata tulemust" : gameWon ? "Vaata tulemust" : "Järgmine küsimus"}
            </button>
        `;

        document.getElementById("feedback-next").addEventListener("click", () => {
            if (isGameOver || gameWon) {
                showGameOver();
            } else {
                currentQuestion = qIndex + 1;
                showQuestion(currentQuestion);
            }
        });
    }

    function showGameOver() {
        feedbackScreen.classList.add("hidden");
        questionScreen.classList.add("hidden");
        gameoverScreen.classList.remove("hidden");

        document.getElementById("gameover-title").textContent = gameWon
            ? "Palju õnne!"
            : "Mäng läbi!";
        document.getElementById("gameover-score").textContent = `Sinu punktisumma: ${formatPoints(score)}`;

        document.getElementById("won-message").classList.toggle("hidden", !gameWon);
    }

    lifelineBtns.forEach((btn) => {
        btn.addEventListener("click", () => {
            const type = btn.dataset.type;
            if (!lifelines[type] || isAnswering || gameOver) return;

            fetch("/api/lifeline", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ type, question_num: currentQuestion }),
            })
                .then((res) => res.json())
                .then((data) => {
                    lifelines[type] = false;
                    btn.disabled = true;

                    if (data.type === "fifty_fifty") {
                        const btns = optionsGrid.querySelectorAll(".option-btn");
                        btns.forEach((b, i) => {
                            if (!data.remaining.includes(i)) {
                                b.style.visibility = "hidden";
                            }
                        });
                    } else if (data.type === "ask_audience") {
                        showAudienceVotes(data.votes);
                    } else if (data.type === "ask_ai") {
                        alert("🤖 " + data.hint);
                    }
                });
        });
    });

    function showAudienceVotes(votes) {
        audienceBars.innerHTML = "";
        const colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12"];
        const labels = ["A", "B", "C", "D"];

        Object.entries(votes).forEach(([key, val], i) => {
            const bar = document.createElement("div");
            bar.className = "audience-bar-item";
            bar.innerHTML = `
                <span class="audience-label" style="color:${colors[i]}">${key}</span>
                <div class="audience-bar-track">
                    <div class="audience-bar-fill" style="width:${val}%;background:${colors[i]}"></div>
                </div>
                <span class="audience-pct">${val}%</span>
            `;
            audienceBars.appendChild(bar);
        });

        audienceModal.classList.remove("hidden");
    }

    document.getElementById("close-audience")?.addEventListener("click", () => {
        audienceModal.classList.add("hidden");
    });

    document.getElementById("btn-restart")?.addEventListener("click", () => {
        fetch("/api/restart", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ assignment_id: assignmentId }),
        })
            .then((res) => res.json())
            .then((data) => {
                if (data.success) {
                    loadQuestions();
                }
            });
    });

    document.getElementById("btn-regenerate")?.addEventListener("click", () => {
        if (confirm("Kas soovid genereerida uued küsimused? Praegune mäng läheb kaotsi.")) {
            fetch("/api/regenerate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ assignment_id: assignmentId }),
            })
                .then((res) => res.json())
                .then((data) => {
                    if (data.success) {
                        loadQuestions();
                    }
                });
        }
    });

    document.getElementById("btn-toggle-assignment")?.addEventListener("click", () => {
        const isHidden = assignmentPanel.classList.toggle("hidden");
        const btn = document.getElementById("btn-toggle-assignment");
        btn.textContent = isHidden ? "Näita ülesannet" : "Peida ülesanne";

        if (!isHidden && !assignmentPanel.dataset.loaded) {
            loadAssignmentContent();
            assignmentPanel.dataset.loaded = "true";
        }
    });

    function loadAssignmentContent() {
        fetch(`/api/assignment/${assignmentId}`)
            .then((res) => res.json())
            .then((data) => {
                if (typeof marked === "function") {
                    assignmentContent.innerHTML = marked.parse(data.content);
                } else {
                    assignmentContent.innerHTML = `<pre>${escapeHtml(data.content)}</pre>`;
                }

                let filesHtml = "<h3>Lahenduse failid</h3>";
                for (const [path, content] of Object.entries(data.solution_files)) {
                    const lang = getFileLang(path);
                    filesHtml += `<div class="file-block">
                        <div class="file-path">📄 ${escapeHtml(path)}</div>
                        <pre><code class="language-${lang}">${escapeHtml(content)}</code></pre>
                    </div>`;
                }
                assignmentFiles.innerHTML = filesHtml;

                if (typeof hljs !== "undefined") {
                    document.querySelectorAll("#assignment-files pre code").forEach((block) => {
                        hljs.highlightElement(block);
                    });
                }
            })
            .catch(() => {
                assignmentContent.innerHTML = "<p>Ülesande sisu laadimine ebaõnnestus.</p>";
            });
    }

    function getFileLang(path) {
        if (path.endsWith(".js")) return "javascript";
        if (path.endsWith(".py")) return "python";
        if (path.endsWith(".css")) return "css";
        if (path.endsWith(".html")) return "html";
        if (path.endsWith(".json")) return "json";
        if (path.endsWith(".md")) return "markdown";
        return "plaintext";
    }

    function escapeHtml(str) {
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    }

    loadQuestions();
})();
