import random
import flet as ft

# ---------- Theme colors ----------
BG = "#0F172A"          # deep navy background
CARD = "#1E293B"        # card surface
CARD_LIGHT = "#273449"  # lighter card surface
TEXT = "#F8FAFC"
MUTED = "#94A3B8"
ORANGE = "#FB923C"
CYAN = "#22D3EE"
PINK = "#F472B6"
GREEN = "#4ADE80"
YELLOW = "#FACC15"
RED = "#F87171"
PURPLE = "#A78BFA"

# Row colors cycle so the table looks colorful
ROW_COLORS = [ORANGE, CYAN, PINK, GREEN, YELLOW, PURPLE]


def soft_shadow(color: str = "#66000000") -> ft.BoxShadow:
    """Reusable soft elevation shadow for cards and buttons."""
    return ft.BoxShadow(
        spread_radius=0,
        blur_radius=14,
        color=color,
        offset=ft.Offset(0, 5),
    )


def main(page: ft.Page):
    # ---------- Page / window setup (portrait phone-like) ----------
    page.title = "Math Fun"
    page.bgcolor = BG
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = None

    # Window settings only matter on desktop; ignored on Android.
    try:
        page.window.width = 390
        page.window.height = 710
        page.window.min_width = 380
        page.window.max_width = 400
        page.window.min_height = 700
        page.window.max_height = 720
        page.window.resizable = False
        page.window.maximizable = False
        page.window.center()
    except Exception:
        try:
            page.window_width = 390
            page.window_height = 710
            page.window_resizable = False
            page.window_center()
        except Exception:
            pass

    # ---------- App state ----------
    state = {
        "number": 5,        # selected table number (1-20)
        "upto": 10,         # table goes up to x10 or x20
        "mode": "tables",   # "tables" or "practice"
        "quiz_op": None,    # current quiz operation
        "score": 0,
        "streak": 0,
        "asked": 0,
        "answer": None,
        "locked": False,
    }

    # Main swappable body area
    body = ft.Container(expand=True)

    # =====================================================
    # SHARED UI HELPERS
    # =====================================================
    def big_button(label, color, on_click, width=None, height=54, size=20,
                   text_color="#0F172A"):
        """Rounded, colorful, elevated tap button built from a Container."""
        return ft.Container(
            content=ft.Text(label, size=size, weight=ft.FontWeight.W_900,
                            color=text_color, text_align=ft.TextAlign.CENTER),
            bgcolor=color,
            border_radius=18,
            width=width,
            height=height,
            alignment=ft.Alignment(0, 0),
            shadow=soft_shadow(),
            on_click=on_click,
            ink=True,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        )

    # =====================================================
    # HEADER
    # =====================================================
    def build_header():
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("🌟 Math Fun 🌟", size=30,
                            weight=ft.FontWeight.W_900, color=YELLOW,
                            text_align=ft.TextAlign.CENTER),
                    ft.Text("Multiplication Tables & Practice", size=15,
                            weight=ft.FontWeight.BOLD, color=CYAN,
                            text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            bgcolor=CARD,
            border_radius=24,
            padding=ft.Padding(left=16, top=14, right=16, bottom=14),
            margin=ft.Margin(left=12, top=10, right=12, bottom=6),
            alignment=ft.Alignment(0, 0),
            shadow=soft_shadow("#5522D3EE"),
        )

    # =====================================================
    # TABLE VIEWER MODE
    # =====================================================
    def build_tables_view():
        n = state["number"]
        upto = state["upto"]

        # --- Number selector chips (1 to 20), horizontally scrollable ---
        chips = []
        for i in range(1, 21):
            selected = (i == n)
            color = ROW_COLORS[(i - 1) % len(ROW_COLORS)]
            chips.append(
                ft.Container(
                    content=ft.Text(
                        str(i), size=22, weight=ft.FontWeight.W_900,
                        color="#0F172A" if selected else color),
                    width=52, height=52,
                    border_radius=26,
                    bgcolor=color if selected else CARD,
                    alignment=ft.Alignment(0, 0),
                    shadow=soft_shadow(),
                    ink=True,
                    on_click=lambda e, v=i: select_number(v),
                    animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                )
            )
        selector = ft.Row(chips, scroll=ft.ScrollMode.AUTO, spacing=10)

        # --- Range toggle: up to x10 or x20 ---
        def range_btn(val):
            active = state["upto"] == val
            return ft.Container(
                content=ft.Text(f"Up to × {val}", size=15,
                                weight=ft.FontWeight.W_800,
                                color="#0F172A" if active else TEXT),
                bgcolor=PINK if active else CARD,
                border_radius=14,
                padding=ft.Padding(left=16, top=8, right=16, bottom=8),
                ink=True,
                on_click=lambda e, v=val: set_range(v),
            )

        range_row = ft.Row(
            [ft.Text("Show:", size=15, color=MUTED, weight=ft.FontWeight.BOLD),
             range_btn(10), range_btn(20)],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        )

        # --- Table title card ---
        title = ft.Container(
            content=ft.Text(f"Table of {n}", size=28,
                            weight=ft.FontWeight.W_900, color=TEXT),
            alignment=ft.Alignment(0, 0),
            padding=ft.Padding(left=0, top=4, right=0, bottom=4),
        )

        # --- Table rows (tap to highlight) ---
        rows = []
        for k in range(1, upto + 1):
            color = ROW_COLORS[(k - 1) % len(ROW_COLORS)]
            rows.append(make_row(n, k, color))

        table_list = ft.ListView(
            controls=rows, spacing=10, expand=True,
            padding=ft.Padding(left=12, top=4, right=12, bottom=12),
        )

        return ft.Column(
            [
                ft.Container(selector, padding=ft.Padding(left=12, top=6, right=12, bottom=6)),
                range_row,
                title,
                table_list,
            ],
            expand=True,
            spacing=6,
        )

    def make_row(n, k, color):
        """One tappable multiplication row, e.g. '5 × 3 = 15'."""
        result = n * k
        text = ft.Text(f"{n} × {k} = {result}", size=30,
                       weight=ft.FontWeight.W_900, color=color)
        emoji = ft.Text("⭐", size=24, opacity=0)

        card = ft.Container(
            content=ft.Row(
                [text, emoji],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=CARD,
            border_radius=20,
            padding=ft.Padding(left=22, top=14, right=22, bottom=14),
            shadow=soft_shadow(),
            ink=True,
            animate=ft.Animation(250, ft.AnimationCurve.EASE_OUT_BACK),
            animate_scale=ft.Animation(250, ft.AnimationCurve.EASE_OUT_BACK),
        )

        def on_tap(e):
            # Toggle joyful highlight on tap
            active = card.data == "on"
            if active:
                card.data = "off"
                card.bgcolor = CARD
                card.scale = 1.0
                text.color = color
                emoji.opacity = 0
            else:
                card.data = "on"
                card.bgcolor = color
                card.scale = 1.04
                text.color = "#0F172A"
                emoji.opacity = 1
            page.update()

        card.on_click = on_tap
        return card

    def select_number(v):
        state["number"] = v
        render()

    def set_range(v):
        state["upto"] = v
        render()

    # =====================================================
    # QUICK PRACTICE / QUIZ MODE
    # =====================================================
    OPS = {
        "add": ("➕ Addition", "+", GREEN),
        "sub": ("➖ Subtraction", "−", CYAN),
        "mul": ("✖️ Multiplication", "×", ORANGE),
        "div": ("➗ Division", "÷", PINK),
    }

    def build_practice_menu():
        """Menu with four big operation buttons."""
        buttons = []
        for key, (label, _sym, color) in OPS.items():
            buttons.append(
                big_button(label, color,
                           lambda e, k=key: start_quiz(k),
                           width=330, height=70, size=24)
            )
        return ft.Column(
            [
                ft.Container(height=10),
                ft.Text("Choose a Practice!", size=28,
                        weight=ft.FontWeight.W_900, color=YELLOW),
                ft.Text("Pick one and test your skills 🚀", size=15,
                        color=MUTED, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                *buttons,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=18,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

    def make_question(op):
        """Return (question_text, correct_answer) for the given operation."""
        if op == "add":
            a, b = random.randint(1, 20), random.randint(1, 20)
            return f"{a} + {b}", a + b
        if op == "sub":
            a, b = random.randint(1, 20), random.randint(1, 20)
            if b > a:
                a, b = b, a  # keep answers non-negative
            return f"{a} − {b}", a - b
        if op == "mul":
            a, b = random.randint(1, 12), random.randint(1, 12)
            return f"{a} × {b}", a * b
        # Division: build from multiplication so result is a whole number
        b, ans = random.randint(1, 12), random.randint(1, 12)
        return f"{b * ans} ÷ {b}", ans

    def make_options(correct):
        """Correct answer plus 3 unique, plausible wrong answers."""
        opts = {correct}
        guard = 0
        while len(opts) < 4 and guard < 200:
            guard += 1
            wrong = correct + random.choice([-10, -5, -3, -2, -1, 1, 2, 3, 5, 10])
            if wrong >= 0:
                opts.add(wrong)
        opts = list(opts)
        random.shuffle(opts)
        return opts

    def start_quiz(op):
        state["quiz_op"] = op
        state["score"] = 0
        state["streak"] = 0
        state["asked"] = 0
        render()

    def back_to_menu(e=None):
        state["quiz_op"] = None
        render()

    def build_quiz_view():
        op = state["quiz_op"]
        label, _sym, color = OPS[op]
        q_text, answer = make_question(op)
        state["answer"] = answer
        state["locked"] = False

        feedback = ft.Text("What is the answer?", size=18,
                           weight=ft.FontWeight.W_800, color=MUTED,
                           text_align=ft.TextAlign.CENTER)
        score_text = ft.Text(
            f"⭐ Score: {state['score']}   🔥 Streak: {state['streak']}",
            size=16, weight=ft.FontWeight.W_800, color=YELLOW)

        # Next-question button (hidden until answered)
        next_btn = big_button("Next ➡️", YELLOW, lambda e: render(),
                              width=200, height=50, size=20)
        next_btn.visible = False

        option_boxes = []

        def on_pick(e, value, box):
            if state["locked"]:
                return
            state["locked"] = True
            state["asked"] += 1
            if value == state["answer"]:
                state["score"] += 1
                state["streak"] += 1
                box.bgcolor = GREEN
                feedback.value = "🎉 Awesome! Correct!"
                feedback.color = GREEN
            else:
                state["streak"] = 0
                box.bgcolor = RED
                feedback.value = f"😅 Oops! Answer is {state['answer']}"
                feedback.color = RED
                # Reveal the correct option in green
                for b in option_boxes:
                    if b.data == state["answer"]:
                        b.bgcolor = GREEN
            score_text.value = (
                f"⭐ Score: {state['score']}   🔥 Streak: {state['streak']}")
            next_btn.visible = True
            page.update()

        for val in make_options(answer):
            box = ft.Container(
                content=ft.Text(str(val), size=34,
                                weight=ft.FontWeight.W_900,
                                color="#0F172A"),
                data=val,
                bgcolor=color,
                border_radius=20,
                width=150, height=84,
                alignment=ft.Alignment(0, 0),
                shadow=soft_shadow(),
                ink=True,
                animate=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
            )
            box.on_click = lambda e, v=val, b=box: on_pick(e, v, b)
            option_boxes.append(box)

        grid = ft.Column(
            [
                ft.Row(option_boxes[0:2], alignment=ft.MainAxisAlignment.CENTER, spacing=16),
                ft.Row(option_boxes[2:4], alignment=ft.MainAxisAlignment.CENTER, spacing=16),
            ],
            spacing=16,
        )

        question_card = ft.Container(
            content=ft.Text(f"{q_text} = ?", size=46,
                            weight=ft.FontWeight.W_900, color=TEXT,
                            text_align=ft.TextAlign.CENTER),
            bgcolor=CARD,
            border_radius=26,
            width=330, height=130,
            alignment=ft.Alignment(0, 0),
            shadow=soft_shadow("#55" + color[1:]),
        )

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Text("⬅️ Back", size=16,
                                            weight=ft.FontWeight.W_800, color=TEXT),
                            bgcolor=CARD, border_radius=14,
                            padding=ft.Padding(left=14, top=8, right=14, bottom=8),
                            ink=True, on_click=back_to_menu),
                        ft.Text(label, size=18, weight=ft.FontWeight.W_900,
                                color=color),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                score_text,
                question_card,
                feedback,
                grid,
                next_btn,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

    def build_practice_view():
        if state["quiz_op"] is None:
            return build_practice_menu()
        return build_quiz_view()

    # =====================================================
    # BOTTOM NAVIGATION
    # =====================================================
    def build_nav():
        def tab(label, mode, color):
            active = state["mode"] == mode
            return ft.Container(
                content=ft.Text(label, size=17, weight=ft.FontWeight.W_900,
                                color="#0F172A" if active else TEXT),
                bgcolor=color if active else CARD_LIGHT,
                border_radius=18,
                expand=True, height=50,
                alignment=ft.Alignment(0, 0),
                ink=True,
                on_click=lambda e, m=mode: switch_mode(m),
                animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            )

        return ft.Container(
            content=ft.Row(
                [tab("📖 Tables", "tables", ORANGE),
                 tab("🎯 Practice", "practice", CYAN)],
                spacing=10,
            ),
            bgcolor=CARD,
            border_radius=24,
            padding=ft.Padding(left=10, top=8, right=10, bottom=8),
            margin=ft.Margin(left=12, top=6, right=12, bottom=10),
            shadow=soft_shadow(),
        )

    def switch_mode(m):
        state["mode"] = m
        if m == "practice":
            state["quiz_op"] = None
        render()

    # =====================================================
    # MAIN RENDER
    # =====================================================
    def render():
        """Rebuild the body and nav according to current state."""
        if state["mode"] == "tables":
            body.content = build_tables_view()
        else:
            body.content = ft.Container(
                content=build_practice_view(),
                padding=ft.Padding(left=16, top=10, right=16, bottom=10),
                expand=True,
            )
        nav_holder.content = build_nav()
        page.update()

    nav_holder = ft.Container()

    page.add(
        ft.SafeArea(
            content=ft.Column(
                [build_header(), body, nav_holder],
                expand=True,
                spacing=0,
            ),
            expand=True,
        )
    )
    render()


if __name__ == "__main__":
    ft.app(target=main)
