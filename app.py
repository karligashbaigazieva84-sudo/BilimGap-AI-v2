import os
import re
import html
import gradio as gr


# =========================================================
# BilimGap AI
# 5-сынып | БЖБ №1
# =========================================================

BZHB = {
    "section": "Ақпарат және компьютер",
    "max_score": 12,

    "goals": {
        "5.4.1.1": "Эргономика",
        "5.2.1.1": "Ақпарат түрлері",
        "5.3.3.1": "Интернетте ақпарат іздеу",
        "5.1.1.1": "Есептеу техникасының даму тарихы",
        "5.1.1.2": "Программалық жасақтама және ЖИ"
    },

    "questions": [
        {
            "id": 1,
            "goal": "5.4.1.1",
            "text": (
                "Айдос экранға өте жақын отырды және бөлмедегі жарық "
                "жеткіліксіз болды. Екі қатені анықтап, дұрыс әрекетті жазыңыз."
            ),
            "keywords": [
                "қашықтық",
                "алыс",
                "жарық",
                "жарықтандыру"
            ],
            "min_keywords": 2,
            "score": 2
        },

        {
            "id": 2,
            "goal": "5.2.1.1",
            "text": (
                "Мақала, фотосурет, ән, бейнероликтің ақпарат түрлерін "
                "және компьютерде ақпарат қандай кодпен сақталатынын жазыңыз."
            ),
            "keywords": [
                "мәтіндік",
                "графикалық",
                "дыбыстық",
                "бейне",
                "екілік"
            ],
            "min_keywords": 4,
            "score": 2
        },

        {
            "id": 3,
            "goal": "5.3.3.1",
            "text": (
                "«Қазақстандағы есептеу техникасының даму тарихы» туралы "
                "тиімді іздеу сұранысын жазыңыз және таңдауыңызды түсіндіріңіз."
            ),
            "keywords": [
                "қазақстан",
                "есептеу",
                "техника",
                "тарих",
                "нақты"
            ],
            "min_keywords": 2,
            "score": 2
        },

        {
            "id": 4,
            "goal": "5.1.1.1",
            "text": (
                "Реттеңіз: A — заманауи дербес компьютерлер, "
                "B — қарапайым есептеу құралдары, "
                "C — электрондық есептеу машиналары, "
                "D — механикалық есептеу құрылғылары. "
                "Болашақ компьютердің бір мүмкіндігін атаңыз."
            ),
            "keywords": [
                "b-d-c-a",
                "b d c a",
                "жасанды интеллект",
                "жылдам",
                "ақылды"
            ],
            "min_keywords": 1,
            "score": 2
        },

        {
            "id": 5,
            "goal": "5.1.1.2",
            "text": (
                "Windows, Microsoft Word және Python IDLE программаларын "
                "түрлері бойынша жіктеңіз."
            ),
            "keywords": [
                "жүйелік",
                "қолданбалы",
                "инструменталды"
            ],
            "min_keywords": 3,
            "score": 2
        },

        {
            "id": 6,
            "goal": "5.1.1.2",
            "text": (
                "Жасанды интеллект қолданылатын бір программаны атаңыз "
                "және ЖИ қандай қызмет атқаратынын түсіндіріңіз."
            ),
            "keywords": [
                "жасанды интеллект",
                "жи",
                "тану",
                "ұсыну",
                "жауап",
                "болжау"
            ],
            "min_keywords": 2,
            "score": 2
        }
    ]
}


CORRECTION_TASKS = {
    "5.4.1.1": {
        "task": "Компьютермен жұмыс істеудің 3 қауіпсіздік ережесін жазыңыз.",
        "tip": "Дұрыс отыру, экран қашықтығы және жарықты еске түсіріңіз."
    },

    "5.2.1.1": {
        "task": (
            "Подкаст, электрондық кітап, сурет және бейнесабақтың "
            "ақпарат түрін анықтаңыз."
        ),
        "tip": (
            "Мәтіндік, графикалық, дыбыстық және бейне "
            "түрлерін қайталаңыз."
        )
    },

    "5.3.3.1": {
        "task": (
            "«Қазақстандағы алғашқы компьютерлер» тақырыбына "
            "тиімді іздеу сұранысын құрыңыз."
        ),
        "tip": "Нақты кілт сөздерді таңдаңыз."
    },

    "5.1.1.1": {
        "task": (
            "Есепшот, механикалық машина, электрондық компьютер, "
            "заманауи компьютерді даму ретімен орналастырыңыз."
        ),
        "tip": "Есептеу техникасының даму кезеңдерін қайталаңыз."
    },

    "5.1.1.2": {
        "task": (
            "Жүйелік, қолданбалы және инструменталды программаларға "
            "бір-бір мысал келтіріп, ЖИ қолданылатын бір программаны атаңыз."
        ),
        "tip": "Программалық жасақтама түрлерін қайталаңыз."
    }
}


