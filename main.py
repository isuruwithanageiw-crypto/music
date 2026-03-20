import flet as ft
from youtube_service import YouTubeMusicService
import threading
import socket

# Setup Local IP
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

LOCAL_IP = get_local_ip()

def format_time(ms):
    if not ms: return "0:00"
    seconds = (int(ms) // 1000) % 60
    minutes = (int(ms) // (1000 * 60)) % 60
    return f"{minutes}:{seconds:02d}"

def main(page: ft.Page):
    page.title = "Aura Music"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#05050A"
    page.padding = 0

    yt_service = YouTubeMusicService()
    
    current_song = None
    is_playing = False
    is_repeat = False
    up_next_queue = []
    
    # Load history from local browser storage
    play_history = page.client_storage.get("play_history")
    if not isinstance(play_history, list):
        play_history = []

    # Pre-warm Audio context with a dummy URL to satisfy mobile browser autoplay requirements
    audio = ft.Audio(
        src="https://github.com/mdn/webaudio-examples/blob/main/audio-analyser/viper.mp3?raw=true",
        autoplay=False,
        on_position_changed=lambda e: audio_position_changed(e),
        on_duration_changed=lambda e: audio_duration_changed(e),
        on_state_changed=lambda e: audio_state_changed(e)
    )
    page.overlay.append(audio)

    def show_history():
        results_list.controls.clear()
        if not play_history:
            results_list.controls.append(ft.Container(content=ft.Text("Welcome! Search for a song.", color="white54"), padding=20))
        else:
            results_list.controls.append(ft.Text("Play History", color="#E5B036", size=18, weight=ft.FontWeight.W_600))
            for song in play_history:
                results_list.controls.append(
                    ft.ListTile(
                        leading=ft.Image(src=song['thumbnail'], width=55, height=55, fit=ft.ImageFit.COVER, border_radius=10) if song['thumbnail'] else ft.Icon(ft.icons.MUSIC_NOTE),
                        title=ft.Text(song['title'], color="white", weight=ft.FontWeight.W_600),
                        subtitle=ft.Text(song['artist'], color="white70"),
                        on_click=lambda e, s=song: (setattr(search_field, 'value', ''), page.update(), play_song(s))
                    )
                )
        page.update()

    def on_search_change(e):
        query = e.control.value
        if not query:
            show_history()
            return
            
        suggestions = yt_service.get_search_suggestions(query)
        results_list.controls.clear()
        for sug in suggestions:
            results_list.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.icons.SEARCH, color="white54"),
                    title=ft.Text(sug, color="white"),
                    on_click=lambda e, q=sug: (setattr(search_field, 'value', q), page.update(), perform_search(q))
                )
            )
        page.update()

    search_field = ft.TextField(
        hint_text="Search songs, artists...",
        bgcolor=ft.colors.with_opacity(0.15, ft.colors.WHITE),
        border_radius=16,
        prefix_icon=ft.icons.SEARCH,
        border=ft.InputBorder.NONE,
        color="white",
        on_change=on_search_change,
        on_submit=lambda e: perform_search(e.control.value)
    )

    results_list = ft.ListView(expand=True, spacing=10, padding=20)
    
    def play_next_song(e=None):
        if up_next_queue:
            play_song(up_next_queue.pop(0))

    def play_prev_song(e=None):
        if len(play_history) > 1:
            prev = play_history[1]
            play_history.pop(0) # remove currently playing
            play_song(prev)

    def stop_audio(e=None):
        nonlocal is_playing
        if audio:
            audio.pause()
        is_playing = False
        mini_player.visible = False
        full_screen_player.visible = False
        full_screen_player.offset = ft.transform.Offset(0, 1)
        page.update()

    def toggle_repeat_state(e):
        nonlocal is_repeat
        is_repeat = not is_repeat
        color = "#E5B036" if is_repeat else "white54"
        mini_repeat_btn.icon_color = color
        fs_repeat_btn.icon_color = color
        page.update()

    # Mini Player UI
    player_title = ft.Text("No track selected", size=14, weight=ft.FontWeight.BOLD, color="white", max_lines=1)
    player_artist = ft.Text("Unknown Artist", size=12, color="white70", max_lines=1)
    
    def toggle_play_event(e):
        e.control.focus()
        toggle_play()

    play_icon_btn = ft.IconButton(icon=ft.icons.PLAY_ARROW_ROUNDED, icon_color="#E5B036", icon_size=40, on_click=toggle_play_event)
    mini_repeat_btn = ft.IconButton(icon=ft.icons.REPEAT, icon_size=20, icon_color="white54", on_click=toggle_repeat_state)
    mini_prev_btn = ft.IconButton(icon=ft.icons.SKIP_PREVIOUS_ROUNDED, icon_size=32, icon_color="white", on_click=play_prev_song)
    mini_next_btn = ft.IconButton(icon=ft.icons.SKIP_NEXT_ROUNDED, icon_size=32, icon_color="white", on_click=play_next_song)
    mini_stop_btn = ft.IconButton(icon=ft.icons.STOP_ROUNDED, icon_size=24, icon_color="#EF5350", on_click=stop_audio)

    mini_player_img = ft.Container(
        width=50, height=50, 
        bgcolor=ft.colors.with_opacity(0.2, ft.colors.WHITE), 
        border_radius=10,
        content=ft.Icon(ft.icons.MUSIC_NOTE, color=ft.colors.WHITE54)
    )

    # Glassmorphism Mini Player
    mini_player = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Row([
                    mini_player_img,
                    ft.Column([player_title, player_artist], expand=True, alignment=ft.MainAxisAlignment.CENTER, spacing=2),
                    ft.Icon(ft.icons.KEYBOARD_ARROW_UP_ROUNDED, color="white54")
                ]),
                on_click=lambda e: show_fs_player(e)
            ),
            ft.Row([
                mini_repeat_btn,
                mini_prev_btn,
                play_icon_btn,
                mini_next_btn,
                mini_stop_btn
            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
        ], spacing=5),
        bgcolor=ft.colors.with_opacity(0.5, "black"),
        blur=ft.Blur(30, 30),
        border=ft.border.all(1, ft.colors.with_opacity(0.3, ft.colors.WHITE)),
        padding=10,
        border_radius=20,
        margin=ft.margin.all(12),
        shadow=ft.BoxShadow(blur_radius=25, color=ft.colors.with_opacity(0.5, "black")),
        visible=False
    )

    # Full Screen Player UI
    fs_album_art = ft.Image(width=340, height=340, fit=ft.ImageFit.COVER, border_radius=25)
    fs_title = ft.Text("Title", size=26, weight=ft.FontWeight.BOLD, color="white", max_lines=2, text_align=ft.TextAlign.CENTER)
    fs_artist = ft.Text("Artist", size=18, color="white70", max_lines=1, text_align=ft.TextAlign.CENTER)
    
    progress_slider = ft.Slider(min=0, max=100, value=0, thumb_color="#E5B036", active_color="#E5B036", inactive_color="white30", expand=True)
    fs_current_time = ft.Text("0:00", size=12, color="white54")
    fs_total_time = ft.Text("0:00", size=12, color="white54")

    fs_play_btn = ft.IconButton(icon=ft.icons.PAUSE_CIRCLE_FILLED_ROUNDED, icon_size=80, icon_color="#E5B036", on_click=toggle_play_event)
    fs_repeat_btn = ft.IconButton(icon=ft.icons.REPEAT, icon_size=28, icon_color="white54", on_click=toggle_repeat_state)
    fs_prev_btn = ft.IconButton(icon=ft.icons.SKIP_PREVIOUS_ROUNDED, icon_size=45, icon_color="white", on_click=play_prev_song)
    fs_next_btn = ft.IconButton(icon=ft.icons.SKIP_NEXT_ROUNDED, icon_size=45, icon_color="white", on_click=play_next_song)

    full_screen_player = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.IconButton(icon=ft.icons.KEYBOARD_ARROW_DOWN_ROUNDED, icon_size=36, icon_color="white", on_click=lambda e: hide_fs_player())
            ], alignment=ft.MainAxisAlignment.START),
            ft.Container(height=30),
            ft.Container(
                content=fs_album_art,
                shadow=ft.BoxShadow(blur_radius=60, color=ft.colors.with_opacity(0.35, "white")), # Glowing effect
                alignment=ft.alignment.center
            ),
            ft.Container(height=40),
            ft.Column([fs_title, fs_artist], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(height=30),
            ft.Row([fs_current_time, progress_slider, fs_total_time], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                ft.IconButton(icon=ft.icons.SHUFFLE, icon_size=28, icon_color="white54"),
                fs_prev_btn,
                fs_play_btn,
                fs_next_btn,
                fs_repeat_btn,
            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=ft.colors.with_opacity(0.85, "#05050A"),
        blur=ft.Blur(40, 40),
        expand=True,
        padding=20,
        offset=ft.transform.Offset(0, 1),
        animate_offset=ft.animation.Animation(500, ft.AnimationCurve.EASE_OUT_EXPO),
        visible=False
    )

    def show_fs_player(e):
        full_screen_player.visible = True
        full_screen_player.offset = ft.transform.Offset(0, 0)
        page.update()
        
    def hide_fs_player():
        full_screen_player.offset = ft.transform.Offset(0, 1)
        page.update()

    # Main Background Container
    bg_container = ft.Container(
        image_src="https://images.unsplash.com/photo-1614613535308-eb5fbd3d2c17?q=80&w=1000",
        image_fit=ft.ImageFit.COVER,
        image_opacity=0.3,
        expand=True,
        content=ft.Stack([
            ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Text("Aura Music", size=32, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                        ft.IconButton(icon=ft.icons.HISTORY, icon_size=28, icon_color="white54", on_click=lambda e: (setattr(search_field, 'value', ''), page.update(), show_history()))
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.only(left=20, right=20, top=40)
                ),
                ft.Container(
                    content=search_field,
                    padding=ft.padding.only(left=20, right=20, top=10)
                ),
                ft.Container(content=results_list, expand=True),
                mini_player
            ], expand=True),
            full_screen_player  # Overlayed Full Screen Player
        ], expand=True)
    )

    def audio_position_changed(e):
        pos = int(e.data)
        progress_slider.value = pos
        fs_current_time.value = format_time(pos)
        page.update()

    def audio_duration_changed(e):
        dur = int(e.data)
        progress_slider.max = dur
        fs_total_time.value = format_time(dur)
        page.update()

    def audio_state_changed(e):
        nonlocal is_playing
        if e.data == "completed":
            if is_repeat:
                audio.seek(0)
            elif up_next_queue:
                play_next_song()
            else:
                is_playing = False
                play_icon_btn.icon = ft.icons.PLAY_ARROW_ROUNDED
                fs_play_btn.icon = ft.icons.PLAY_CIRCLE_FILLED_ROUNDED
                page.update()

    def play_song(song):
        nonlocal current_song, is_playing, audio
        current_song = song
        
        # Add to history
        if song not in play_history:
            play_history.insert(0, song)
            # Limit history
            if len(play_history) > 20: 
                play_history.pop()
            # Save history to local browser storage
            page.client_storage.set("play_history", play_history)

        player_title.value = song['title']
        player_artist.value = song['artist']
        fs_title.value = song['title']
        fs_artist.value = song['artist']
        
        if song['thumbnail']:
            bg_container.image_src = song['thumbnail']
            bg_container.image_opacity = 0.4
            
            mini_player_img.content = ft.Image(src=song['thumbnail'], fit=ft.ImageFit.COVER, border_radius=10)
            fs_album_art.src = song['thumbnail']
            
        mini_player.visible = True
        
        play_icon_btn.icon = ft.icons.HOURGLASS_EMPTY
        fs_play_btn.icon = ft.icons.HOURGLASS_EMPTY
        page.update()
        
        try:
            import threading
            def load_and_play():
                nonlocal is_playing, up_next_queue
                filename = yt_service.download_song(song['id'])
                if filename:
                    audio.src = filename
                    audio.play()
                    is_playing = True
                    
                    # Update buttons on UI thread
                    play_icon_btn.icon = ft.icons.PAUSE_ROUNDED
                    fs_play_btn.icon = ft.icons.PAUSE_CIRCLE_FILLED_ROUNDED
                    page.update()
                    
                    # Fetch next queue in background transparently
                    up_next_queue = yt_service.get_up_next(song['id'])
                    
            threading.Thread(target=load_and_play, daemon=True).start()
                
        except Exception as e:
            print("Playback error", e)

    def toggle_play():
        nonlocal current_song, is_playing, audio
        if not current_song or audio is None: return
        
        if is_playing:
            audio.pause()
            play_icon_btn.icon = ft.icons.PLAY_ARROW_ROUNDED
            fs_play_btn.icon = ft.icons.PLAY_CIRCLE_FILLED_ROUNDED
        else:
            audio.resume()
            play_icon_btn.icon = ft.icons.PAUSE_ROUNDED
            fs_play_btn.icon = ft.icons.PAUSE_CIRCLE_FILLED_ROUNDED
        
        is_playing = not is_playing
        page.update()

    def perform_search(query):
        if not query: return
        results_list.controls.clear()
        results_list.controls.append(ft.Row([ft.ProgressRing(color="#E5B036")], alignment=ft.MainAxisAlignment.CENTER))
        page.update()
        
        songs = yt_service.search_songs(query)
        results_list.controls.clear()
        
        for song in songs:
            results_list.controls.append(
                ft.ListTile(
                    leading=ft.Image(src=song['thumbnail'], width=55, height=55, fit=ft.ImageFit.COVER, border_radius=10) if song['thumbnail'] else ft.Icon(ft.icons.MUSIC_NOTE),
                    title=ft.Text(song['title'], color="white", weight=ft.FontWeight.W_600),
                    subtitle=ft.Text(song['artist'], color="white70"),
                    on_click=lambda e, s=song: play_song(s)
                )
            )
        page.update()

    # Show history initially
    show_history()
    page.add(bg_container)
    page.update()

if __name__ == "__main__":
    print("\n" + "="*50)
    print(f"🔥 AURA MUSIC IS RUNNING! 🔥")
    print(f"To play on your MOBILE, open Safari/Chrome and type:")
    print(f"👉 http://{LOCAL_IP}:8550 👈")
    print("="*50 + "\n")
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=8550, assets_dir="assets")
