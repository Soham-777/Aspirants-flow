"""
main.py — AspirantFlow Entry Point & UI
========================================
Routing logic:
  app() starts Flet.
  Router class holds the current user session and switches views.
  Each section is a build_*_view() function that returns a flet.View.

Data flow per section:
  1. View renders using db.get_*() calls.
  2. User interacts (button/field) → handler calls db.upsert/add/toggle/delete.
  3. Handler calls page.update() or navigates to refresh.
"""

import flet as ft
from datetime import date, datetime
from database import DatabaseManager
import auth as auth_module

db = DatabaseManager()

# ── Palette ──────────────────────────────────────────────────────────────────
BG         = "#0D1117"   # near-black background
SURFACE    = "#161B22"   # card surfaces
SURFACE2   = "#1C2333"   # elevated surface
BORDER     = "#30363D"   # subtle borders
ACCENT     = "#58A6FF"   # primary accent (bright blue)
ACCENT2    = "#3FB950"   # green (Biology / success)
ACCENT3    = "#F78166"   # red-orange (Physics / danger)
ACCENT4    = "#D2A8FF"   # purple (Chemistry)
ACCENT5    = "#FFA657"   # amber (warnings / Medium priority)
TEXT       = "#E6EDF3"   # primary text
TEXT_DIM   = "#8B949E"   # secondary / dim text
HIGH_CLR   = "#F85149"
MED_CLR    = "#FFA657"
LOW_CLR    = "#3FB950"

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SUBJECTS = ["Physics", "Chemistry", "Biology"]
SUBJECT_COLORS = {"Physics": ACCENT3, "Chemistry": ACCENT4, "Biology": ACCENT2}

DEFAULT_SLOTS = [
    ("5:00 AM", "Wake-up / Exercise"),
    ("6:00 AM", "Physics"),
    ("8:00 AM", "Breakfast / Break"),
    ("8:30 AM", "Chemistry"),
    ("10:30 AM", "Break"),
    ("11:00 AM", "Biology"),
    ("1:00 PM", "Lunch / Rest"),
    ("2:00 PM", "Revision / PYQs"),
    ("4:00 PM", "Mock Test / Practice"),
    ("6:00 PM", "Break / Walk"),
    ("7:00 PM", "Weak Topic Deep-Dive"),
    ("9:00 PM", "Dinner"),
    ("9:30 PM", "Flashcard Review"),
    ("10:30 PM", "Sleep"),
]

# ── Reusable UI helpers ───────────────────────────────────────────────────────

def card(content, padding=16, radius=12):
    return ft.Container(
        content=content,
        bgcolor=SURFACE,
        border_radius=radius,
        padding=padding,
        border=ft.border.all(1, BORDER),
    )

def section_title(text: str, icon=None):
    items = []
    if icon:
        items.append(ft.Icon(icon, color=ACCENT, size=20))
    items.append(ft.Text(text, size=18, weight=ft.FontWeight.BOLD, color=TEXT))
    return ft.Row(items, spacing=8)

def chip_priority(priority: str):
    colors = {"High": HIGH_CLR, "Medium": MED_CLR, "Low": LOW_CLR}
    return ft.Container(
        content=ft.Text(priority, size=11, color="#000000", weight=ft.FontWeight.BOLD),
        bgcolor=colors.get(priority, BORDER),
        border_radius=20,
        padding=ft.padding.symmetric(horizontal=10, vertical=3),
    )

def snack(page: ft.Page, msg: str, color=ACCENT2):
    page.snack_bar = ft.SnackBar(
        ft.Text(msg, color="#000000"),
        bgcolor=color,
        duration=2500,
    )
    page.snack_bar.open = True
    page.update()

def label_field(label: str, field: ft.Control):
    return ft.Column([ft.Text(label, size=12, color=TEXT_DIM), field], spacing=4)

def styled_field(hint: str, value: str = "", multiline=False,
                 min_lines=1, max_lines=1, expand=False, password=False):
    return ft.TextField(
        hint_text=hint,
        value=value,
        multiline=multiline,
        min_lines=min_lines,
        max_lines=max_lines,
        expand=expand,
        password=password,
        bgcolor=SURFACE2,
        border_color=BORDER,
        focused_border_color=ACCENT,
        color=TEXT,
        hint_style=ft.TextStyle(color=TEXT_DIM),
        text_size=14,
        border_radius=8,
    )

def primary_btn(text: str, on_click, icon=None, color=ACCENT):
    return ft.ElevatedButton(
        text,
        icon=icon,
        on_click=on_click,
        style=ft.ButtonStyle(
            bgcolor=color,
            color="#000000",
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
        ),
    )

# ── Auth Views ────────────────────────────────────────────────────────────────