# =========================================================
# Мәтінді қалыпқа келтіру
# =========================================================

def normalize_text(value):
    value = str(value or "").lower().strip()

    value = (
        value
        .replace("–", "-")
        .replace("—", "-")
        .replace("_", " ")
    )

    value = re.sub(r"\s+", " ", value)

    return value


# =========================================================
# Бір тапсырманы автоматты тексеру
# =========================================================

def check_question(question, answer):
    text = normalize_text(answer)

    if not text:
        return 0

    keywords = question.get("keywords", [])

    found = 0

    for keyword in keywords:
        if normalize_text(keyword) in text:
            found += 1

    minimum = question.get("min_keywords", 1)

    if found >= minimum:
        return question["score"]

    return 0


# =========================================================
# Мәртебе
# =========================================================

def status_from_percent(percent):
    if percent >= 80:
        return "green", "🟢", "Меңгерілген"

    if percent >= 50:
        return "yellow", "🟡", "Бекіту қажет"

    return "red", "🔴", "Олқылық анықталды"


# =========================================================
# Білім картасының карточкасы
# =========================================================

def status_card(goal, goal_name, percent):
    color, icon, status = status_from_percent(percent)

    styles = {
        "green": (
            "#eafaf1",
            "#22c55e",
            "#087a3e"
        ),

        "yellow": (
            "#fffbea",
            "#f4b400",
            "#9a6700"
        ),

        "red": (
            "#fff0f0",
            "#ef4444",
            "#b91c1c"
        )
    }

    bg, border, text_color = styles[color]

    return f"""
    <div style="
        background:{bg};
        border-left:10px solid {border};
        padding:16px;
        margin:12px 0;
        border-radius:12px;
    ">

        <div style="font-size:28px;">
            {icon}
        </div>

        <b>
            {html.escape(goal)}
            —
            {html.escape(goal_name)}
        </b>

        <br>

        <span style="
            font-size:21px;
            color:{text_color};
            font-weight:700;
        ">
            {percent}% — {status}
        </span>

    </div>
    """


# =========================================================
# Негізгі тексеру
# =========================================================

def check_bzhb(
    student_name,
    answer1,
    answer2,
    answer3,
    answer4,
    answer5,
    answer6
):

    if not str(student_name).strip():
        return """
        <div style="
            background:#fff3cd;
            padding:16px;
            border-radius:12px;
        ">
            ⚠️ Оқушының аты-жөнін енгізіңіз.
        </div>
        """

    answers = [
        answer1,
        answer2,
        answer3,
        answer4,
        answer5,
        answer6
    ]

    total_score = 0

    goal_scores = {}

    for goal in BZHB["goals"]:
        goal_scores[goal] = {
            "score": 0,
            "max": 0
        }

    # Әр тапсырманы тексеру
    for question, answer in zip(
        BZHB["questions"],
        answers
    ):

        score = check_question(
            question,
            answer
        )

        total_score += score

        goal = question["goal"]

        goal_scores[goal]["score"] += score
        goal_scores[goal]["max"] += question["score"]

    # Жалпы пайыз
    total_percent = round(
        total_score /
        BZHB["max_score"] *
        100
    )

    overall_color, overall_icon, overall_status = (
        status_from_percent(total_percent)
    )

    result_html = f"""
    <div style="
        padding:20px;
        border-radius:16px;
        background:#f8fafc;
        margin-bottom:20px;
    ">

        <h2>📊 БЖБ НӘТИЖЕСІ</h2>

        <b>Оқушы:</b>
        {html.escape(str(student_name))}
        <br>

        <b>Сынып:</b> 5
        <br>

        <b>БЖБ:</b>
        №1 — Ақпарат және компьютер
        <br><br>

        <span style="font-size:25px;">
            <b>
                {total_score} / 12 балл
                — {total_percent}%
            </b>
        </span>

        <br><br>

        <span style="font-size:22px;">
            {overall_icon}
            <b>{overall_status}</b>
        </span>

    </div>

    <h2>
        🧠 ЦИФРЛЫҚ БІЛІМ КАРТАСЫ
    </h2>
    """

    correction_html = ""

    # Әр оқу мақсаты жеке есептеледі
    for goal, goal_name in BZHB["goals"].items():

        earned = goal_scores[goal]["score"]
        maximum = goal_scores[goal]["max"]

        if maximum > 0:
            percent = round(
                earned /
                maximum *
                100
            )
        else:
            percent = 0

        result_html += status_card(
            goal,
            goal_name,
            percent
        )

        # Тек жасыл емес мақсаттарға түзету тапсырмасы
        if percent < 80:

            correction = CORRECTION_TASKS.get(goal)

            if correction:

                _, icon, status = (
                    status_from_percent(percent)
                )

                correction_html += f"""
                <div style="
                    background:#f8fafc;
                    border:1px solid #e5e7eb;
                    padding:16px;
                    margin:12px 0;
                    border-radius:12px;
                ">

                    <b>
                        {icon}
                        {html.escape(goal)}
                        —
                        {status}
                    </b>

                    <br><br>

                    <b>✍️ Түзету тапсырмасы:</b>
                    <br>

                    {html.escape(correction["task"])}

                    <br><br>

                    <b>💡 Кеңес:</b>
                    <br>

                    {html.escape(correction["tip"])}

                </div>
                """

    if correction_html:

        result_html += """
        <br>
        <h2>
            🎯 ЖЕКЕ ТҮЗЕТУ ТАПСЫРМАЛАРЫ
        </h2>
        """

        result_html += correction_html

    else:

        result_html += """
        <div style="
            background:#eafaf1;
            border-left:10px solid #22c55e;
            padding:16px;
            margin-top:20px;
            border-radius:12px;
        ">
            🎉 Барлық оқу мақсаттары меңгерілген.
        </div>
        """

    return result_html


