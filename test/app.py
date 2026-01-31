import streamlit as st
import streamlit.components.v1 as components

# ページ設定
st.set_page_config(
    page_title="Neon Breakout",
    page_icon="🎮",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# カスタムCSSでUIを整える
st.markdown("""
    <style>
    .main {
        background-color: #0d0d0d;
        color: #ffffff;
    }
    .stApp {
        background: radial-gradient(circle, #1a1a1a 0%, #000000 100%);
    }
    h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        letter-spacing: -1px;
        text-align: center;
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("NEON BREAKOUT")

# JavaScript Game Engine
game_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            overflow: hidden;
            background-color: transparent;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        canvas {
            border: 2px solid #333;
            box-shadow: 0 0 20px rgba(0, 242, 254, 0.2);
            border-radius: 8px;
            cursor: none;
        }
        #ui {
            position: absolute;
            top: 20px;
            left: 20px;
            color: #00f2fe;
            pointer-events: none;
            font-size: 20px;
            text-shadow: 0 0 10px rgba(0, 242, 254, 0.5);
        }
    </style>
</head>
<body>
    <div id="ui">Score: <span id="score">0</span></div>
    <canvas id="gameCanvas"></canvas>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreElement = document.getElementById('score');

        canvas.width = 600;
        canvas.height = 400;

        // ゲーム定数
        const BALL_RADIUS = 8;
        const PADDLE_HEIGHT = 10;
        const PADDLE_WIDTH = 75;
        const BRICK_ROW_COUNT = 5;
        const BRICK_COLUMN_COUNT = 7;
        const BRICK_WIDTH = 75;
        const BRICK_HEIGHT = 20;
        const BRICK_PADDING = 10;
        const BRICK_OFFSET_TOP = 30;
        const BRICK_OFFSET_LEFT = 30;

        // 色の設定 (ネオンカラー)
        const COLORS = ['#ff00ff', '#00ffff', '#ffff00', '#00ff00', '#ff0000'];

        let x = canvas.width / 2;
        let y = canvas.height - 30;
        let dx = 3;
        let dy = -3;
        let paddleX = (canvas.width - PADDLE_WIDTH) / 2;
        let score = 0;
        let particles = [];

        // ブロックの初期化
        const bricks = [];
        for (let c = 0; c < BRICK_COLUMN_COUNT; c++) {
            bricks[c] = [];
            for (let r = 0; r < BRICK_ROW_COUNT; r++) {
                bricks[c][r] = { x: 0, y: 0, status: 1, color: COLORS[r] };
            }
        }

        // パーティクルクラス
        class Particle {
            constructor(x, y, color) {
                this.x = x;
                this.y = y;
                this.color = color;
                this.size = Math.random() * 3 + 1;
                this.speedX = (Math.random() - 0.5) * 8;
                this.speedY = (Math.random() - 0.5) * 8;
                this.life = 1.0;
            }
            update() {
                this.x += this.speedX;
                this.y += this.speedY;
                this.life -= 0.02;
            }
            draw() {
                ctx.save();
                ctx.globalAlpha = this.life;
                ctx.fillStyle = this.color;
                ctx.shadowBlur = 10;
                ctx.shadowColor = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
        }

        function mouseMoveHandler(e) {
            const rect = canvas.getBoundingClientRect();
            const relativeX = e.clientX - rect.left;
            if (relativeX > 0 && relativeX < canvas.width) {
                paddleX = relativeX - PADDLE_WIDTH / 2;
            }
        }
        document.addEventListener("mousemove", mouseMoveHandler, false);

        function collisionDetection() {
            for (let c = 0; c < BRICK_COLUMN_COUNT; c++) {
                for (let r = 0; r < BRICK_ROW_COUNT; r++) {
                    const b = bricks[c][r];
                    if (b.status === 1) {
                        if (x > b.x && x < b.x + BRICK_WIDTH && y > b.y && y < b.y + BRICK_HEIGHT) {
                            dy = -dy;
                            b.status = 0;
                            score++;
                            scoreElement.innerText = score;
                            createParticles(b.x + BRICK_WIDTH/2, b.y + BRICK_HEIGHT/2, b.color);
                            
                            if (score === BRICK_ROW_COUNT * BRICK_COLUMN_COUNT) {
                                alert("YOU WIN, CONGRATS!");
                                document.location.reload();
                            }
                        }
                    }
                }
            }
        }

        function createParticles(x, y, color) {
            for (let i = 0; i < 15; i++) {
                particles.push(new Particle(x, y, color));
            }
        }

        function drawBall() {
            ctx.beginPath();
            ctx.arc(x, y, BALL_RADIUS, 0, Math.PI * 2);
            ctx.fillStyle = "#ffffff";
            ctx.shadowBlur = 15;
            ctx.shadowColor = "#00f2fe";
            ctx.fill();
            ctx.closePath();
        }

        function drawPaddle() {
            ctx.beginPath();
            ctx.rect(paddleX, canvas.height - PADDLE_HEIGHT - 5, PADDLE_WIDTH, PADDLE_HEIGHT);
            ctx.fillStyle = "#00f2fe";
            ctx.shadowBlur = 15;
            ctx.shadowColor = "#00f2fe";
            ctx.fill();
            ctx.closePath();
        }

        function drawBricks() {
            for (let c = 0; c < BRICK_COLUMN_COUNT; c++) {
                for (let r = 0; r < BRICK_ROW_COUNT; r++) {
                    if (bricks[c][r].status === 1) {
                        const brickX = (c * (BRICK_WIDTH + BRICK_PADDING)) + BRICK_OFFSET_LEFT;
                        const brickY = (r * (BRICK_HEIGHT + BRICK_PADDING)) + BRICK_OFFSET_TOP;
                        bricks[c][r].x = brickX;
                        bricks[c][r].y = brickY;
                        
                        ctx.beginPath();
                        ctx.rect(brickX, brickY, BRICK_WIDTH, BRICK_HEIGHT);
                        ctx.fillStyle = bricks[c][r].color;
                        ctx.shadowBlur = 10;
                        ctx.shadowColor = bricks[c][r].color;
                        ctx.fill();
                        ctx.closePath();
                    }
                }
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // 背景のグリッド描画 (クールな演出)
            ctx.strokeStyle = '#1a1a1a';
            ctx.lineWidth = 1;
            for(let i=0; i<canvas.width; i+=40) {
                ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, canvas.height); ctx.stroke();
            }
            for(let i=0; i<canvas.height; i+=40) {
                ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(canvas.width, i); ctx.stroke();
            }

            drawBricks();
            drawBall();
            drawPaddle();
            collisionDetection();

            // パーティクルの更新と描画
            particles = particles.filter(p => p.life > 0);
            particles.forEach(p => {
                p.update();
                p.draw();
            });

            if (x + dx > canvas.width - BALL_RADIUS || x + dx < BALL_RADIUS) {
                dx = -dx;
            }
            if (y + dy < BALL_RADIUS) {
                dy = -dy;
            } else if (y + dy > canvas.height - BALL_RADIUS - 5) {
                if (x > paddleX && x < paddleX + PADDLE_WIDTH) {
                    dy = -dy;
                    // 跳ね返り角を変化させる
                    dx = 8 * ((x - (paddleX + PADDLE_WIDTH / 2)) / PADDLE_WIDTH);
                } else {
                    alert("GAME OVER");
                    document.location.reload();
                    return;
                }
            }

            x += dx;
            y += dy;
            requestAnimationFrame(draw);
        }

        draw();
    </script>
</body>
</html>
"""

# ゲームを埋め込む
components.html(game_html, height=450, scrolling=False)

st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 10px;">
    Use mouse to move the paddle
    </div>
    """, unsafe_allow_html=True)