def build_login_view(page: ft.Page, on_login):
    username_f = styled_field("Username")
    password_f = styled_field("Password", password=True)
    err_text   = ft.Text("", color=HIGH_CLR, size=13)

    def do_login(e):
        user, msg = auth_module.login(username_f.value, password_f.value)
        if user:
            on_login(user)
        else:
            err_text.value = msg
            page.update()

    def go_signup(e):
        page.go("/signup")

    return ft.View(
        "/login",
        bgcolor=BG,
        controls=[
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.LOCAL_HOSPITAL_ROUNDED, size=56, color=ACCENT),
                        ft.Text("AspirantFlow", size=32, weight=ft.FontWeight.BOLD, color=TEXT),
                        ft.Text("Your NEET productivity companion", size=14, color=TEXT_DIM),
                        ft.Divider(height=20, color="transparent"),
                        card(
                            ft.Column(
                                [
                                    ft.Text("Sign In", size=20, weight=ft.FontWeight.BOLD, color=TEXT),
                                    ft.Divider(height=8, color="transparent"),
                                    label_field("Username", username_f),
                                    label_field("Password", password_f),
                                    err_text,
                                    ft.Divider(height=4, color="transparent"),
                                    primary_btn("Login", do_login, ft.Icons.LOGIN),
                                    ft.Row([
                                        ft.Text("New here?", color=TEXT_DIM, size=13),
                                        ft.TextButton("Create account", on_click=go_signup,
                                                      style=ft.ButtonStyle(color=ACCENT)),
                                    ], alignment=ft.MainAxisAlignment.CENTER),
                                ],
                                spacing=12,
                            ),
                            padding=28,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                    width=380,
                ),
            )
        ],
    )


def build_signup_view(page: ft.Page, on_login):
    username_f = styled_field("Choose a username")
    password_f = styled_field("Choose a password (min 6 chars)", password=True)
    err_text   = ft.Text("", color=HIGH_CLR, size=13)

    def do_signup(e):
        ok, msg = auth_module.signup(username_f.value, password_f.value)
        if ok:
            snack(page, msg)
            page.go("/login")
        else:
            err_text.value = msg
            page.update()

    return ft.View(
        "/signup",
        bgcolor=BG,
        controls=[
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.SCIENCE_ROUNDED, size=56, color=ACCENT2),
                        ft.Text("Join AspirantFlow", size=28, weight=ft.FontWeight.BOLD, color=TEXT),
                        ft.Divider(height=16, color="transparent"),
                        card(
                            ft.Column(
                                [
                                    label_field("Username", username_f),
                                    label_field("Password", password_f),
                                    err_text,
                                    primary_btn("Create Account", do_signup,
                                                ft.Icons.PERSON_ADD, color=ACCENT2),
                                    ft.TextButton("← Back to Login",
                                                  on_click=lambda _: page.go("/login"),
                                                  style=ft.ButtonStyle(color=TEXT_DIM)),
                                ],
                                spacing=12,
                            ),
                            padding=28,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                    width=380,
                ),
            )
        ],
    )

# ── Dashboard ─────────────────────────────────────────────────────────────────

