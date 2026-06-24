import flet as ft


BG = "#101820"
PANEL = "#F5F1E8"
PAPER = "#FFF9E6"
INK = "#1F2933"
MUTED = "#65717C"
ACCENT = "#C65D3B"
GREEN = "#2F7D5A"
BLUE = "#2F5F8F"
YELLOW = "#D7A83E"


def main(page: ft.Page):
    page.title = "放課後の校舎からの脱出"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(font_family="Meiryo")
    page.window_width = 1040
    page.window_height = 760
    page.padding = 0

    game_state = {
        "items": [],
        "checked_places": [],
        "current_area": "computer_room",
        "pc_unlocked": False,
        "locker_unlocked": False,
        "printer_used": False,
        "breaker_fixed": False,
        "action_count": 0,
        "focus": 100,
        "hint_count": 0,
        "wrong_count": 0,
        "cleared": False,
        "game_over": False,
        "message": "放課後の情報室。ここを出ても、まだ校舎から脱出しなければならない。",
    }

    item_view = ft.Column(spacing=8)
    clue_view = ft.Column(spacing=8)
    message_text = ft.Text(game_state["message"], size=15, color=INK, selectable=True)
    action_count_text = ft.Text(size=13, color=MUTED)
    focus_text = ft.Text(size=13, color=INK, weight=ft.FontWeight.BOLD)
    mistake_text = ft.Text(size=12, color=MUTED)

    item_descriptions = {
        "係メモ": "PC係はB2、図書係はA3、ロッカー係はC1。",
        "座席表": "A3=Flet、B2=Linux、C1=青・赤・緑。",
        "巡回メモ": "非常灯側から見る。色順は逆から読む。",
        "色ログ": "青=3、赤=7、緑=9。",
        "小さな鍵": "ロッカーの物理キー。",
        "ドアカード": "情報室のドアに使うカードキー。",
        "最終メモ": "情報室ドアの暗証番号は、時刻の下2桁 + ロッカー番号 + 図書係の答えの文字数。",
        "避難経路図": "2階から4番階段を通り、1階の昇降口へ向かう。",
        "絶縁手袋": "分電盤を安全に操作できる。",
        "非常口コード": "昇降口の非常口端末に使う4桁コード。",
    }

    # 所持アイテムを追加する。すでに持っている場合は重複させない。
    def add_item(item_name):
        if item_name not in game_state["items"]:
            game_state["items"].append(item_name)
        update_status()

    # アイテムを持っているか確認する。
    def has_item(item_name):
        return item_name in game_state["items"]

    # 画面下部のメッセージを更新する。
    def show_message(message):
        game_state["message"] = message
        message_text.value = message
        update_status()
        page.show_dialog(ft.SnackBar(ft.Text(message), open=True))
        page.update()

    # 集中力を減らす。0になると先生が戻ってきてゲームオーバー。
    def lose_focus(amount):
        game_state["focus"] = max(0, game_state["focus"] - amount)
        update_status()
        if game_state["focus"] <= 0 and not game_state["cleared"]:
            game_state["game_over"] = True
            show_game_over()
            return False

        return True

    # 不正解時の共通処理。行動回数だけでなく集中力も減らす。
    def wrong_answer(message):
        game_state["wrong_count"] += 1
        if lose_focus(7):
            show_message(f"{message}\n\n不正解で集中力が下がった。")

    # 行動回数を増やす。クリア後やゲームオーバー後は調査できないようにする。
    def count_action():
        if game_state["cleared"]:
            show_message("すでに脱出済みだ。もう一度遊ぶ場合はリセットしよう。")
            return False

        if game_state["game_over"]:
            show_message("先生が戻ってきた後だ。もう一度遊ぶ場合はリセットしよう。")
            return False

        game_state["action_count"] += 1
        if not lose_focus(1):
            return False

        update_status()
        return True

    # Flet 0.85でも使える枠線を作る。
    def border(color="#D8D0C0", width=1):
        side = ft.BorderSide(width, color)
        return ft.Border(left=side, top=side, right=side, bottom=side)

    # 所持アイテム欄と手がかり欄を最新状態にする。
    def update_status():
        item_view.controls.clear()
        clue_view.controls.clear()

        if game_state["items"]:
            for item in game_state["items"]:
                item_view.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.INVENTORY_2, size=18, color=GREEN),
                                ft.Text(item, size=13, weight=ft.FontWeight.BOLD, color=INK),
                            ],
                            spacing=8,
                        ),
                        padding=ft.Padding(10, 8, 10, 8),
                        bgcolor="#FDFBF4",
                        border=border("#DED4C3"),
                        border_radius=6,
                    )
                )
        else:
            item_view.controls.append(ft.Text("なし", size=14, color=MUTED))

        for item in game_state["items"]:
            if item in item_descriptions:
                clue_view.controls.append(
                    ft.Text(f"・{item}: {item_descriptions[item]}", size=12, color=INK, selectable=True)
                )

        if not clue_view.controls:
            clue_view.controls.append(ft.Text("集めた情報はここに整理される。", size=12, color=MUTED))

        action_count_text.value = f"行動回数: {game_state['action_count']}"
        focus_text.value = f"集中力: {game_state['focus']} / 100"
        mistake_text.value = f"ヒント使用: {game_state['hint_count']} 回 / 不正解: {game_state['wrong_count']} 回"

    # クリア時の評価を計算する。
    def clear_rank():
        score = game_state["focus"] - game_state["hint_count"] * 4 - game_state["wrong_count"] * 5
        if game_state["action_count"] <= 26 and score >= 72:
            return "S"
        if game_state["action_count"] <= 34 and score >= 55:
            return "A"
        if score >= 35:
            return "B"
        return "C"

    # 入力が必要な謎をダイアログで表示する。
    def show_input_dialog(title, question, hint, on_submit, password=False):
        input_field = ft.TextField(
            label="答えを入力",
            autofocus=True,
            password=password,
            can_reveal_password=password,
            on_submit=lambda event: submit_answer(),
        )

        def close_dialog():
            page.pop_dialog()
            page.update()

        def submit_answer():
            answer = input_field.value.strip()
            if not answer:
                close_dialog()
                show_message("何か入力する必要がある。")
                return

            close_dialog()
            on_submit(answer)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Column(
                [
                    ft.Text(question, selectable=True, color=INK),
                    ft.Container(
                        content=ft.Text(hint, size=13, color=MUTED, selectable=True),
                        padding=12,
                        bgcolor="#F3F6F4",
                        border=border("#D7E1DA"),
                        border_radius=6,
                    ),
                    input_field,
                ],
                tight=True,
                spacing=14,
                width=460,
            ),
            actions=[
                ft.TextButton("戻る", on_click=lambda event: close_dialog()),
                ft.ElevatedButton("決定", on_click=lambda event: submit_answer()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.show_dialog(dialog)

    # 机を調べる。係メモを入手し、以後の謎の起点にする。
    def check_desk(event=None):
        if not count_action():
            return

        if "desk" not in game_state["checked_places"]:
            game_state["checked_places"].append("desk")
            add_item("係メモ")
            show_message(
                "机の引き出しから、日直が残した係メモを見つけた。\n\n"
                "PC係: B2\n図書係: A3\nロッカー係: C1\n\n"
                "席番号だけでは意味がない。どこかに座席表があるはずだ。"
            )
            return

        show_message("机には古いUSBケーブルと消しゴムの粉が残っている。新しい手がかりはない。")

    # 黒板を調べる。座席表と時計の時刻を確認する。
    def check_board(event=None):
        if not count_action():
            return

        if "board" not in game_state["checked_places"]:
            game_state["checked_places"].append("board")
            add_item("座席表")
            show_message(
                "黒板に今日の座席表が残っている。\n\n"
                "A1=HTML / A2=Python / A3=Flet\n"
                "B1=Django / B2=Linux / B3=CSS\n"
                "C1=青・赤・緑 / C2=Scratch / C3=JavaScript\n\n"
                "黒板横の時計は17:40で止まっている。"
            )
            return

        show_message("黒板には座席表と、17:40で止まった時計が見える。")

    # 掲示板を調べる。ロッカー番号を逆順に読むための追加ルールを入手する。
    def check_bulletin(event=None):
        if not count_action():
            return

        if "bulletin" not in game_state["checked_places"]:
            game_state["checked_places"].append("bulletin")
            add_item("巡回メモ")
            show_message(
                "掲示板の隅に、用務員の巡回メモが貼られている。\n\n"
                "「情報室のロッカーは非常灯側から確認すること」\n"
                "「窓側に書かれた色順は、非常灯側から見ると逆になる」\n\n"
                "座席表の色順をそのまま読んではいけないようだ。"
            )
            return

        show_message("掲示板には巡回メモが残っている。ロッカーの色順は非常灯側から見る。")

    # パソコンを調べる。係メモと座席表を組み合わせてパスワードを解く。
    def check_pc(event=None):
        if not count_action():
            return

        if game_state["pc_unlocked"]:
            show_message("パソコンは解除済みだ。画面には色ログが表示されている。\n青=3 / 赤=7 / 緑=9")
            return

        if not has_item("係メモ") or not has_item("座席表"):
            show_message("パソコンはログイン画面のままだ。係メモと座席表を照合する必要がありそうだ。")
            return

        def submit_pc(answer):
            if answer.lower() == "linux":
                game_state["pc_unlocked"] = True
                add_item("色ログ")
                show_message(
                    "ログインに成功した。古い管理画面に色ログが表示される。\n\n"
                    "青=3 / 赤=7 / 緑=9\n"
                    "メモ: ロッカー係の席に書かれた色順を使う。"
                )
                return

            wrong_answer("パスワードが違うようだ。PC係の席番号と座席表をもう一度見直そう。")

        show_input_dialog(
            "パソコン",
            "ログインパスワードを入力する。",
            "係メモには「PC係: B2」。座席表でB2に書かれていた単語は何だったか。",
            submit_pc,
            password=True,
        )

    # 本棚を調べる。図書係の席からキーワードを導き、小さな鍵を入手する。
    def check_bookshelf(event=None):
        if not count_action():
            return

        if has_item("小さな鍵"):
            show_message("本棚には鍵が入っていた隙間だけが残っている。")
            return

        if not has_item("係メモ") or not has_item("座席表"):
            show_message("本棚には技術書が並んでいるが、どれを選ぶべきかまだ分からない。")
            return

        def submit_bookshelf(answer):
            if answer.lower() == "flet":
                add_item("小さな鍵")
                game_state["checked_places"].append("bookshelf")
                show_message("Fletの本を少し引くと、奥から小さな鍵が落ちてきた。")
                return

            wrong_answer("その本ではなさそうだ。図書係の席番号と座席表を組み合わせよう。")

        show_input_dialog(
            "本棚",
            "図書係が最後に触った本だけが、少し前に出ている。",
            "係メモには「図書係: A3」。座席表でA3に書かれていた技術名は何だったか。",
            submit_bookshelf,
        )

    # ロッカーを調べる。鍵、色ログ、座席表を組み合わせて3桁番号を解く。
    def check_locker(event=None):
        if not count_action():
            return

        if game_state["locker_unlocked"]:
            show_message("ロッカーは開いている。中にはもう何も残っていない。")
            return

        if not has_item("小さな鍵"):
            show_message("ロッカーには物理キーと3桁の暗証番号が必要だ。鍵がない。")
            return

        if not has_item("色ログ") or not has_item("座席表"):
            show_message("鍵穴は回りそうだが、3桁の番号が分からない。色に関するヒントが必要だ。")
            return

        if not has_item("巡回メモ"):
            show_message("色順は分かったが、ロッカーの向きが気になる。掲示板に管理メモがないか確認しよう。")
            return

        def submit_locker(answer):
            if answer == "973":
                game_state["locker_unlocked"] = True
                add_item("ドアカード")
                show_message(
                    "ロッカーが開いた。中からドアカードを見つけた。\n\n"
                    "ロッカーの奥には「印刷待ちあり」と書かれた付箋も貼ってある。"
                )
                return

            wrong_answer("番号が違うようだ。C1の色順、色ログ、巡回メモの向きを合わせよう。")

        show_input_dialog(
            "ロッカー",
            "物理キーは回った。次は3桁の暗証番号だ。",
            "C1は「青・赤・緑」。ただし巡回メモには、非常灯側から見ると逆になるとある。",
            submit_locker,
            password=True,
        )

    # プリンタを調べる。条件を満たすと最終メモを印刷する。
    def check_printer(event=None):
        if not count_action():
            return

        if game_state["printer_used"]:
            show_message("プリンタのトレイには、最終メモの控えだけが残っている。")
            return

        if not game_state["pc_unlocked"]:
            show_message("プリンタは待機中だ。パソコン側で何かを解除しないと印刷できなさそうだ。")
            return

        if not game_state["locker_unlocked"]:
            show_message("プリンタにはロック付きの印刷ジョブが残っている。ロッカーの中に解除の手がかりがありそうだ。")
            return

        game_state["printer_used"] = True
        add_item("最終メモ")
        show_message(
            "プリンタがゆっくり動き出し、紙が1枚出てきた。\n\n"
            "最終メモ: 最後の暗証番号は、時刻の下2桁 + ロッカー番号 + 図書係の答えの文字数。"
        )

    # 現在地を切り替える。別エリアへ移動した感覚を出すため、画面全体を描き直す。
    def move_area(area_name, message):
        if not count_action():
            return

        game_state["current_area"] = area_name
        game_state["message"] = message
        message_text.value = message
        show_game()
        page.show_dialog(ft.SnackBar(ft.Text(message), open=True))
        page.update()

    # 廊下の窓を調べる。建物内にいる緊張感を出す調査ポイント。
    def check_hall_window(event=None):
        if not count_action():
            return

        show_message(
            "廊下の窓から校庭が見える。部活の声はもう遠い。\n"
            "正門は閉まっているが、昇降口の非常口灯だけがかすかに点いている。"
        )

    # 階段踊り場を調べる。建物脱出に必要な経路情報を得る。
    def check_stairs(event=None):
        if not count_action():
            return

        if "stairs" not in game_state["checked_places"]:
            game_state["checked_places"].append("stairs")
            add_item("避難経路図")
            show_message(
                "階段踊り場の壁に避難経路図が貼られている。\n\n"
                "現在地: 2階 情報室前\n"
                "経路: 2階 → 4番階段 → 1階 昇降口\n\n"
                "図の端には、分電盤メモらしき数字「2-4-1」が書き込まれている。"
            )
            return

        show_message("避難経路図には、2階から4番階段を通って1階へ下りる経路が示されている。")

    # 準備室へ入る。ドアカードを持っていれば入室できる。
    def enter_prep_room(event=None):
        if not has_item("ドアカード"):
            show_message("準備室のドアにはカードリーダーがある。ドアカードが必要だ。")
            return

        move_area(
            "prep_room",
            "準備室に入った。薬品棚、工具棚、古い分電盤が並び、空気が少し重い。",
        )

    # 廊下へ戻る。
    def return_hallway(event=None):
        move_area("hallway", "廊下に戻った。非常口灯の緑色が、奥の昇降口へ続いている。")

    # 工具棚を調べる。分電盤を操作するためのアイテムを得る。
    def check_tool_shelf(event=None):
        if not count_action():
            return

        if has_item("絶縁手袋"):
            show_message("工具棚にはドライバーや古いLANケーブルがある。必要なものはもう取った。")
            return

        add_item("絶縁手袋")
        show_message(
            "工具棚から厚手の絶縁手袋を見つけた。\n"
            "これなら古い分電盤にも触れられそうだ。"
        )

    # 薬品棚を調べる。雰囲気づくりとミスリードの調査ポイント。
    def check_chemical_shelf(event=None):
        if not count_action():
            return

        show_message(
            "薬品棚には清掃用アルコールとラベルの剥がれた瓶が並んでいる。\n"
            "鍵や暗号に関係しそうなものはないが、準備室の静けさが妙に気になる。"
        )

    # 分電盤を調べる。避難経路図の数字を使って昇降口のロック電源を復旧する。
    def check_breaker(event=None):
        if not count_action():
            return

        if game_state["breaker_fixed"]:
            show_message("分電盤は復旧済みだ。昇降口の非常口端末にも電源が戻っているはずだ。")
            return

        if not has_item("絶縁手袋"):
            show_message("分電盤の金属扉は古く、素手で触るのは危険そうだ。絶縁できるものが必要だ。")
            return

        if not has_item("避難経路図"):
            show_message("分電盤には3つのスイッチがある。押す順番の手がかりが必要だ。")
            return

        def submit_breaker(answer):
            normalized = answer.replace("-", "").replace(" ", "")
            if normalized == "241":
                game_state["breaker_fixed"] = True
                add_item("非常口コード")
                show_message(
                    "分電盤のスイッチを 2 → 4 → 1 の順に入れると、低い機械音が廊下へ響いた。\n\n"
                    "昇降口の非常口端末に電源が戻り、画面に「EXIT CODE: 6192」と表示された。"
                )
                return

            wrong_answer("スイッチの順番が違う。避難経路図の階数と階段番号を見直そう。")

        show_input_dialog(
            "分電盤",
            "古い分電盤には、2・4・1のラベルが付いたスイッチがある。",
            "避難経路図には「2階 → 4番階段 → 1階」と書かれていた。",
            submit_breaker,
            password=True,
        )

    # 昇降口を調べる。建物から出る最後の場面。
    def check_entrance(event=None):
        if not count_action():
            return

        if not game_state["breaker_fixed"]:
            show_message("昇降口の自動扉は停止している。非常口端末にも電源が来ていない。")
            return

        if not has_item("非常口コード"):
            show_message("非常口端末は起動しているが、4桁コードが必要だ。準備室の分電盤に何か表示があったはずだ。")
            return

        def submit_entrance(answer):
            if answer == "6192":
                game_state["cleared"] = True
                show_clear()
                return

            wrong_answer("非常口端末のコードが違う。分電盤を復旧したときに表示された数字を思い出そう。")

        show_input_dialog(
            "昇降口 非常口端末",
            "非常口灯が緑に点灯している。端末に4桁コードを入力すれば、建物の外へ出られそうだ。",
            "分電盤を復旧したとき、端末にEXIT CODEが表示されていた。",
            submit_entrance,
            password=True,
        )

    # 情報室のドアを調べる。解除できると建物内の廊下へ移動する。
    def check_door(event=None):
        if not count_action():
            return

        if not has_item("ドアカード"):
            show_message("カードリーダーが赤く光っている。ドアカードが必要だ。")
            return

        if not has_item("最終メモ"):
            show_message("カードは反応したが、最後の暗証番号が必要だ。印刷待ちの資料が気になる。")
            return

        def submit_door(answer):
            if answer == "409734":
                game_state["current_area"] = "hallway"
                game_state["message"] = (
                    "情報室のドアが開いた。\n"
                    "しかし外はまだ校舎の中だ。廊下の奥から、非常口灯の緑色だけが見える。"
                )
                message_text.value = game_state["message"]
                show_game()
                return

            wrong_answer("ドアのロックは解除されなかった。時刻、ロッカー番号、図書係の答えを整理しよう。")

        show_input_dialog(
            "情報室のドア",
            "カードリーダーの横に、最後の暗証番号を入力するテンキーがある。",
            "時刻17:40の下2桁は40。ロッカー番号は973。図書係の答えFletは4文字。",
            submit_door,
            password=True,
        )

    # 行き詰まったときの軽いヒントを出す。
    def show_hint(event=None):
        if game_state["cleared"]:
            show_message("もう脱出済みだ。")
            return

        game_state["hint_count"] += 1
        if not lose_focus(4):
            return

        if not has_item("係メモ"):
            show_message("まずは机を調べよう。係メモがすべての起点になる。")
        elif not has_item("座席表"):
            show_message("係メモの席番号だけでは解けない。黒板の座席表を確認しよう。")
        elif not game_state["pc_unlocked"]:
            show_message("PC係はB2。座席表のB2に書かれた単語をパソコンに入れる。")
        elif not has_item("小さな鍵"):
            show_message("図書係はA3。座席表のA3に書かれた本を本棚で選ぶ。")
        elif not has_item("巡回メモ"):
            show_message("ロッカーの向きを決める情報が足りない。掲示板を確認しよう。")
        elif not game_state["locker_unlocked"]:
            show_message("C1の色順は青・赤・緑。ただし掲示板の巡回メモにより逆順で読む。")
        elif not has_item("最終メモ"):
            show_message("ロッカーを開けた後は、印刷待ちのプリンタを調べよう。")
        elif game_state["current_area"] == "computer_room":
            show_message("情報室ドアの暗証番号を解いたら、建物内の廊下へ進める。")
        elif game_state["current_area"] == "hallway" and not has_item("避難経路図"):
            show_message("廊下ではまず階段踊り場を調べよう。建物から出る経路が分かる。")
        elif game_state["current_area"] == "hallway" and not game_state["breaker_fixed"]:
            show_message("昇降口は電源が落ちている。準備室に入り、分電盤を調べよう。")
        elif game_state["current_area"] == "prep_room" and not has_item("絶縁手袋"):
            show_message("準備室では工具棚を調べよう。分電盤を触る準備が必要だ。")
        elif game_state["current_area"] == "prep_room" and not game_state["breaker_fixed"]:
            show_message("避難経路図の 2階 → 4番階段 → 1階 が、分電盤のスイッチ順になる。")
        elif game_state["current_area"] == "hallway" and game_state["breaker_fixed"]:
            show_message("昇降口の非常口端末に、分電盤復旧時に表示されたEXIT CODEを入力する。")
        else:
            show_message("次に進める場所を調べ、必要な手がかりを組み合わせよう。")

    # 見取り図内の調査カードを作る。
    def scene_tile(title, subtitle, icon, color, handler):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(icon, color=ft.Colors.WHITE, size=24),
                                width=42,
                                height=42,
                                bgcolor=color,
                                border_radius=8,
                                alignment=ft.Alignment(0, 0),
                            ),
                            ft.Column(
                                [
                                    ft.Text(title, size=15, weight=ft.FontWeight.BOLD, color=INK),
                                    ft.Text(subtitle, size=11, color=MUTED),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    )
                ],
                spacing=8,
            ),
            padding=14,
            bgcolor="#FCFAF3",
            border=border("#DDD2BF"),
            border_radius=8,
            on_click=handler,
            ink=True,
        )

    # タイトル画面を表示する。
    def show_title():
        def show_how_to_play(event):
            dialog = ft.AlertDialog(
                title=ft.Text("遊び方"),
                content=ft.Text(
                    "情報室の中の机、黒板、掲示板、パソコン、本棚、ロッカー、プリンタ、ドアを調べます。\n"
                    "行動、ヒント、不正解で集中力が下がります。集中力が0になる前に脱出してください。"
                ),
                actions=[ft.ElevatedButton("閉じる", on_click=lambda event: close_dialog())],
            )
            page.show_dialog(dialog)

        def close_dialog():
            page.pop_dialog()
            page.update()

        page.controls.clear()
        page.add(
            ft.Container(
                expand=True,
                padding=32,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(-1, -1),
                    end=ft.Alignment(1, 1),
                    colors=["#111C24", "#1F4037", "#8A4B32"],
                ),
                content=ft.Column(
                    [
                        ft.Container(expand=1),
                        ft.Icon(ft.Icons.COMPUTER, size=74, color="#F4D35E"),
                        ft.Text(
                            "放課後の校舎からの脱出",
                            size=34,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "夕焼けの情報室、暗い廊下、古い準備室。校舎の出口まで手がかりをつないで進む。",
                            size=15,
                            color="#F0E6CE",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Row(
                            [
                                ft.ElevatedButton("ゲーム開始", icon=ft.Icons.PLAY_ARROW, on_click=lambda event: show_game()),
                                ft.OutlinedButton("遊び方", icon=ft.Icons.HELP_OUTLINE, on_click=show_how_to_play),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=16,
                        ),
                        ft.Container(expand=1),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=22,
                ),
            )
        )
        page.update()

    # メインのゲーム画面を表示する。
    def show_game():
        update_status()

        area_data = {
            "computer_room": {
                "label": "2F 情報室",
                "title": "情報室 見取り図",
                "subtitle": "夕焼けに染まるPC教室。ここから校舎脱出が始まる。",
                "bgcolor": "#ECE5D5",
                "border": "#CBBCA2",
                "tiles": [
                    ("机", "日直の引き出し", ft.Icons.DESK, "#7A4F36", check_desk),
                    ("黒板", "座席表と時計", ft.Icons.CO_PRESENT, "#2F7D5A", check_board),
                    ("掲示板", "巡回メモ", ft.Icons.PUSH_PIN, "#A96D32", check_bulletin),
                    ("パソコン", "ログイン画面", ft.Icons.COMPUTER, "#2F5F8F", check_pc),
                    ("本棚", "技術書の列", ft.Icons.MENU_BOOK, "#8A5A8D", check_bookshelf),
                    ("ロッカー", "鍵とテンキー", ft.Icons.LOCK, "#5F6670", check_locker),
                    ("プリンタ", "印刷待ち", ft.Icons.PRINT, "#D7A83E", check_printer),
                    ("情報室ドア", "廊下へ出る", ft.Icons.DOOR_FRONT_DOOR, "#C65D3B", check_door),
                ],
            },
            "hallway": {
                "label": "2F 廊下",
                "title": "廊下",
                "subtitle": "消灯した校舎。奥の非常口灯だけが緑に光っている。",
                "bgcolor": "#D8DEE2",
                "border": "#AEB9C2",
                "tiles": [
                    ("情報室", "戻って調べ直す", ft.Icons.ARROW_BACK, "#5F6670", lambda event: move_area("computer_room", "情報室に戻った。まだ見落としがあるかもしれない。")),
                    ("廊下の窓", "校庭を確認", ft.Icons.WINDOW, "#486581", check_hall_window),
                    ("階段踊り場", "避難経路図", ft.Icons.STAIRS, "#2F7D5A", check_stairs),
                    ("準備室", "カードリーダー", ft.Icons.MEETING_ROOM, "#8A5A8D", enter_prep_room),
                    ("昇降口", "建物の出口", ft.Icons.EXIT_TO_APP, "#C65D3B", check_entrance),
                ],
            },
            "prep_room": {
                "label": "2F 準備室",
                "title": "情報準備室",
                "subtitle": "古い機材と分電盤が並ぶ薄暗い部屋。",
                "bgcolor": "#E6E0D4",
                "border": "#B9A995",
                "tiles": [
                    ("廊下へ戻る", "非常口灯の方へ", ft.Icons.ARROW_BACK, "#5F6670", return_hallway),
                    ("工具棚", "手袋と工具", ft.Icons.HANDYMAN, "#7A4F36", check_tool_shelf),
                    ("薬品棚", "静かな棚", ft.Icons.SCIENCE, "#5F6670", check_chemical_shelf),
                    ("分電盤", "3つのスイッチ", ft.Icons.ELECTRICAL_SERVICES, "#D7A83E", check_breaker),
                ],
            },
        }
        area = area_data[game_state["current_area"]]

        room_map = ft.Container(
            padding=16,
            bgcolor=area["bgcolor"],
            border=border(area["border"]),
            border_radius=8,
            content=ft.Column(
                [
                    ft.Container(
                        padding=ft.Padding(14, 12, 14, 12),
                        bgcolor="#1F2933",
                        border_radius=8,
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.MAP, color="#F4D35E"),
                                ft.Column(
                                    [
                                        ft.Text(area["label"], size=12, color="#F0E6CE"),
                                        ft.Text(area["subtitle"], size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                            ],
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ),
                    ft.Row(
                        [
                            ft.Text(area["title"], size=18, weight=ft.FontWeight.BOLD, color=INK),
                            ft.Text("クリックして調べる", size=12, color=MUTED),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.ResponsiveRow(
                        [
                            *[
                                ft.Container(
                                    scene_tile(title, subtitle, icon, color, handler),
                                    col={"xs": 12, "sm": 6, "md": 4},
                                )
                                for title, subtitle, icon, color, handler in area["tiles"]
                            ],
                        ],
                        spacing=12,
                        run_spacing=12,
                    ),
                ],
                spacing=14,
            ),
        )

        message_card = ft.Container(
            padding=18,
            bgcolor=PAPER,
            border=border("#E1D3A7"),
            border_radius=8,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.STICKY_NOTE_2, color=ACCENT),
                            ft.Text("調査ログ", weight=ft.FontWeight.BOLD, color=INK),
                        ],
                        spacing=8,
                    ),
                    message_text,
                ],
                spacing=8,
            ),
        )

        side_panel = ft.Container(
            padding=18,
            bgcolor=PANEL,
            border=border("#D4C7B1"),
            border_radius=8,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("所持品", size=17, weight=ft.FontWeight.BOLD, color=INK),
                            ft.IconButton(icon=ft.Icons.LIGHTBULB_OUTLINE, tooltip="ヒント", on_click=show_hint),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    item_view,
                    ft.Divider(),
                    ft.Text("緊張度", size=15, weight=ft.FontWeight.BOLD, color=INK),
                    ft.ProgressBar(value=game_state["focus"] / 100, color=GREEN, bgcolor="#D8D0C0"),
                    focus_text,
                    mistake_text,
                    ft.Divider(),
                    ft.Text("整理した手がかり", size=15, weight=ft.FontWeight.BOLD, color=INK),
                    clue_view,
                    ft.Divider(),
                    action_count_text,
                ],
                spacing=10,
            ),
        )

        page.controls.clear()
        page.add(
            ft.Container(
                expand=True,
                padding=24,
                bgcolor="#DCE4E0",
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text("放課後の校舎からの脱出", size=26, weight=ft.FontWeight.BOLD, color=INK),
                                        ft.Text("集中力が0になる前に、手がかり同士の関係を読む。", size=13, color=MUTED),
                                    ],
                                    spacing=2,
                                ),
                                ft.TextButton("最初から", icon=ft.Icons.RESTART_ALT, on_click=lambda event: reset_game()),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.ResponsiveRow(
                            [
                                ft.Container(ft.Column([room_map, message_card], spacing=16), col={"xs": 12, "md": 8}),
                                ft.Container(side_panel, col={"xs": 12, "md": 4}),
                            ],
                            spacing=16,
                            run_spacing=16,
                        ),
                    ],
                    spacing=16,
                    scroll=ft.ScrollMode.AUTO,
                ),
            )
        )
        page.update()

    # 脱出成功画面を表示する。
    def show_clear():
        page.controls.clear()
        page.add(
            ft.Container(
                expand=True,
                padding=32,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(-1, -1),
                    end=ft.Alignment(1, 1),
                    colors=["#F8F2DC", "#D7E7D7", "#9CC5A1"],
                ),
                content=ft.Column(
                    [
                        ft.Container(expand=1),
                        ft.Icon(ft.Icons.WB_SUNNY, size=82, color="#D7A83E"),
                        ft.Text("脱出成功！", size=38, weight=ft.FontWeight.BOLD, color=GREEN),
                        ft.Container(
                            content=ft.Text(f"評価ランク: {clear_rank()}", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            padding=ft.Padding(18, 10, 18, 10),
                            bgcolor=GREEN,
                            border_radius=8,
                        ),
                        ft.Text(
                            "昇降口の非常口端末が緑に変わり、自動扉がゆっくり開いた。\n"
                            "夜の校庭へ出た瞬間、校舎の中の緊張が一気にほどけた。\n"
                            f"行動回数: {game_state['action_count']} 回 / 残り集中力: {game_state['focus']} / "
                            f"ヒント: {game_state['hint_count']} 回 / 不正解: {game_state['wrong_count']} 回",
                            size=16,
                            color=INK,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.ElevatedButton("もう一度遊ぶ", icon=ft.Icons.RESTART_ALT, on_click=lambda event: reset_game()),
                        ft.Container(expand=1),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                ),
            )
        )
        page.update()

    # 集中力が0になったときのゲームオーバー画面を表示する。
    def show_game_over():
        page.controls.clear()
        page.add(
            ft.Container(
                expand=True,
                padding=32,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(-1, -1),
                    end=ft.Alignment(1, 1),
                    colors=["#1F2933", "#4B2E2E", "#7A3B2E"],
                ),
                content=ft.Column(
                    [
                        ft.Container(expand=1),
                        ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, size=78, color="#F4D35E"),
                        ft.Text("先生が戻ってきた", size=34, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text(
                            "廊下から足音が近づき、情報室の鍵が開いた。\n"
                            "考え込んでいる間に、脱出のチャンスを逃してしまった。",
                            size=16,
                            color="#F0E6CE",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            f"行動回数: {game_state['action_count']} 回 / ヒント: {game_state['hint_count']} 回 / 不正解: {game_state['wrong_count']} 回",
                            size=14,
                            color="#F0E6CE",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.ElevatedButton("もう一度挑戦", icon=ft.Icons.RESTART_ALT, on_click=lambda event: reset_game()),
                        ft.Container(expand=1),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                ),
            )
        )
        page.update()

    # ゲーム状態を初期化してタイトル画面に戻る。
    def reset_game():
        game_state["items"] = []
        game_state["checked_places"] = []
        game_state["current_area"] = "computer_room"
        game_state["pc_unlocked"] = False
        game_state["locker_unlocked"] = False
        game_state["printer_used"] = False
        game_state["breaker_fixed"] = False
        game_state["action_count"] = 0
        game_state["focus"] = 100
        game_state["hint_count"] = 0
        game_state["wrong_count"] = 0
        game_state["cleared"] = False
        game_state["game_over"] = False
        game_state["message"] = "放課後の情報室。ここを出ても、まだ校舎から脱出しなければならない。"
        message_text.value = game_state["message"]
        update_status()
        show_title()

    show_title()


if __name__ == "__main__":
    ft.run(main)
