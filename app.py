import os
import re
import gradio as gr

# =========================================================
# BILIMGAP AI v2
# 5-СЫНЫП: БЖБ №1 + БЖБ №2
# =========================================================

BZHBS = {
    "БЖБ №1": {
        "section": "Ақпарат және компьютер",
        "max_score": 12,
        "goals": {
            "5.4.1.1": "Эргономика",
            "5.2.1.1": "Ақпарат түрлері",
            "5.3.3.1": "Интернетте ақпарат іздеу",
            "5.1.1.1": "Есептеу техникасының даму тарихы",
            "5.1.1.2": "Программалық жасақтама және ЖИ",
        },
        "questions": [
            {
                "id": 1,
                "goal": "5.4.1.1",
                "text": "Компьютермен жұмыс істеу кезінде денсаулықты сақтаудың екі ережесін жазыңыз.",
                "keywords": ["қашықтық", "жарық", "дұрыс отыру", "үзіліс", "экран"],
                "score": 2,
            },
            {
                "id": 2,
                "goal": "5.2.1.1",
                "text": "Мақала, фотосурет, ән және бейнеролик қандай ақпарат түрлеріне жатады? Компьютерде ақпарат қалай сақталады?",
                "keywords": ["мәтін", "графикалық", "дыбыстық", "бейне", "екілік"],
                "score": 2,
            },
            {
                "id": 3,
                "goal": "5.3.3.1",
                "text": "Қазақстандағы есептеу техникасының даму тарихы туралы ақпарат іздеу үшін тиімді іздеу сұранысын жазыңыз.",
                "keywords": ["қазақстан", "есептеу", "техника", "тарих"],
                "score": 2,
            },
            {
                "id": 4,
                "goal": "5.1.1.1",
                "text": "Есептеу техникасының даму кезеңдерін ретімен көрсетіп, болашақ компьютерлердің бір мүмкіндігін жазыңыз.",
                "keywords": ["b-d-c-a", "жасанды интеллект", "жи"],
                "score": 2,
            },
            {
                "id": 5,
                "goal": "5.1.1.2",
                "text": "Windows, Microsoft Word және Python IDLE программаларын программалық жасақтама түрлеріне жіктеңіз.",
                "keywords": ["windows", "жүйелік", "word", "қолданбалы", "python", "инструменталды"],
                "score": 2,
            },
            {
                "id": 6,
                "goal": "5.1.1.2",
                "text": "Жасанды интеллект қолданылатын бір программаны атаңыз және оның не істейтінін түсіндіріңіз.",
                "keywords": ["chatgpt", "жасанды интеллект", "жи", "жауап", "ақпарат"],
                "score": 2,
            },
        ],
    },

    "БЖБ №2": {
        "section": "Цифрлық кескіндер",
        "max_score": 12,
        "goals": {
            "5.2.2.1": "Растрлық және векторлық графика, RGB/CMYK",
            "5.2.2.3": "Растрлық кескіндерді құру",
            "5.2.2.2": "Растрлық кескіндерді өңдеу",
            "5.3.3.2": "Кіріс деректердің цифрлық жүйе нәтижесіне әсері",
        },
        "questions": [
            {
                "id": 1,
                "goal": "5.2.2.1",
                "text": "Фотосурет үшін қай графика тиімді?",
                "answer": "растрлық",
                "score": 1,
            },
            {
                "id": 2,
                "goal": "5.2.2.1",
                "text": "Экрандағы кескін үшін қай түстік модель қолданылады?",
                "answer": "rgb",
                "score": 1,
            },
            {
                "id": 3,
                "goal": "5.2.2.3",
                "text": "Растрлық редакторда кескін құруға қолданылатын екі нысанды атаңыз.",
                "keywords": ["тіктөртбұрыш", "шеңбер", "эллипс", "сызық", "көпбұрыш", "мәтін"],
                "score": 2,
            },
            {
                "id": 4,
                "goal": "5.2.2.2",
                "text": "Растрлық кескінді өңдеудің екі әрекетін атаңыз.",
                "keywords": ["ерекшелеу", "жылжыту", "кадрлау", "қабат"],
                "score": 2,
            },
            {
                "id": 5,
                "goal": "5.3.3.2",
                "text": "ЖИ-ға нақты әрі толық кіріс дерегін беру неге маңызды?",
                "keywords": ["нақты", "толық", "нәтиже", "сапа", "дұрыс"],
                "score": 3,
            },
            {
                "id": 6,
                "goal": "5.3.3.2",
                "text": "«Табиғат суретін жаса» сұранысын нақтылап жазыңыз.",
                "keywords": ["тау", "орман", "көл", "күн", "аспан", "табиғат"],
                "score": 3,
            },
        ],
    },
}