def build_dashboard(page: ft.Page, user: dict):
    uid    = user["id"]
    today  = date.today().isoformat()
    logs   = db.get_recent_study_summary(uid, 7)
    todos  = [t for t in db.get_todos(uid) if not t["done"]]
    backs  = db.get_backlogs(uid, cleared=False)
    tests  = db.get_tests(uid)

    # stat cards
    total_today = sum(
        r["hours"] for r in db.get_study_logs(uid, today)
    )
    pending_back = len(backs)
    last_score   = tests[-1]["total"] if tests else 0

    def stat_card(label, value, icon, color):
        return ft.Container(
            expand=True,
            content=ft.Column(
                [
                    ft.Icon(icon, color=color, size=28),
                    ft.Text(str(value), size=26, weight=ft.FontWeight.BOLD, color=color),
                    ft.Text(label, size=12, color=TEXT_DIM),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
            ),
            bgcolor=SURFACE,
            border_radius=12,
            padding=ft.padding.symmetric(vertical=20, horizontal=10),
            border=ft.border.all(1, BORDER),
        )

    # mini study bar chart (last 7 days)
    bar_groups = []
    log_map = {r["log_date"]: r["total_hours"] for r in logs}
    from datetime import timedelta
    base = date.today()
    for i in range(6, -1, -1):
        d = (base - timedelta(days=i)).isoformat()
        h = log_map.get(d, 0)
        bar_groups.append(
            ft.BarChartGroup(
                x=6 - i,
                bar_rods=[ft.BarChartRod(
                    from_y=0, to_y=h if h else 0.05,
                    width=18, color=ACCENT,
                    border_radius=4,
                )],
            )
        )

    chart = ft.BarChart(
        bar_groups=bar_groups,
        border=ft.border.all(0, "transparent"),
        left_axis=ft.ChartAxis(labels_size=30),
        bottom_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(
                    value=6 - i,
                    label=ft.Text(
                        (base - timedelta(days=i)).strftime("%a"),
                        size=10, color=TEXT_DIM,
                    ),
                )
                for i in range(6, -1, -1)
            ],
            labels_size=28,
        ),
        max_y=max((r["total_hours"] for r in logs), default=1) + 1,
        bgcolor="transparent",
        expand=True,
        interactive=True,
        tooltip_bgcolor=SURFACE2,
    )

    pending_list = ft.Column(
        [
            ft.Row([
                ft.Icon(ft.Icons.CIRCLE, size=8, color=ACCENT),
                ft.Text(t["task"], size=13, color=TEXT, expand=True),
            ])
            for t in todos[:5]
        ] or [ft.Text("All clear! ✓", color=TEXT_DIM, size=13)],
        spacing=6,
    )

    return ft.Column(
        [
            ft.Text(f"Welcome back, {user['username']} 👋", size=22,
                    weight=ft.FontWeight.BOLD, color=TEXT),
            ft.Text(f"Today: {date.today().strftime('%A, %d %B %Y')}",
                    color=TEXT_DIM, size=13),
            ft.Divider(height=12, color="transparent"),

            # stat row
            ft.Row(
                [
                    stat_card(f"Hours Today", f"{total_today:.1f}h",
                              ft.Icons.TIMER_OUTLINED, ACCENT),
                    stat_card("Backlogs", pending_back,
                              ft.Icons.PENDING_ACTIONS, ACCENT3),
                    stat_card("Last Score", f"{last_score:.0f}",
                              ft.Icons.ANALYTICS_OUTLINED, ACCENT2),
                ],
                spacing=12,
            ),

            ft.Divider(height=12, color="transparent"),

            # charts + todos
            ft.ResponsiveRow(
                [
                    ft.Column(
                        [
                            section_title("Study Hours (Last 7 Days)",
                                          ft.Icons.BAR_CHART),
                            ft.Divider(height=6, color="transparent"),
                            ft.Container(chart, height=180),
                        ],
                        col={"xs": 12, "md": 7},
                    ),
                    ft.Column(
                        [
                            section_title("Pending Tasks", ft.Icons.CHECKLIST),
                            ft.Divider(height=6, color="transparent"),
                            card(pending_list, padding=12),
                        ],
                        col={"xs": 12, "md": 5},
                    ),
                ],
                spacing=16,
            ),
        ],
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

# ── Study Log ─────────────────────────────────────────────────────────────────

def build_study_log(page: ft.Page, user: dict):
    uid = user["id"]
    selected_date = ft.Ref[ft.Text]()
    current_date  = [date.today().isoformat()]

    fields: dict[str, tuple[ft.TextField, ft.TextField]] = {}  # subject → (hours, topics)
    for s in SUBJECTS:
        fields[s] = (
            styled_field("0.0", expand=False),
            styled_field(f"e.g. Chapter 3, Organic reactions…", multiline=True,
                         min_lines=2, max_lines=4),
        )

    status_text = ft.Text("", color=ACCENT2, size=13)

    def load_date(d: str):
        current_date[0] = d
        logs = {r["subject"]: r for r in db.get_study_logs(uid, d)}
        for s in SUBJECTS:
            hf, tf = fields[s]
            row = logs.get(s)
            hf.value = str(row["hours"]) if row else "0"
            tf.value = row["topics"] if row else ""
        status_text.value = ""
        page.update()

    def save_log(e):
        for s in SUBJECTS:
            hf, tf = fields[s]
            try:
                h = float(hf.value or 0)
            except ValueError:
                h = 0.0
            db.upsert_study_log(uid, current_date[0], s, h, tf.value or "")
        status_text.value = f"✓ Saved for {current_date[0]}"
        snack(page, "Study log saved!")

    def pick_date(e):
        def date_picked(ev):
            if ev.value:
                d = ev.value.date().isoformat()
                load_date(d)
                selected_date.current.value = d
                page.update()

        page.open(ft.DatePicker(
            on_change=date_picked,
            first_date=datetime(2024, 1, 1),
            last_date=datetime(2026, 12, 31),
        ))

    load_date(current_date[0])

    subject_cards = []
    for s in SUBJECTS:
        hf, tf = fields[s]
        color = SUBJECT_COLORS[s]
        subject_cards.append(
            ft.Container(
                expand=True,
                content=ft.Column([
                    ft.Row([
                        ft.Container(width=4, height=40, bgcolor=color, border_radius=4),
                        ft.Text(s, size=15, weight=ft.FontWeight.BOLD, color=color),
                    ], spacing=8),
                    label_field("Hours studied", hf),
                    label_field("Topics covered", tf),
                ], spacing=10),
                bgcolor=SURFACE,
                border_radius=12,
                padding=16,
                border=ft.border.all(1, BORDER),
            )
        )

    return ft.Column(
        [
            section_title("Daily Study Log", ft.Icons.MENU_BOOK_ROUNDED),
            ft.Divider(height=12, color="transparent"),
            ft.Row([
                ft.Icon(ft.Icons.CALENDAR_TODAY, color=TEXT_DIM, size=18),
                ft.Text(ref=selected_date, value=current_date[0], color=TEXT, size=14),
                ft.TextButton("Change Date", on_click=pick_date,
                              style=ft.ButtonStyle(color=ACCENT)),
            ]),
            ft.Divider(height=8, color="transparent"),
            ft.ResponsiveRow(
                [ft.Column([c], col={"xs": 12, "md": 4}) for c in subject_cards],
                spacing=12,
            ),
            ft.Divider(height=12, color="transparent"),
            ft.Row([
                primary_btn("Save Log", save_log, ft.Icons.SAVE_ROUNDED),
                status_text,
            ], spacing=16),
        ],
        spacing=4,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

# ── Backlog Manager ───────────────────────────────────────────────────────────

def build_backlog(page: ft.Page, user: dict):
    uid  = user["id"]
    list_col = ft.Column(spacing=8)

    topic_f    = styled_field("Topic name, e.g. Krebs Cycle", expand=True)
    subject_dd = ft.Dropdown(
        options=[ft.dropdown.Option(s) for s in SUBJECTS],
        value="Biology",
        bgcolor=SURFACE2,
        border_color=BORDER,
        focused_border_color=ACCENT,
        color=TEXT,
        hint_style=ft.TextStyle(color=TEXT_DIM),
        border_radius=8,
        width=160,
    )
    priority_dd = ft.Dropdown(
        options=[ft.dropdown.Option(p) for p in ["High", "Medium", "Low"]],
        value="Medium",
        bgcolor=SURFACE2,
        border_color=BORDER,
        focused_border_color=ACCENT,
        color=TEXT,
        border_radius=8,
        width=130,
    )

    def refresh_list():
        list_col.controls.clear()
        items = db.get_backlogs(uid)
        if not items:
            list_col.controls.append(
                ft.Text("No pending backlogs 🎉", color=TEXT_DIM, size=14)
            )
        for item in items:
            iid = item["id"]

            def make_clear(i=iid):
                def _clear(e):
                    db.toggle_backlog(i)
                    refresh_list()
                    page.update()
                return _clear

            def make_delete(i=iid):
                def _delete(e):
                    db.delete_backlog(i)
                    refresh_list()
                    page.update()
                return _delete

            color = SUBJECT_COLORS.get(item["subject"], ACCENT)
            list_col.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(width=4, bgcolor=color, border_radius=4),
                            ft.Column(
                                [
                                    ft.Text(item["topic"], size=14, color=TEXT,
                                            weight=ft.FontWeight.W_500),
                                    ft.Row([
                                        ft.Text(item["subject"], size=11, color=TEXT_DIM),
                                        chip_priority(item["priority"]),
                                    ], spacing=8),
                                ],
                                spacing=4,
                                expand=True,
                            ),
                            ft.IconButton(
                                ft.Icons.CHECK_CIRCLE_OUTLINE,
                                icon_color=ACCENT2,
                                tooltip="Mark cleared",
                                on_click=make_clear(),
                            ),
                            ft.IconButton(
                                ft.Icons.DELETE_OUTLINE,
                                icon_color=HIGH_CLR,
                                tooltip="Delete",
                                on_click=make_delete(),
                            ),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=SURFACE,
                    border_radius=10,
                    padding=ft.padding.symmetric(vertical=10, horizontal=12),
                    border=ft.border.all(1, BORDER),
                )
            )
        page.update()

    def add_item(e):
        if not topic_f.value.strip():
            return
        db.add_backlog(uid, topic_f.value.strip(),
                       subject_dd.value, priority_dd.value)
        topic_f.value = ""
        refresh_list()
        page.update()

    refresh_list()

    return ft.Column(
        [
            section_title("Backlog Manager", ft.Icons.PENDING_ACTIONS),
            ft.Divider(height=12, color="transparent"),
            card(
                ft.Column([
                    ft.Text("Add New Backlog Item", size=14,
                            weight=ft.FontWeight.BOLD, color=TEXT),
                    ft.Row([topic_f, subject_dd, priority_dd], spacing=10,
                           wrap=True),
                    primary_btn("Add to Backlog", add_item, ft.Icons.ADD_CIRCLE_OUTLINE),
                ], spacing=10),
            ),
            ft.Divider(height=16, color="transparent"),
            ft.Text("Pending Backlogs", size=14, color=TEXT_DIM,
                    weight=ft.FontWeight.W_500),
            ft.Divider(height=6, color="transparent"),
            list_col,
        ],
        spacing=4,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

# ── Test Analytics ────────────────────────────────────────────────────────────

def build_analytics(page: ft.Page, user: dict):
    uid      = user["id"]
    table_col = ft.Column(spacing=6)
    chart_col = ft.Column()

    name_f  = styled_field("Test name, e.g. ALLEN Mock #3", expand=True)
    date_f  = styled_field(date.today().isoformat(), value=date.today().isoformat())
    phy_f   = styled_field("0", value="0")
    chem_f  = styled_field("0", value="0")
    bio_f   = styled_field("0", value="0")

    def parse(f):
        try:
            return float(f.value or 0)
        except ValueError:
            return 0.0

    def refresh():
        tests = db.get_tests(uid)

        # ── table ──
        table_col.controls.clear()
        header = ft.Row(
            [ft.Text(h, size=11, color=TEXT_DIM, expand=True, weight=ft.FontWeight.BOLD)
             for h in ["Date", "Test", "Phy", "Chem", "Bio", "Total", ""]],
            spacing=4,
        )
        table_col.controls.append(
            ft.Container(header, bgcolor=SURFACE2, border_radius=8,
                         padding=ft.padding.symmetric(vertical=8, horizontal=10))
        )
        for t in reversed(tests):
            tid = t["id"]

            def make_del(i=tid):
                def _d(e):
                    db.delete_test(i)
                    refresh()
                    page.update()
                return _d

            row_color = SURFACE if tests.index(t) % 2 == 0 else SURFACE2
            table_col.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(t["test_date"], size=12, color=TEXT_DIM, expand=True),
                            ft.Text(t["test_name"] or "—", size=12, color=TEXT, expand=True),
                            ft.Text(f"{t['physics']:.0f}", size=12, color=ACCENT3, expand=True),
                            ft.Text(f"{t['chemistry']:.0f}", size=12, color=ACCENT4, expand=True),
                            ft.Text(f"{t['biology']:.0f}", size=12, color=ACCENT2, expand=True),
                            ft.Text(f"{t['total']:.0f}", size=13, color=ACCENT,
                                    weight=ft.FontWeight.BOLD, expand=True),
                            ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=HIGH_CLR,
                                          on_click=make_del(), icon_size=16),
                        ],
                        spacing=4,
                    ),
                    bgcolor=row_color,
                    border_radius=6,
                    padding=ft.padding.symmetric(vertical=8, horizontal=10),
                )
            )

        # ── line chart ──
        chart_col.controls.clear()
        if tests:
            def make_dp(y, color):
                return ft.LineChartDataPoint(x, y,
                    selected_below_line=ft.ChartPointLine(color=color, stroke_width=1))

            lines = []
            for label, key, color in [
                ("Physics", "physics", ACCENT3),
                ("Chemistry", "chemistry", ACCENT4),
                ("Biology", "biology", ACCENT2),
                ("Total", "total", ACCENT),
            ]:
                pts = [ft.LineChartDataPoint(i, t[key]) for i, t in enumerate(tests)]
                lines.append(ft.LineChartData(
                    data_points=pts,
                    color=color,
                    stroke_width=2,
                    curved=True,
                    below_line_gradient=ft.LinearGradient(
                        colors=[f"{color}44", "transparent"],
                        begin=ft.alignment.top_center,
                        end=ft.alignment.bottom_center,
                    ),
                ))

            max_val = max(t["total"] for t in tests) if tests else 720
            lc = ft.LineChart(
                data_series=lines,
                border=ft.border.all(0, "transparent"),
                left_axis=ft.ChartAxis(labels_size=36),
                bottom_axis=ft.ChartAxis(
                    labels=[
                        ft.ChartAxisLabel(
                            value=i,
                            label=ft.Text(t["test_name"][:8] or t["test_date"][-5:],
                                          size=9, color=TEXT_DIM),
                        )
                        for i, t in enumerate(tests)
                    ],
                    labels_size=36,
                ),
                min_y=0,
                max_y=max_val + 20,
                expand=True,
                bgcolor="transparent",
                interactive=True,
                tooltip_bgcolor=SURFACE2,
            )
            chart_col.controls.append(
                ft.Container(lc, height=260, border_radius=12,
                             bgcolor=SURFACE, padding=16,
                             border=ft.border.all(1, BORDER))
            )
            # legend
            chart_col.controls.append(
                ft.Row([
                    ft.Row([ft.Container(width=16, height=3, bgcolor=c), ft.Text(l, size=11, color=TEXT_DIM)])
                    for l, c in [("Physics", ACCENT3), ("Chemistry", ACCENT4),
                                 ("Biology", ACCENT2), ("Total", ACCENT)]
                ], spacing=16, wrap=True)
            )
        page.update()

    def add_test(e):
        db.add_test(uid, date_f.value.strip(), name_f.value.strip(),
                    parse(phy_f), parse(chem_f), parse(bio_f))
        name_f.value = ""
        refresh()
        page.update()

    refresh()

    return ft.Column(
        [
            section_title("Test Analytics", ft.Icons.ANALYTICS_ROUNDED),
            ft.Divider(height=12, color="transparent"),
            card(
                ft.Column([
                    ft.Text("Log a Test", size=14, weight=ft.FontWeight.BOLD, color=TEXT),
                    ft.ResponsiveRow([
                        ft.Column([label_field("Date (YYYY-MM-DD)", date_f)],
                                  col={"xs": 12, "sm": 4}),
                        ft.Column([label_field("Test Name", name_f)],
                                  col={"xs": 12, "sm": 8}),
                    ], spacing=10),
                    ft.Row([
                        label_field("Physics", phy_f),
                        label_field("Chemistry", chem_f),
                        label_field("Biology", bio_f),
                    ], spacing=12),
                    primary_btn("Add Test", add_test, ft.Icons.ADD_CHART),
                ], spacing=10),
            ),
            ft.Divider(height=16, color="transparent"),
            section_title("Score Trend", ft.Icons.SHOW_CHART),
            ft.Divider(height=8, color="transparent"),
            chart_col,
            ft.Divider(height=16, color="transparent"),
            section_title("Test History", ft.Icons.TABLE_ROWS_ROUNDED),
            ft.Divider(height=8, color="transparent"),
            table_col,
        ],
        spacing=4,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

# ── Daily Grind (To-Do) ───────────────────────────────────────────────────────

def build_todo(page: ft.Page, user: dict):
    uid      = user["id"]
    task_f   = styled_field("Add a task…", expand=True)
    todo_col = ft.Column(spacing=8)

    def refresh():
        todo_col.controls.clear()
        items = db.get_todos(uid)
        pending = [t for t in items if not t["done"]]
        done    = [t for t in items if t["done"]]

        def make_row(t):
            tid = t["id"]
            is_done = bool(t["done"])

            def toggle(e, i=tid):
                db.toggle_todo(i)
                refresh()
                page.update()

            def delete(e, i=tid):
                db.delete_todo(i)
                refresh()
                page.update()

            return ft.Container(
                content=ft.Row(
                    [
                        ft.Checkbox(value=is_done, on_change=toggle,
                                    fill_color=ACCENT2 if is_done else BORDER,
                                    check_color="#000000"),
                        ft.Text(
                            t["task"], size=14, color=TEXT_DIM if is_done else TEXT,
                            expand=True,
                            style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH
                                               if is_done else None),
                        ),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=BORDER,
                                      on_click=delete, icon_size=16),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor=SURFACE2 if is_done else SURFACE,
                border_radius=8,
                padding=ft.padding.symmetric(vertical=8, horizontal=12),
                border=ft.border.all(1, BORDER),
                opacity=0.6 if is_done else 1.0,
            )

        if pending:
            todo_col.controls.append(
                ft.Text(f"Pending ({len(pending)})", size=12, color=TEXT_DIM))
            for t in pending:
                todo_col.controls.append(make_row(t))
        if done:
            todo_col.controls.append(ft.Divider(height=12, color=BORDER))
            todo_col.controls.append(
                ft.Text(f"Completed ({len(done)})", size=12, color=TEXT_DIM))
            for t in done:
                todo_col.controls.append(make_row(t))
        if not items:
            todo_col.controls.append(
                ft.Text("Add your first task above!", color=TEXT_DIM, size=14))

        page.update()

    def add_task(e):
        if task_f.value.strip():
            db.add_todo(uid, task_f.value.strip())
            task_f.value = ""
            refresh()
            page.update()

    task_f.on_submit = add_task
    refresh()

    return ft.Column(
        [
            section_title("The Daily Grind", ft.Icons.CHECKLIST_ROUNDED),
            ft.Text("Tasks persist until you check them off.", color=TEXT_DIM, size=12),
            ft.Divider(height=12, color="transparent"),
            ft.Row([
                task_f,
                primary_btn("Add", add_task, ft.Icons.ADD),
            ], spacing=12),
            ft.Divider(height=12, color="transparent"),
            todo_col,
        ],
        spacing=4,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

# ── Smart Timetable ───────────────────────────────────────────────────────────

def build_timetable(page: ft.Page, user: dict):
    uid = user["id"]

    # Load saved timetable or seed defaults
    saved = db.get_timetable(uid)
    slot_map: dict[tuple, str] = {}
    for s in saved:
        slot_map[(s["day"], s["slot_index"])] = s["activity"]

    # If empty, seed defaults for all days
    if not saved:
        for day in DAYS:
            for idx, (tl, act) in enumerate(DEFAULT_SLOTS):
                db.save_timetable_slot(uid, day, idx, tl, act)
                slot_map[(day, idx)] = act

    selected_day = ft.Ref[ft.Text]()
    current_day = [DAYS[datetime.today().weekday()]]
    slot_controls = ft.Column(spacing=6)

    def build_day_slots(day: str):
        slot_controls.controls.clear()
        for idx, (tl, _) in enumerate(DEFAULT_SLOTS):
            act = slot_map.get((day, idx), DEFAULT_SLOTS[idx][1])
            activity_f = styled_field(DEFAULT_SLOTS[idx][1], value=act, expand=True)

            def make_save(d=day, i=idx, tl2=tl, f=activity_f):
                def _save(e):
                    slot_map[(d, i)] = f.value
                    db.save_timetable_slot(uid, d, i, tl2, f.value)
                    snack(page, "Slot updated!")
                return _save

            activity_f.on_blur = make_save()

            slot_controls.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                ft.Text(tl, size=11, color=ACCENT, weight=ft.FontWeight.W_600),
                                width=80,
                            ),
                            ft.Container(width=1, height=30, bgcolor=BORDER),
                            activity_f,
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=SURFACE,
                    border_radius=8,
                    padding=ft.padding.symmetric(vertical=8, horizontal=12),
                    border=ft.border.all(1, BORDER),
                )
            )
        page.update()

    def switch_day(day: str):
        current_day[0] = day
        if selected_day.current:
            selected_day.current.value = day
        build_day_slots(day)

    build_day_slots(current_day[0])

    day_tabs = ft.Row(
        [
            ft.TextButton(
                d[:3],
                on_click=(lambda e, dd=d: switch_day(dd)),
                style=ft.ButtonStyle(
                    color=ACCENT if d == current_day[0] else TEXT_DIM,
                    bgcolor=SURFACE2 if d == current_day[0] else "transparent",
                    shape=ft.RoundedRectangleBorder(radius=6),
                ),
            )
            for d in DAYS
        ],
        wrap=True,
        spacing=4,
    )

    return ft.Column(
        [
            section_title("Smart Timetable", ft.Icons.CALENDAR_VIEW_WEEK_ROUNDED),
            ft.Text("Click any field to edit and click away to save.",
                    color=TEXT_DIM, size=12),
            ft.Divider(height=12, color="transparent"),
            day_tabs,
            ft.Text(ref=selected_day, value=current_day[0],
                    size=16, weight=ft.FontWeight.BOLD, color=TEXT),
            ft.Divider(height=8, color="transparent"),
            slot_controls,
        ],
        spacing=6,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

# ── Revision Notes ────────────────────────────────────────────────────────────

def build_notes(page: ft.Page, user: dict):
    uid        = user["id"]
    notes_list = ft.Column(spacing=10)
    title_f    = styled_field("Note title, e.g. DNA Replication Key Points", expand=True)
    body_f     = styled_field(
        "Write your note here (Markdown supported)…",
        multiline=True, min_lines=5, max_lines=12, expand=True,
    )
    editing_id = [None]
    preview    = ft.Markdown("", extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                              selectable=True, expand=True)

    def refresh_list():
        notes_list.controls.clear()
        notes = db.get_notes(uid)
        if not notes:
            notes_list.controls.append(
                ft.Text("No notes yet. Add your first volatile fact!",
                        color=TEXT_DIM, size=13))
        for n in notes:
            nid = n["id"]

            def make_edit(note=n):
                def _edit(e):
                    editing_id[0] = note["id"]
                    title_f.value = note["title"]
                    body_f.value  = note["body"]
                    preview.value = note["body"]
                    page.update()
                return _edit

            def make_del(i=nid):
                def _del(e):
                    db.delete_note(i)
                    if editing_id[0] == i:
                        editing_id[0] = None
                        title_f.value = ""
                        body_f.value  = ""
                        preview.value = ""
                    refresh_list()
                    page.update()
                return _del

            notes_list.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(n["title"], size=14, color=TEXT,
                                            weight=ft.FontWeight.W_500),
                                    ft.Text(f"Updated {n['updated_at']}",
                                            size=11, color=TEXT_DIM),
                                ],
                                expand=True,
                                spacing=2,
                            ),
                            ft.IconButton(ft.Icons.EDIT_OUTLINED, icon_color=ACCENT,
                                          on_click=make_edit(), icon_size=18),
                            ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=HIGH_CLR,
                                          on_click=make_del(), icon_size=18),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=SURFACE,
                    border_radius=10,
                    padding=ft.padding.symmetric(vertical=10, horizontal=14),
                    border=ft.border.all(1, BORDER),
                )
            )
        page.update()

    def save_note(e):
        t, b = title_f.value.strip(), body_f.value.strip()
        if not t:
            return
        if editing_id[0]:
            db.update_note(editing_id[0], t, b)
        else:
            editing_id[0] = db.add_note(uid, t, b)
        preview.value = b
        refresh_list()
        snack(page, "Note saved!")

    def new_note(e):
        editing_id[0] = None
        title_f.value = ""
        body_f.value  = ""
        preview.value = ""
        page.update()

    def on_body_change(e):
        preview.value = body_f.value
        page.update()

    body_f.on_change = on_body_change
    refresh_list()

    return ft.Column(
        [
            section_title("Revision Notes", ft.Icons.NOTES_ROUNDED),
            ft.Text("Save volatile facts & formulas. Markdown supported.",
                    color=TEXT_DIM, size=12),
            ft.Divider(height=12, color="transparent"),
            ft.ResponsiveRow(
                [
                    # Editor pane
                    ft.Column(
                        [
                            ft.Row([
                                ft.Text("Editor", size=13, color=TEXT_DIM),
                                ft.IconButton(ft.Icons.ADD_CIRCLE_OUTLINE, icon_color=ACCENT,
                                              tooltip="New note", on_click=new_note, icon_size=18),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            label_field("Title", title_f),
                            label_field("Body (Markdown)", body_f),
                            ft.Row([
                                primary_btn("Save Note", save_note, ft.Icons.SAVE),
                            ]),
                            ft.Divider(height=12, color=BORDER),
                            ft.Text("Saved Notes", size=13, color=TEXT_DIM),
                            notes_list,
                        ],
                        col={"xs": 12, "md": 5},
                        spacing=10,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    # Preview pane
                    ft.Column(
                        [
                            ft.Text("Preview", size=13, color=TEXT_DIM),
                            ft.Container(
                                preview,
                                bgcolor=SURFACE,
                                border_radius=10,
                                padding=16,
                                border=ft.border.all(1, BORDER),
                                expand=True,
                                min_height=400,
                            ),
                        ],
                        col={"xs": 12, "md": 7},
                        spacing=10,
                    ),
                ],
                spacing=16,
                expand=True,
            ),
        ],
        spacing=4,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

# ── Main App Shell ────────────────────────────────────────────────────────────

NAV_ITEMS = [
    ("Dashboard",   ft.Icons.DASHBOARD_ROUNDED),
    ("Study Log",   ft.Icons.MENU_BOOK_ROUNDED),
    ("Backlogs",    ft.Icons.PENDING_ACTIONS),
    ("Analytics",   ft.Icons.ANALYTICS_ROUNDED),
    ("Daily Grind", ft.Icons.CHECKLIST_ROUNDED),
    ("Timetable",   ft.Icons.CALENDAR_VIEW_WEEK_ROUNDED),
    ("Notes",       ft.Icons.NOTES_ROUNDED),
]


def build_app_shell(page: ft.Page, user: dict):
    """Main shell with NavigationRail + content area."""
    selected_idx = [0]
    content_area = ft.Column(expand=True)

    def get_view(idx: int) -> ft.Column:
        builders = [
            build_dashboard,
            build_study_log,
            build_backlog,
            build_analytics,
            build_todo,
            build_timetable,
            build_notes,
        ]
        return builders[idx](page, user)

    def nav_change(e):
        selected_idx[0] = e.control.selected_index
        content_area.controls.clear()
        content_area.controls.append(get_view(selected_idx[0]))
        page.update()

    # Build NavigationRail
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.SELECTED,
        on_change=nav_change,
        bgcolor=SURFACE,
        indicator_color=f"{ACCENT}33",
        indicator_shape=ft.RoundedRectangleBorder(radius=10),
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icon(icon, color=TEXT_DIM),
                selected_icon=ft.Icon(icon, color=ACCENT),
                label=label,
                padding=ft.padding.symmetric(vertical=2),
            )
            for label, icon in NAV_ITEMS
        ],
        leading=ft.Padding(
            padding=ft.padding.only(top=16, bottom=8),
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.LOCAL_HOSPITAL_ROUNDED, color=ACCENT, size=28),
                    ft.Text("AF", size=11, color=TEXT_DIM, weight=ft.FontWeight.BOLD),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
        ),
        trailing=ft.IconButton(
            ft.Icons.LOGOUT_ROUNDED,
            icon_color=TEXT_DIM,
            tooltip="Logout",
            on_click=lambda _: page.go("/login"),
        ),
        min_width=68,
        min_extended_width=160,
        extended=False,
        expand=False,
    )

    content_area.controls.append(get_view(0))

    return ft.Row(
        [
            rail,
            ft.VerticalDivider(width=1, color=BORDER),
            ft.Container(
                content=content_area,
                expand=True,
                padding=24,
            ),
        ],
        expand=True,
        spacing=0,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )


# ── Flet entry point ──────────────────────────────────────────────────────────

def main(page: ft.Page):
    page.title = "AspirantFlow"
    page.bgcolor = BG
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window.min_width = 480
    page.theme = ft.Theme(color_scheme_seed=ACCENT)
    page.fonts = {}  # system fonts

    current_user = [None]

    def on_login(user: dict):
        current_user[0] = user
        page.go("/app")

    def route_change(e):
        route = page.route
        page.views.clear()

        if route == "/signup":
            page.views.append(build_signup_view(page, on_login))
        elif route == "/app" and current_user[0]:
            page.views.append(
                ft.View(
                    "/app",
                    bgcolor=BG,
                    padding=0,
                    controls=[build_app_shell(page, current_user[0])],
                )
            )
        else:
            page.go("/login")
            return

        page.update()

    page.on_route_change = route_change

    # Default view is always the login screen
    page.views.append(build_login_view(page, on_login))
    page.go("/login")


ft.app(target=main)
