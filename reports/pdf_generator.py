"""
PDF report generator for la soccer Machine.
Uses fpdf2 to produce branded player reports.
"""
from __future__ import annotations

import io
import tempfile
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

try:
    from fpdf import FPDF
except ImportError:
    FPDF = None  # type: ignore

# Brand colours as (R, G, B)
DARK_GREEN = (26, 77, 46)
GOLD = (212, 160, 23)
LIGHT_TEXT = (220, 220, 220)
WHITE = (255, 255, 255)
DARK_BG = (15, 31, 20)


class PlayerReport:
    """
    Build a PDF report for a single player.

    Usage
    -----
    report = PlayerReport()
    report.add_header("Kylian Mbappé", {"match": "FRA vs ESP", "date": "2021-07-06"})
    report.add_stats_table({"goals": 1, "passes": 45, ...})
    report.add_figure(fig, "Heatmap")
    report.add_figure(radar_fig, "Radar Tactique")
    report.add_observations("Le joueur a montré une grande intensité...")
    pdf_bytes = report.generate()
    """

    def __init__(self) -> None:
        if FPDF is None:
            raise ImportError("fpdf2 n'est pas installé. Installez-le avec : pip install fpdf2")
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self._temp_files: list[str] = []
        self._setup_fonts()

    def _setup_fonts(self) -> None:
        self.pdf.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", uni=True)
        self.pdf.add_font("DejaVu", "B", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", uni=True)
        self.pdf.add_font("DejaVu", "I", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf", uni=True)

    def _set_font(self, style: str = "", size: int = 11) -> None:
        try:
            self.pdf.set_font("DejaVu", style, size)
        except Exception:
            self.pdf.set_font("Helvetica", style, size)

    def _header_band(self) -> None:
        """Draw the dark-green header band on current page."""
        self.pdf.set_fill_color(*DARK_GREEN)
        self.pdf.rect(0, 0, 210, 22, "F")
        # Gold accent line
        self.pdf.set_fill_color(*GOLD)
        self.pdf.rect(0, 22, 210, 1.5, "F")

    def _footer_band(self) -> None:
        self.pdf.set_fill_color(*DARK_GREEN)
        self.pdf.rect(0, 282, 210, 15, "F")
        self._set_font("", 7)
        self.pdf.set_text_color(*LIGHT_TEXT)
        self.pdf.set_y(285)
        self.pdf.cell(0, 5, "la soccer Machine — Sport Analytics  |  Données: StatsBomb Open Data", align="C")

    def add_header(self, player_name: str, match_info: dict) -> None:
        """Add cover / header page with player name and match context."""
        self.pdf.add_page()
        self.pdf.set_fill_color(*DARK_BG)
        self.pdf.rect(0, 0, 210, 297, "F")

        # Top accent band
        self.pdf.set_fill_color(*DARK_GREEN)
        self.pdf.rect(0, 0, 210, 50, "F")
        self.pdf.set_fill_color(*GOLD)
        self.pdf.rect(0, 50, 210, 3, "F")

        # Brand name
        self._set_font("B", 22)
        self.pdf.set_text_color(*GOLD)
        self.pdf.set_xy(0, 10)
        self.pdf.cell(210, 12, "la soccer Machine", align="C")

        self._set_font("I", 9)
        self.pdf.set_text_color(*LIGHT_TEXT)
        self.pdf.set_xy(0, 22)
        self.pdf.cell(210, 8, "SPORT ANALYTICS — RAPPORT TACTIQUE", align="C")

        # Player name
        self._set_font("B", 28)
        self.pdf.set_text_color(*WHITE)
        self.pdf.set_xy(0, 70)
        self.pdf.cell(210, 14, player_name, align="C")

        # Gold divider
        self.pdf.set_fill_color(*GOLD)
        self.pdf.rect(40, 88, 130, 0.8, "F")

        # Match info
        self._set_font("", 12)
        self.pdf.set_text_color(*LIGHT_TEXT)
        y = 95
        for k, v in match_info.items():
            self.pdf.set_xy(0, y)
            self.pdf.cell(210, 8, f"{k.title()} : {v}", align="C")
            y += 9

        # Watermark football
        self._set_font("", 60)
        self.pdf.set_text_color(26, 77, 46)
        self.pdf.set_xy(0, 180)
        self.pdf.cell(210, 40, "⚽", align="C")

        self._footer_band()

    def add_stats_table(self, stats: dict, section_title: str = "Statistiques du match") -> None:
        """Add a two-column stats table on a new page."""
        self.pdf.add_page()
        self.pdf.set_fill_color(*DARK_BG)
        self.pdf.rect(0, 0, 210, 297, "F")
        self._header_band()

        # Section title
        self._set_font("B", 14)
        self.pdf.set_text_color(*GOLD)
        self.pdf.set_xy(15, 28)
        self.pdf.cell(0, 10, section_title)

        # Gold line under title
        self.pdf.set_fill_color(*GOLD)
        self.pdf.rect(15, 39, 180, 0.5, "F")

        # Table rows
        LABEL_MAP = {
            "minutes": "Minutes jouées",
            "goals": "Buts",
            "assists": "Passes décisives",
            "shots": "Tirs",
            "shots_on_target": "Tirs cadrés",
            "xg": "xG",
            "passes": "Passes",
            "pass_completion": "% Passes réussies",
            "key_passes": "Passes clés",
            "progressive_passes": "Passes progressives",
            "carries": "Conduites de balle",
            "dribbles_attempted": "Dribbles tentés",
            "dribbles_completed": "Dribbles réussis",
            "pressures": "Pressings",
            "pressing_intensity": "Intensité pressing",
            "duels": "Duels",
            "duels_won": "Duels gagnés",
            "defensive_actions": "Actions défensives",
            "ball_receipts": "Réceptions",
        }

        y = 45
        row_h = 8
        col_label_w = 100
        col_val_w = 80

        for i, (key, val) in enumerate(stats.items()):
            if y > 265:
                break
            fill = i % 2 == 0
            if fill:
                self.pdf.set_fill_color(20, 50, 35)
                self.pdf.rect(15, y, 180, row_h, "F")

            label = LABEL_MAP.get(key, key.replace("_", " ").title())
            if isinstance(val, float):
                display_val = f"{val:.2f}"
            else:
                display_val = str(val)

            self._set_font("", 10)
            self.pdf.set_text_color(*LIGHT_TEXT)
            self.pdf.set_xy(18, y + 1)
            self.pdf.cell(col_label_w, row_h - 2, label)

            self._set_font("B", 10)
            self.pdf.set_text_color(*GOLD)
            self.pdf.set_xy(18 + col_label_w, y + 1)
            self.pdf.cell(col_val_w, row_h - 2, display_val)

            y += row_h

        self._footer_band()

    def add_figure(self, fig: plt.Figure, title: str = "") -> None:
        """Save a matplotlib figure to a temp PNG and embed in PDF."""
        self.pdf.add_page()
        self.pdf.set_fill_color(*DARK_BG)
        self.pdf.rect(0, 0, 210, 297, "F")
        self._header_band()

        if title:
            self._set_font("B", 14)
            self.pdf.set_text_color(*GOLD)
            self.pdf.set_xy(15, 28)
            self.pdf.cell(0, 10, title)

        # Save figure to temp file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name
        self._temp_files.append(tmp_path)

        fig.savefig(tmp_path, dpi=120, bbox_inches="tight",
                    facecolor=fig.get_facecolor(), format="png")

        # Embed image: centered, max width 170mm
        img_y = 42 if title else 28
        try:
            self.pdf.image(tmp_path, x=20, y=img_y, w=170)
        except Exception:
            self._set_font("", 10)
            self.pdf.set_text_color(*LIGHT_TEXT)
            self.pdf.set_xy(15, img_y + 10)
            self.pdf.cell(0, 8, "[Erreur lors du rendu de l'image]")

        self._footer_band()

    def add_observations(self, text: str, section_title: str = "Observations tactiques") -> None:
        """Add a free-text observations section."""
        self.pdf.add_page()
        self.pdf.set_fill_color(*DARK_BG)
        self.pdf.rect(0, 0, 210, 297, "F")
        self._header_band()

        self._set_font("B", 14)
        self.pdf.set_text_color(*GOLD)
        self.pdf.set_xy(15, 28)
        self.pdf.cell(0, 10, section_title)

        self.pdf.set_fill_color(*GOLD)
        self.pdf.rect(15, 39, 180, 0.5, "F")

        self._set_font("", 10)
        self.pdf.set_text_color(*LIGHT_TEXT)
        self.pdf.set_xy(15, 44)
        self.pdf.set_left_margin(15)
        self.pdf.set_right_margin(15)

        # Strip markdown bold (**...**) for PDF plain text
        clean_text = text.replace("**", "").replace("*", "")
        self.pdf.multi_cell(0, 6, clean_text)

        self._footer_band()

    def generate(self) -> bytes:
        """Return PDF as bytes and clean up temp files."""
        output = self.pdf.output()
        # Cleanup temp image files
        for path in self._temp_files:
            try:
                Path(path).unlink(missing_ok=True)
            except Exception:
                pass
        self._temp_files.clear()
        return bytes(output)