CORRECTIONS = {
    "5.4.1.1": "Компьютермен қауіпсіз жұмыс істеудің 3 ережесін жазыңыз.",
    "5.2.1.1": "Мәтіндік, графикалық, дыбыстық және бейне ақпаратқа бір-бірден мысал келтіріңіз.",
    "5.3.3.1": "Интернеттен нақты ақпарат табуға арналған 2 тиімді іздеу сұранысын құрыңыз.",
    "5.1.1.1": "Есептеу техникасының даму кезеңдерін ретімен жазыңыз.",
    "5.1.1.2": "Жүйелік, қолданбалы программалар мен ЖИ құралдарына мысал келтіріңіз.",

    "5.2.2.1": "Растрлық және векторлық графиканың 2 айырмашылығын жазыңыз.",
    "5.2.2.2": "Растрлық кескінді өңдеудің 3 әрекетін атаңыз.",
    "5.2.2.3": "Растрлық редакторда сурет құруға қолданылатын 3 құралды атаңыз.",
    "5.3.3.2": "ЖИ-ға «Мектеп туралы сурет жаса» сұранысын нақты әрі толық етіп қайта жазыңыз.",
}


def normalize(text):
    text = str(text or "").lower().strip()
    text = text.replace("ё", "е")
    text = re.sub(r"\s+", " ", text)
    return text


def score_question(question, answer):
    answer = normalize(answer)

    if not answer:
        return 0

    max_score = question["score"]

    if "answer" in question:
        correct = normalize(question["answer"])

        if correct in answer:
            return max_score

        return 0

    keywords = [normalize(x) for x in question.get("keywords", [])]
    found = sum(1 for keyword in keywords if keyword in answer)

    if found == 0:
        return 0

    # 1 балдық сұрақ
    if max_score == 1:
        return 1

    # 2 балдық сұрақ: кемінде екі негізгі белгі
    if max_score == 2:
        return 2 if found >= 2 else 1

    # 3 балдық сұрақ
    if max_score == 3:
        if found >= 3:
            return 3
        elif found == 2:
            return 2
        else:
            return 1

    return min(found, max_score)


def get_bzhb_info(bzhb_name):
    data = BZHBS[bzhb_name]

    info = f"""
## 📘 5-сынып — {bzhb_name}

### {data['section']}

**Максималды балл:** {data['max_score']}

### 🎯 Оқу мақсаттары
"""

    for code, title in data["goals"].items():
        info += f"- **{code}** — {title}\n"

    questions = [
        gr.update(
           label=f"{q['id']}-тапсырма — {q['score']} балл | {q['text']}",
            placeholder=q["text"],
            visible=True,
            value=""
        )
        for q in data["questions"]
    ]

    return [info] + questions + [gr.update(value="", visible=False)]


