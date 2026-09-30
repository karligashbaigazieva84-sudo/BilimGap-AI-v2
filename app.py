import os
import gradio as gr
import pandas as pd
from datetime import datetime

RESULT_FILE = "student_results.csv"


def status_from_percent(percent):
    """Пайызға сәйкес тұрақты мәртебе."""
    if percent >= 80:
        return "green", "🟢", "Меңгерілген"
    elif percent >= 50:
        return "yellow", "🟡", "Бекіту қажет"
    else:
        return "red", "🔴", "Олқылық анықталды"


def status_card(goal, goal_name, percent):
    color, icon, status = status_from_percent(percent)

    styles = {
        "green": ("#eafaf1", "#22c55e", "#087a3e"),
        "yellow": ("#fffbea", "#f4b400", "#9a6700"),
        "red": ("#fff0f0", "#ef4444", "#b91c1c"),
    }

    bg, border, text = styles[color]

    return f"""
    <div style="
        background:{bg};
        border-left:10px solid {border};
        padding:16px;
        margin:12px 0;
        border-radius:12px;
    ">
        <div style="font-size:26px;">{icon}</div>
        <b>{goal} — {goal_name}</b><br>
        <span style="font-size:22px;color:{text};">
            {percent}% — {status}
        </span>
    </div>
    """


def demo_check(name, score):
    """
    Алдымен түстердің дұрыс жұмыс істейтінін тексеретін
    уақытша тест функциясы.
    """
    if not str(name).strip():
        return """
        <div style="padding:15px;background:#fff3cd;border-radius:12px;">
        ⚠️ Оқушының аты-жөнін енгізіңіз.
        </div>
        """

    try:
        percent = int(score)
    except (TypeError, ValueError):
        percent = 0

    percent = max(0, min(100, percent))

    html = f"""
    <div style="
        padding:20px;
        border-radius:16px;
        background:#f8fafc;
        margin-bottom:18px;
    ">
        <h2>📊 БЖБ НӘТИЖЕСІ</h2>
        <b>Оқушы:</b> {name}<br>
        <b>Нәтиже:</b> {percent}%
    </div>

    <h2>🧠 ЦИФРЛЫҚ БІЛІМ КАРТАСЫ</h2>
    """

    # Уақытша бір оқу мақсаты арқылы түсті тексереміз
    html += status_card(
        "5.4.1.1",
        "Эргономика",
        percent
    )

    return html


CSS = """
.gradio-container {
    max-width: 1100px !important;
    margin: auto !important;
}

.title {
    text-align:center;
    margin-bottom:25px;
}

.orange-btn {
    background:#ff7417 !important;
    color:white !important;
    font-weight:bold !important;
    border-radius:12px !important;
}
"""


with gr.Blocks(title="BilimGap AI", css=CSS) as app:

    gr.HTML("""
    <div class="title">
        <h1>🧠 BilimGap AI</h1>
        <h2>Білім олқылықтарын анықтау және түзету жүйесі</h2>
        <p>5–9 сынып | Информатика және жасанды интеллект</p>
    </div>
    """)

    with gr.Tab("👨‍🎓 ОҚУШЫ"):

        gr.Markdown("## 📝 БЖБ орындау")

        name = gr.Textbox(
            label="👤 Оқушының аты-жөні",
            placeholder="Мысалы: Аружан"
        )

        score = gr.Slider(
            minimum=0,
            maximum=100,
            value=40,
            step=1,
            label="Уақытша тест нәтижесі (%)"
        )

        check_btn = gr.Button(
            "🧠 Нәтижені тексеру",
            elem_classes="orange-btn"
        )

        output = gr.HTML()

        check_btn.click(
            fn=demo_check,
            inputs=[name, score],
            outputs=output
        )

    with gr.Tab("👩‍🏫 МҰҒАЛІМ"):
        gr.Markdown("""
        # 👩‍🏫 Мұғалімнің талдау панелі

        Бұл бөлімге келесі кезеңде Colab-тағы
        БЖБ нәтижелері мен талдау жүйесі қосылады.

        **Топтардың түсі енді K-means кластерінің реттік
        нөмірімен емес, нақты пайызбен анықталады:**

        🟢 80–100% — Меңгерілген  
        🟡 50–79% — Бекіту қажет  
        🔴 0–49% — Олқылық анықталды
        """)

    with gr.Tab("ℹ️ ЖОБА ТУРАЛЫ"):
        gr.Markdown("""
        # 💡 BilimGap AI

        **Мақсаты:** БЖБ нәтижелерін автоматты тексеру,
        оқу мақсаттары бойынша білім олқылықтарын анықтау
        және түзету жұмыстарын ұсыну.
        """)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))

    app.launch(
        server_name="0.0.0.0",
        server_port=port
    )
