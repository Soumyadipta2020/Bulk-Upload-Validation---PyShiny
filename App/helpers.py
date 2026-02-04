from shiny import ui
from datetime import datetime


def create_modal_with_loading(text: str):
    """Create a modal window with custom text and a loading animation."""
    animations = {
        "spinner": """
            <div class="spinner" style="display: inline-block; width: 16px; height: 16px; border: 2px solid #f3f3f3; border-top: 2px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite;"></div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        """,
        "dots": """
            <div class="dots" style="display: inline-block;">
                <span style="animation: blink 1.4s infinite both; animation-delay: 0s;">.</span>
                <span style="animation: blink 1.4s infinite both; animation-delay: 0.2s;">.</span>
                <span style="animation: blink 1.4s infinite both; animation-delay: 0.4s;">.</span>
            </div>
            <style>
                @keyframes blink {
                    0%, 80%, 100% { opacity: 0; }
                    40% { opacity: 1; }
                }
            </style>
        """,
        "pulse": """
            <div class="pulse" style="display: inline-block; width: 16px; height: 16px; background-color: #3498db; border-radius: 50%; animation: pulse 1.5s ease-in-out infinite;"></div>
            <style>
                @keyframes pulse {
                    0% { transform: scale(0); opacity: 1; }
                    100% { transform: scale(1); opacity: 0; }
                }
            </style>
        """,
        "bars": """
            <div class="bars" style="display: inline-block;">
                <div style="display: inline-block; width: 3px; height: 16px; background-color: #3498db; margin: 0 1px; animation: bars 1.2s infinite ease-in-out; animation-delay: -1.1s;"></div>
                <div style="display: inline-block; width: 3px; height: 16px; background-color: #3498db; margin: 0 1px; animation: bars 1.2s infinite ease-in-out; animation-delay: -1.0s;"></div>
                <div style="display: inline-block; width: 3px; height: 16px; background-color: #3498db; margin: 0 1px; animation: bars 1.2s infinite ease-in-out; animation-delay: -0.9s;"></div>
            </div>
            <style>
                @keyframes bars {
                    0%, 40%, 100% { transform: scaleY(0.4); }
                    20% { transform: scaleY(1.0); }
                }
            </style>
        """,
    }

    animation_html = animations.get("bars", "spinner")

    ui.modal_show(
        ui.modal(
            ui.div(
                ui.HTML(f"""
                <div style="font-size: 16px; text-align: center; padding: 20px;">
                    <span>{text}</span>
                    <span style="margin-left: 10px;">
                        {animation_html}
                    </span>
                </div>
            """)
            ),
            easy_close=False,
            footer=None,
        )
    )


def close_modal(delay_seconds: int = 2):
    import time

    time.sleep(delay_seconds)
    ui.modal_remove()
