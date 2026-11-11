"""
طيف — TAYF
شاشة المراقبة الطيفية السينمائية المتناسقة — Professional Cyber RF Scope
معالجة مشاكل التناسق، المحاذاة، الانعكاس، وتوسيع المساحة
"""

def get_cinematic_ecg_html(rssi_values: list[float], snr_values: list[float], is_incident: bool = True) -> str:
    rssi_js = str(rssi_values)
    snr_js = str(snr_values)
    
    html_code = f"""
    <!DOCTYPE html>
    <html lang="ar">
    <head>
    <meta charset="utf-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;700&family=Tajawal:wght@500;700;900&display=swap');
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            background: transparent;
            font-family: 'Tajawal', -apple-system, sans-serif;
            overflow: hidden;
            display: flex;
            justify-content: center;
            width: 100%;
        }}
        
        .scope-card {{
            width: 100%;
            max-width: 950px;
            background: #090d16;
            border: 1.5px solid #00f0ff;
            border-radius: 12px;
            box-shadow: 0 0 20px rgba(0, 240, 255, 0.2), inset 0 0 15px rgba(0, 0, 0, 0.8);
            padding: 16px 20px;
        }}
        
        .scope-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            direction: rtl;
        }}
        
        .scope-title {{
            color: #00f0ff;
            font-size: 1.1rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .status-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255, 23, 68, 0.12);
            border: 1px solid #ff1744;
            color: #ff1744;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 700;
        }}
        
        .status-badge.normal {{
            background: rgba(0, 230, 118, 0.12);
            border: 1px solid #00e676;
            color: #00e676;
        }}
        
        .blinker-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: currentColor;
            box-shadow: 0 0 8px currentColor;
            animation: pulse-dot 1.2s infinite;
        }}
        
        @keyframes pulse-dot {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.3; transform: scale(0.85); }}
        }}
        
        .canvas-wrapper {{
            position: relative;
            width: 100%;
            height: 240px;
            border-radius: 8px;
            overflow: hidden;
            background: #030710;
            border: 1px solid rgba(0, 240, 255, 0.25);
        }}
        
        canvas {{
            display: block;
            width: 100%;
            height: 100%;
        }}

        /* شريط القراءات بالأسفل - محاذاة من اليسار لليمين LTR للأرقام لتفادي الانعكاس */
        .hud-dashboard {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-top: 14px;
        }}

        .hud-box {{
            background: #0d131f;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 8px;
            padding: 8px 10px;
            text-align: center;
        }}

        .hud-box.alert {{
            border-color: rgba(255, 23, 68, 0.4);
            background: rgba(255, 23, 68, 0.06);
        }}

        .hud-label {{
            font-size: 0.75rem;
            color: #94a3b8;
            margin-bottom: 4px;
            font-weight: 500;
        }}

        /* إجبار الأرقام والوحدات على الاتجاه الطبيعي بدون قلب */
        .hud-value {{
            font-family: 'Chakra Petch', monospace;
            font-size: 1.15rem;
            font-weight: 700;
            direction: ltr !important;
            unicode-bidi: isolate !important;
            letter-spacing: 0.5px;
        }}
        
        /* تسميات خطوط النبضة */
        .legend-tag {{
            position: absolute;
            right: 12px;
            font-size: 0.75rem;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 4px;
            pointer-events: none;
            background: rgba(0,0,0,0.6);
            backdrop-filter: blur(2px);
        }}
    </style>
    </head>
    <body>

    <div class="scope-card">
        <div class="scope-header">
            <div class="scope-title">
                <span>📡 رادار المراقبة الطيفية الحية</span>
                <span style="font-size: 0.8rem; color: #64748b; font-family: monospace;">(RF Live Telemetry)</span>
            </div>
            <div class="status-badge {'normal' if not is_incident else ''}">
                <div class="blinker-dot"></div>
                <span>{'مسرح الجريمة: تشويش نشط' if is_incident else 'الحالة: طبيعية ومستقرة'}</span>
            </div>
        </div>

        <div class="canvas-wrapper">
            <span class="legend-tag" style="top: 10px; color: #00e676; border: 1px solid #00e676;">قوة الإشارة RSSI</span>
            <span class="legend-tag" style="bottom: 15px; color: #ffd600; border: 1px solid #ffd600;">نسبة SNR</span>
            <canvas id="scopeCanvas"></canvas>
        </div>

        <div class="hud-dashboard">
            <div class="hud-box">
                <div class="hud-label">قوة الإشارة الحية RSSI</div>
                <div class="hud-value" id="valRssi" style="color: #00e676;">-55.0 dBm</div>
            </div>
            <div class="hud-box" id="snrBox">
                <div class="hud-label">نسبة الإشارة إلى الضوضاء SNR</div>
                <div class="hud-value" id="valSnr" style="color: #ffd600;">39.2 dB</div>
            </div>
            <div class="hud-box">
                <div class="hud-label">معدل الإطارات</div>
                <div class="hud-value" style="color: #00f0ff;">60.0 FPS</div>
            </div>
            <div class="hud-box">
                <div class="hud-label">تردد القناة</div>
                <div class="hud-value" style="color: #e2e8f0;">2.400 GHz</div>
            </div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('scopeCanvas');
        const ctx = canvas.getContext('2d');
        const valRssi = document.getElementById('valRssi');
        const valSnr = document.getElementById('valSnr');
        const snrBox = document.getElementById('snrBox');

        // ضبط أبعاد الـ Canvas الداخلية لتطابق الحجم الحقيقي بدقة
        function resizeCanvas() {{
            canvas.width = canvas.parentElement.clientWidth;
            canvas.height = canvas.parentElement.clientHeight;
        }}
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        const rssiData = {rssi_js};
        const snrData = {snr_js};
        const totalPoints = rssiData.length;

        let sweepX = 0;
        const sweepSpeed = 2.2;
        let historyPoints = [];

        function drawGrid(w, h) {{
            ctx.strokeStyle = "rgba(0, 240, 255, 0.07)";
            ctx.lineWidth = 1;
            const step = 32;

            for (let x = 0; x < w; x += step) {{
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, h);
                ctx.stroke();
            }}
            for (let y = 0; y < h; y += step) {{
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(w, y);
                ctx.stroke();
            }}

            // خط فاصل بين القناتين
            ctx.strokeStyle = "rgba(0, 240, 255, 0.2)";
            ctx.setLineDash([6, 4]);
            ctx.beginPath();
            ctx.moveTo(0, h * 0.52);
            ctx.lineTo(w, h * 0.52);
            ctx.stroke();
            ctx.setLineDash([]);
        }}

        function render() {{
            const w = canvas.width;
            const h = canvas.height;

            // مسح تدريجي بأثر توهج سينمائي خفيف
            ctx.fillStyle = "rgba(3, 7, 16, 0.18)";
            ctx.fillRect(0, 0, w, h);

            drawGrid(w, h);

            sweepX += sweepSpeed;
            if (sweepX > w) {{
                sweepX = 0;
                historyPoints = [];
            }}

            const progress = sweepX / w;
            const idx = Math.min(totalPoints - 1, Math.floor(progress * totalPoints));
            
            const curRssi = rssiData[idx] ?? -60;
            const curSnr = snrData[idx] ?? 20;

            // تحديث شريط القياسات السفلي بدقة واتجاه سليم
            valRssi.textContent = curRssi.toFixed(1) + " dBm";
            valSnr.textContent = curSnr.toFixed(1) + " dB";

            if (curSnr < 10) {{
                valSnr.style.color = "#ff1744";
                snrBox.classList.add('alert');
            }} else {{
                valSnr.style.color = "#ffd600";
                snrBox.classList.remove('alert');
            }}

            // موازنة الإحداثيات العمودية بدقة بدون تداخل
            // RSSI في النصف العلوي (بين y=25 و y=105)
            const normRssi = Math.max(0, Math.min(1, (curRssi - (-95)) / ( -35 - (-95) )));
            const yRssi = (h * 0.45) - (normRssi * (h * 0.35));

            // SNR في النصف السفلي (بين y=130 و y=220)
            const normSnr = Math.max(0, Math.min(1, (curSnr - (-5)) / ( 45 - (-5) )));
            const ySnr = (h * 0.92) - (normSnr * (h * 0.35));

            historyPoints.push({{ x: sweepX, yRssi: yRssi, ySnr: ySnr, isBad: (curSnr < 10) }});

            // رسم خط RSSI الأخضر
            ctx.shadowBlur = 10;
            ctx.shadowColor = "#00e676";
            ctx.strokeStyle = "#00e676";
            ctx.lineWidth = 2.2;
            ctx.beginPath();
            for (let i = 0; i < historyPoints.length; i++) {{
                const p = historyPoints[i];
                if (i === 0) ctx.moveTo(p.x, p.yRssi);
                else ctx.lineTo(p.x, p.yRssi);
            }}
            ctx.stroke();

            // رسم خط SNR الأصفر / الأحمر
            ctx.lineWidth = 2.2;
            for (let i = 1; i < historyPoints.length; i++) {{
                const p0 = historyPoints[i - 1];
                const p1 = historyPoints[i];
                const col = p1.isBad ? "#ff1744" : "#ffd600";
                ctx.shadowColor = col;
                ctx.strokeStyle = col;
                ctx.beginPath();
                ctx.moveTo(p0.x, p0.ySnr);
                ctx.lineTo(p1.x, p1.ySnr);
                ctx.stroke();
            }}

            // شعاع مسح الليزر الراداري الأزرق
            ctx.shadowBlur = 14;
            ctx.shadowColor = "#00f0ff";
            ctx.strokeStyle = "rgba(0, 240, 255, 0.85)";
            ctx.lineWidth = 2.5;
            ctx.beginPath();
            ctx.moveTo(sweepX, 0);
            ctx.lineTo(sweepX, h);
            ctx.stroke();

            // رؤوس مؤشرات التتبع اللحظي
            ctx.fillStyle = "#ffffff";
            ctx.shadowBlur = 12;
            ctx.shadowColor = "#00e676";
            ctx.beginPath();
            ctx.arc(sweepX, yRssi, 4, 0, Math.PI * 2);
            ctx.fill();

            ctx.shadowColor = (curSnr < 10) ? "#ff1744" : "#ffd600";
            ctx.beginPath();
            ctx.arc(sweepX, ySnr, 4, 0, Math.PI * 2);
            ctx.fill();

            ctx.shadowBlur = 0; // إعادة ضبط التوهج

            requestAnimationFrame(render);
        }}

        requestAnimationFrame(render);
    </script>
    </body>
    </html>
    """
    return html_code