def check_bzhb(name, bzhb_name, *answers):
    data = BZHBS[bzhb_name]

    total = 0
    goal_scores = {}
    goal_max = {}

    for question, answer in zip(data["questions"], answers):
        earned = score_question(question, answer)
        total += earned

        goal = question["goal"]
        goal_scores[goal] = goal_scores.get(goal, 0) + earned
        goal_max[goal] = goal_max.get(goal, 0) + question["score"]

    percentage = round(total / data["max_score"] * 100)

    if percentage >= 80:
        overall = "🟢 Меңгерілген"
    elif percentage >= 50:
        overall = "🟡 Бекіту қажет"
    else:
        overall = "🔴 Олқылық анықталды"

    student = name.strip() if name and name.strip() else "Оқушы"

    result = f"""
# 🧠 Цифрлық білім картасы

**Оқушы:** {student}  
**Сынып:** 5-сынып  
**БЖБ:** {bzhb_name} — {data['section']}

## 📊 Жалпы нәтиже

### {total}/{data['max_score']} балл — {percentage}%

### {overall}

---

## 🎯 Оқу мақсаттары бойынша нәтиже
"""

    weak_goals = []

    for goal, title in data["goals"].items():
        earned = goal_scores.get(goal, 0)
        maximum = goal_max.get(goal, 0)

        if maximum == 0:
            goal_percent = 0
        else:
            goal_percent = round(earned / maximum * 100)

        if goal_percent >= 80:
            status = "🟢 Меңгерілген"
        elif goal_percent >= 50:
            status = "🟡 Бекіту қажет"
            weak_goals.append(goal)
        else:
            status = "🔴 Олқылық анықталды"
            weak_goals.append(goal)

        result += (
            f"\n### {status}\n"
            f"**{goal} — {title}**  \n"
            f"{earned}/{maximum} балл — {goal_percent}%\n"
        )

    result += "\n---\n"

    if weak_goals:
        result += "\n## 🎯 Жеке түзету тапсырмалары\n"

        for number, goal in enumerate(weak_goals, 1):
            title = data["goals"].get(goal, "")
            task = CORRECTIONS.get(
                goal,
                "Осы оқу мақсаты бойынша қосымша жаттығу орындаңыз."
            )

            result += f"""
### {number}. {goal} — {title}

**✏️ Түзету тапсырмасы:**  
{task}

"""
    else:
        result += """
## 🌟 Қосымша түзету жұмысы қажет емес

Барлық бағаланған оқу мақсаттары жеткілікті деңгейде меңгерілген.
"""

    return gr.update(value=result, visible=True)


CSS = """
.gradio-container {
    max-width: 1050px !important;
    margin: auto !important;
}
#title {
    text-align: center;
    padding: 18px;
}
"""


with gr.Blocks(css=CSS, title="BilimGap AI") as app:

    gr.Markdown(
        """
# 🧠 BilimGap AI
### БЖБ нәтижесі арқылы білім олқылығын автоматты анықтау

**5–9 сынып информатика пәніне арналған интеллектуалды білім картасы**
""",
        elem_id="title"
    )

    with gr.Tab("👨‍🎓 ОҚУШЫ"):

        gr.Markdown("## 📝 БЖБ орындау")

        name = gr.Textbox(
            label="Оқушының аты-жөні",
            placeholder="Мысалы: Арнұр"
        )

        grade = gr.Dropdown(
            choices=["5-сынып"],
            value="5-сынып",
            label="Сынып"
        )

        bzhb = gr.Dropdown(
            choices=["БЖБ №1", "БЖБ №2"],
            value="БЖБ №1",
            label="БЖБ таңдаңыз"
        )

        info = gr.Markdown()

        answer_boxes = []

        for i in range(6):
            box = gr.Textbox(
                label=f"{i+1}-тапсырма",
                lines=3
            )
            answer_boxes.append(box)

        check_button = gr.Button(
            "🧠 БЖБ-ны тексеру",
            variant="primary"
        )

        result = gr.Markdown(visible=False)

        bzhb.change(
            fn=get_bzhb_info,
            inputs=bzhb,
            outputs=[info] + answer_boxes + [result]
        )

        app.load(
            fn=get_bzhb_info,
            inputs=bzhb,
            outputs=[info] + answer_boxes + [result]
        )

        check_button.click(
            fn=check_bzhb,
            inputs=[name, bzhb] + answer_boxes,
            outputs=result
        )

    with gr.Tab("🗺️ ЦИФРЛЫҚ БІЛІМ КАРТАСЫ"):
        gr.Markdown(
            """
## 🗺️ Цифрлық білім картасы

Оқушы БЖБ тапсырмаларын орындағаннан кейін жүйе:

- жалпы балл мен пайызды есептейді;
- әр оқу мақсатын жеке талдайды;
- 🟢 **Меңгерілген**
- 🟡 **Бекіту қажет**
- 🔴 **Олқылық анықталды**
- қажет оқу мақсаттарына жеке түзету тапсырмасын ұсынады.
"""
        )

    with gr.Tab("👩‍🏫 МҰҒАЛІМ КАБИНЕТІ"):
        gr.Markdown(
            """
## 👩‍🏫 Мұғалім кабинеті

Келесі кезеңде бұл бөлімге:

**сынып нәтижелері → оқу мақсаты бойынша олқылықтар → түзету топтары → Excel есебі**

қосылады.
"""
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))

    app.launch(
        server_name="0.0.0.0",
        server_port=port
    )