# =========================================================
# Интерфейс
# =========================================================

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

.question-box {
    border:1px solid #e5e7eb;
    border-radius:14px;
    padding:10px;
    margin-bottom:10px;
}
"""


with gr.Blocks(
    title="BilimGap AI",
    css=CSS
) as app:

    gr.HTML("""
    <div class="title">

        <h1>
            🧠 BilimGap AI
        </h1>

        <h2>
            Білім олқылықтарын анықтау
            және түзету жүйесі
        </h2>

        <p>
            5–9 сынып |
            Информатика және жасанды интеллект
        </p>

    </div>
    """)

    with gr.Tab("👨‍🎓 ОҚУШЫ"):

        gr.Markdown(
            """
            ## 📝 БЖБ орындау

            **Сынып:** 5

            **БЖБ №1:** Ақпарат және компьютер

            **Максималды балл:** 12
            """
        )

        student_name = gr.Textbox(
            label="👤 Оқушының аты-жөні",
            placeholder="Мысалы: Арнұр"
        )

        gr.Markdown(
            "### 1-тапсырма — Эргономика"
        )

        gr.Markdown(
            BZHB["questions"][0]["text"]
        )

        answer1 = gr.Textbox(
            label="Жауап",
            lines=3
        )

        gr.Markdown(
            "### 2-тапсырма — Ақпарат түрлері"
        )

        gr.Markdown(
            BZHB["questions"][1]["text"]
        )

        answer2 = gr.Textbox(
            label="Жауап",
            lines=3
        )

        gr.Markdown(
            "### 3-тапсырма — Интернетте ақпарат іздеу"
        )

        gr.Markdown(
            BZHB["questions"][2]["text"]
        )

        answer3 = gr.Textbox(
            label="Жауап",
            lines=3
        )

        gr.Markdown(
            "### 4-тапсырма — Есептеу техникасының даму тарихы"
        )

        gr.Markdown(
            BZHB["questions"][3]["text"]
        )

        answer4 = gr.Textbox(
            label="Жауап",
            lines=3
        )

        gr.Markdown(
            "### 5-тапсырма — Программалық жасақтама"
        )

        gr.Markdown(
            BZHB["questions"][4]["text"]
        )

        answer5 = gr.Textbox(
            label="Жауап",
            lines=3
        )

        gr.Markdown(
            "### 6-тапсырма — Жасанды интеллект"
        )

        gr.Markdown(
            BZHB["questions"][5]["text"]
        )

        answer6 = gr.Textbox(
            label="Жауап",
            lines=3
        )

        check_button = gr.Button(
            "🧠 БЖБ-ны тексеру",
            elem_classes="orange-btn"
        )

        result = gr.HTML()

        check_button.click(
            fn=check_bzhb,
            inputs=[
                student_name,
                answer1,
                answer2,
                answer3,
                answer4,
                answer5,
                answer6
            ],
            outputs=result
        )

    with gr.Tab("👩‍🏫 МҰҒАЛІМ"):

        gr.Markdown(
            """
            # 👩‍🏫 Мұғалімнің талдау панелі

            Бұл бөлім келесі кезеңде
            барлық оқушылардың нәтижелерін
            жинақтап көрсетеді.

            ### Бағалау шектері

            🟢 **80–100% — Меңгерілген**

            🟡 **50–79% — Бекіту қажет**

            🔴 **0–49% — Олқылық анықталды**
            """
        )

    with gr.Tab("ℹ️ ЖОБА ТУРАЛЫ"):

        gr.Markdown(
            """
            # 💡 BilimGap AI

            **Мақсаты:** БЖБ нәтижелерін автоматты
            тексеру, оқу мақсаттары бойынша білім
            олқылықтарын анықтау және оқушыға
            жеке түзету тапсырмаларын ұсыну.

            Жүйе 5–9 сынып информатика пәніне
            арналған.
            """
        )


# =========================================================
# Render іске қосу
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            7860
        )
    )

    app.launch(
        server_name="0.0.0.0",
        server_port=port
    )
# BilimGap AI v2 жаңартылды
