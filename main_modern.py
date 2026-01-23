#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Archaeologist v3.1.0 — Semantische Dokumentenanalyse mit Multi-Provider LLMs
MODERN UI VERSION with ttkbootstrap

- Scannt Ordner rekursiv
- Extrahiert Text aus 7 Formaten
- Claude Haiku 4.5: Metadaten-Analyse
- Gemini Embedding-001: Vektorisierung
- SQLite + FTS5: Persistente Speicherung & Volltextsuche
- Duplikaterkennung via Cosine-Similarity
- Optional: Markdown-Export
- MODERN UI: Dark/Light themes, cards, icons, progress indicators
"""
import os
import threading
import queue
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, END, DISABLED, NORMAL, Text as TkText
from pathlib import Path

from text_extractor import extract_text, readable_extension, infer_source_type
from file_scanner import iter_supported_files
from exporter import write_markdown_with_metadata
from utils import log_error, safe_relpath
from database import Database, DatabaseError
from llm_providers import MultiProvider, LLMProviderError, RateLimitError
from dupdetect import most_similar

APP_TITLE = "Archaeologist — Dokument-Analysator"
VERSION = "3.1.0"
SIM_THRESHOLD = 0.95  # Duplikat-Schwellwert


class App:
    def __init__(self, master):
        self.master = master
        master.title(f"{APP_TITLE} v{VERSION}")
        master.geometry("1000x700")
        master.minsize(800, 600)

        # Configuration
        self.source_dir = ttk.StringVar(value="(kein Ordner gewählt)")
        self.search_query = ttk.StringVar(value="")
        # Central database in app directory (single DB for all scanned folders)
        self.db_path = Path(__file__).parent / "archaeologist.db"
        self.enable_embeddings = ttk.IntVar(value=1)
        self.export_markdown = ttk.IntVar(value=0)  # Optional, da DB primär

        # LLM Provider (lazy init)
        self.llm_provider = None

        # GUI Setup
        self._build_gui()

        # Message queue for thread-safe GUI updates
        self.msg_queue = queue.Queue()
        self.master.after(100, self.drain_queue)

    def _build_gui(self):
        """Build the modern GUI layout with ttkbootstrap"""

        # Main container with padding
        main_container = ttk.Frame(self.master)
        main_container.pack(fill=BOTH, expand=True)

        # Theme toggle button (top-right corner)
        frame_theme = ttk.Frame(main_container)
        frame_theme.pack(anchor="ne", padx=20, pady=10)

        self.btn_theme = ttk.Button(
            frame_theme,
            text="🌓",
            command=self.toggle_theme,
            bootstyle="secondary-outline",
            width=3
        )
        self.btn_theme.pack()

        # ============================================================
        # 1. SOURCE DIRECTORY SECTION (Card-style)
        # ============================================================
        frame_source = ttk.Labelframe(
            main_container,
            text="📁 Quellordner",
            bootstyle="info",
            padding=15
        )
        frame_source.pack(fill=X, padx=20, pady=(10, 0))

        # Selected directory display (card-style with background)
        dir_display = ttk.Frame(frame_source, bootstyle="secondary")
        dir_display.pack(fill=X, pady=(0, 12))

        self.lbl_dir = ttk.Label(
            dir_display,
            textvariable=self.source_dir,
            font=("Segoe UI", 10),
            bootstyle="inverse-secondary",
            padding=12
        )
        self.lbl_dir.pack(fill=X)

        # Button with icon
        self.btn_choose = ttk.Button(
            frame_source,
            text="📂 Ordner auswählen",
            command=self.choose_folder,
            bootstyle="info",
            width=20
        )
        self.btn_choose.pack(anchor="w")

        # ============================================================
        # 2. OPTIONS SECTION (Modern toggles)
        # ============================================================
        frame_options = ttk.Labelframe(
            main_container,
            text="⚙️ Einstellungen",
            bootstyle="secondary",
            padding=15
        )
        frame_options.pack(fill=X, padx=20, pady=(12, 0))

        # Embedding option with round toggle
        self.chk_emb = ttk.Checkbutton(
            frame_options,
            text="Embeddings erzeugen (empfohlen für Duplikaterkennung)",
            variable=self.enable_embeddings,
            bootstyle="success-round-toggle"
        )
        self.chk_emb.pack(anchor="w", pady=(0, 8))

        # Export option
        self.chk_export = ttk.Checkbutton(
            frame_options,
            text="Markdown-Dateien exportieren (optional)",
            variable=self.export_markdown,
            bootstyle="info-round-toggle"
        )
        self.chk_export.pack(anchor="w")

        # ============================================================
        # 3. SEARCH SECTION (Integrated search bar)
        # ============================================================
        frame_search = ttk.Labelframe(
            main_container,
            text="🔍 Suche in Datenbank",
            bootstyle="primary",
            padding=15
        )
        frame_search.pack(fill=X, padx=20, pady=(12, 0))

        search_container = ttk.Frame(frame_search)
        search_container.pack(fill=X)

        self.entry_search = ttk.Entry(
            search_container,
            textvariable=self.search_query,
            font=("Segoe UI", 10),
            bootstyle="primary"
        )
        self.entry_search.pack(side=LEFT, fill=X, expand=True, padx=(0, 8))
        self.entry_search.bind('<Return>', lambda e: self.search_documents())

        self.btn_search = ttk.Button(
            search_container,
            text="🔍 Suchen",
            command=self.search_documents,
            bootstyle="primary",
            state=DISABLED,
            width=12
        )
        self.btn_search.pack(side=LEFT)

        # ============================================================
        # 4. ACTION BUTTONS (Primary + Secondary hierarchy)
        # ============================================================
        frame_actions = ttk.Frame(main_container)
        frame_actions.pack(fill=X, padx=20, pady=(12, 0))

        # Primary action (prominent, success style)
        self.btn_run = ttk.Button(
            frame_actions,
            text="▶️ Scannen & Analysieren",
            command=self.run_pipeline,
            bootstyle="success",
            state=DISABLED,
            width=25
        )
        self.btn_run.pack(side=LEFT, padx=(0, 8))

        # Secondary actions
        self.btn_stats = ttk.Button(
            frame_actions,
            text="📊 Statistiken",
            command=self.show_statistics,
            bootstyle="info-outline",
            state=DISABLED,
            width=15
        )
        self.btn_stats.pack(side=LEFT, padx=(0, 8))

        self.btn_clear = ttk.Button(
            frame_actions,
            text="🗑️ Log leeren",
            command=self.clear_log,
            bootstyle="secondary-outline",
            width=15
        )
        self.btn_clear.pack(side=LEFT)

        # ============================================================
        # 5. STATUS BAR (With progress indicator)
        # ============================================================
        frame_status = ttk.Frame(main_container, bootstyle="dark")
        frame_status.pack(fill=X, padx=20, pady=(12, 0))

        # Status icon + text
        self.status_icon = ttk.Label(
            frame_status,
            text="✅",
            font=("Segoe UI", 10)
        )
        self.status_icon.pack(side=LEFT, padx=(0, 5))

        self.lbl_status = ttk.Label(
            frame_status,
            text="Bereit",
            font=("Segoe UI", 9),
            bootstyle="inverse-success"
        )
        self.lbl_status.pack(side=LEFT, anchor="w")

        # Progress bar (shown during operations)
        self.progress = ttk.Progressbar(
            frame_status,
            mode='indeterminate',
            bootstyle="success-striped",
            length=200
        )
        # Don't pack initially - will be shown during operations

        # ============================================================
        # 6. LOG DISPLAY (Styled text area with better contrast)
        # ============================================================
        frame_log = ttk.Labelframe(
            main_container,
            text="📋 Protokoll",
            bootstyle="secondary",
            padding=10
        )
        frame_log.pack(fill=BOTH, expand=True, padx=20, pady=(12, 20))

        self.txt = TkText(
            frame_log,
            wrap="word",
            font=("Consolas", 9),
            bg="#2b2b2b",
            fg="#ffffff",
            insertbackground="#ffffff",
            selectbackground="#17a2b8",
            selectforeground="#ffffff",
            relief="flat",
            borderwidth=0
        )
        scr = ttk.Scrollbar(
            frame_log,
            command=self.txt.yview,
            bootstyle="secondary-round"
        )
        self.txt.configure(yscrollcommand=scr.set)
        self.txt.pack(side=LEFT, fill=BOTH, expand=True)
        scr.pack(side=RIGHT, fill=Y)

    def toggle_theme(self):
        """Toggle between dark and light themes"""
        current = self.master.style.theme.name
        new_theme = "flatly" if current == "darkly" else "darkly"
        self.master.style.theme_use(new_theme)
        self.log(f"🌓 Theme geändert: {new_theme}")

    def log(self, msg, level="INFO"):
        """Thread-safe logging to GUI text widget with color coding"""
        self.msg_queue.put(("log", msg, level))

    def set_status(self, msg, status_type="info"):
        """
        Update status bar with icon and color
        status_type: 'info', 'success', 'warning', 'error', 'working'
        """
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "working": "⏳"
        }
        styles = {
            "info": "inverse-info",
            "success": "inverse-success",
            "warning": "inverse-warning",
            "error": "inverse-danger",
            "working": "inverse-secondary"
        }

        self.msg_queue.put(("status", msg, icons.get(status_type, "ℹ️"), styles.get(status_type, "inverse-info")))

    def show_progress(self, show=True):
        """Show or hide progress indicator"""
        if show:
            self.progress.pack(side=RIGHT, padx=(10, 0))
            self.progress.start(10)
        else:
            self.progress.stop()
            self.progress.pack_forget()

    def choose_folder(self):
        """Folder selection dialog"""
        folder = filedialog.askdirectory(title="Quellordner auswählen")
        if not folder:
            return

        self.source_dir.set(folder)
        self.log(f"📁 Ordner gewählt: {folder}")
        self.log(f"💾 Zentrale Datenbank: {self.db_path}")

        # Enable buttons after folder selection
        self.btn_run.config(state=NORMAL)
        self.btn_search.config(state=NORMAL)
        self.btn_stats.config(state=NORMAL)

        self.set_status("Ordner ausgewählt – bereit zum Scannen", "success")

    def clear_log(self):
        """Clear the log display"""
        self.txt.delete("1.0", END)
        self.log("🗑️ Protokoll geleert")

    def search_documents(self):
        """Search documents using FTS5"""
        query = self.search_query.get().strip()
        if not query:
            self.log("⚠️ Bitte Suchbegriff eingeben", "WARNING")
            return

        self.set_status(f"Suche nach: '{query}'", "working")
        self.log(f"🔍 Suche: '{query}'")

        try:
            db = Database(self.db_path)
            results = db.fts_search(query)

            if not results:
                self.log(f"❌ Keine Ergebnisse für '{query}'", "WARNING")
                self.set_status("Keine Ergebnisse gefunden", "warning")
            else:
                self.log(f"✅ {len(results)} Treffer gefunden:", "INFO")
                for i, row in enumerate(results, 1):
                    filepath = row.get('filepath', 'N/A')
                    title = row.get('title', 'Ohne Titel')
                    match_score = row.get('rank', 0)

                    self.log(f"  [{i}] {title}", "INFO")
                    self.log(f"      📄 {filepath}", "INFO")
                    self.log(f"      🎯 Score: {match_score:.4f}", "INFO")

                    # Show snippet if available
                    if 'snippet' in row and row['snippet']:
                        snippet = row['snippet'][:200]
                        self.log(f"      💬 {snippet}...", "INFO")
                    self.log("", "INFO")  # Blank line

                self.set_status(f"{len(results)} Ergebnisse gefunden", "success")

        except DatabaseError as e:
            self.log(f"❌ Datenbankfehler: {e}", "ERROR")
            self.set_status("Datenbankfehler", "error")
        except Exception as e:
            self.log(f"❌ Suchfehler: {e}", "ERROR")
            self.set_status("Suchfehler", "error")

    def show_statistics(self):
        """Display database statistics in a modern dialog"""
        try:
            db = Database(self.db_path)
            stats = db.get_statistics()

            # Create modern statistics dialog
            stats_window = ttk.Toplevel(self.master)
            stats_window.title("📊 Statistiken")
            stats_window.geometry("500x400")
            stats_window.resizable(False, False)

            # Main container with scrollbar support
            container = ttk.Frame(stats_window, padding=20)
            container.pack(fill=BOTH, expand=True)

            # Title
            title_label = ttk.Label(
                container,
                text="📊 Datenbank-Statistiken",
                font=("Segoe UI", 14, "bold"),
                bootstyle="primary"
            )
            title_label.pack(pady=(0, 20))

            # Stats cards
            stats_frame = ttk.Frame(container)
            stats_frame.pack(fill=BOTH, expand=True)

            # Document count card
            card1 = ttk.Labelframe(stats_frame, text="📄 Dokumente", bootstyle="info", padding=15)
            card1.pack(fill=X, pady=(0, 10))
            ttk.Label(
                card1,
                text=str(stats.get('total_documents', 0)),
                font=("Segoe UI", 24, "bold"),
                bootstyle="info"
            ).pack()

            # File types card
            card2 = ttk.Labelframe(stats_frame, text="📁 Dateitypen", bootstyle="success", padding=15)
            card2.pack(fill=X, pady=(0, 10))

            file_types = stats.get('file_types', {})
            if file_types:
                for ext, count in file_types.items():
                    ttk.Label(
                        card2,
                        text=f"{ext}: {count}",
                        font=("Segoe UI", 10)
                    ).pack(anchor="w")
            else:
                ttk.Label(card2, text="Keine Daten", bootstyle="secondary").pack()

            # Database info card
            card3 = ttk.Labelframe(stats_frame, text="💾 Datenbank", bootstyle="secondary", padding=15)
            card3.pack(fill=X)

            ttk.Label(
                card3,
                text=f"Pfad: {self.db_path}",
                font=("Consolas", 8),
                wraplength=450
            ).pack(anchor="w")

            # Close button
            ttk.Button(
                container,
                text="Schließen",
                command=stats_window.destroy,
                bootstyle="primary-outline",
                width=15
            ).pack(pady=(20, 0))

        except DatabaseError as e:
            self.log(f"❌ Statistik-Fehler: {e}", "ERROR")
            self.set_status("Fehler beim Laden der Statistiken", "error")
        except Exception as e:
            self.log(f"❌ Unerwarteter Fehler: {e}", "ERROR")
            self.set_status("Unerwarteter Fehler", "error")

    def run_pipeline(self):
        """Start the document analysis pipeline in a background thread"""
        src = self.source_dir.get()
        if not src or src == "(kein Ordner gewählt)":
            self.log("⚠️ Bitte zuerst Ordner auswählen", "WARNING")
            self.set_status("Kein Ordner ausgewählt", "warning")
            return

        # Disable UI during processing
        self.btn_run.config(state=DISABLED)
        self.btn_choose.config(state=DISABLED)
        self.btn_search.config(state=DISABLED)
        self.btn_stats.config(state=DISABLED)

        self.set_status("Analyse läuft...", "working")
        self.show_progress(True)

        # Start worker thread
        t = threading.Thread(target=self._worker, daemon=True)
        t.start()

    def drain_queue(self):
        """Process queued GUI updates from worker thread"""
        try:
            while True:
                item = self.msg_queue.get_nowait()

                if item[0] == "log":
                    _, msg, level = item
                    timestamp = datetime.now().strftime("%H:%M:%S")

                    # Color coding based on level
                    if level == "ERROR":
                        prefix = "❌"
                    elif level == "WARNING":
                        prefix = "⚠️"
                    elif level == "SUCCESS":
                        prefix = "✅"
                    else:
                        prefix = "ℹ️"

                    self.txt.insert(END, f"[{timestamp}] {prefix} {msg}\n")
                    self.txt.see(END)

                elif item[0] == "status":
                    _, msg, icon, style = item
                    self.status_icon.config(text=icon)
                    self.lbl_status.config(text=msg, bootstyle=style)

                elif item[0] == "done":
                    # Re-enable UI
                    self.btn_run.config(state=NORMAL)
                    self.btn_choose.config(state=NORMAL)
                    self.btn_search.config(state=NORMAL)
                    self.btn_stats.config(state=NORMAL)
                    self.show_progress(False)
                    self.set_status("Analyse abgeschlossen", "success")

        except queue.Empty:
            pass

        finally:
            self.master.after(100, self.drain_queue)

    def _worker(self):
        """
        Background worker thread for document analysis.
        Scans folder, processes files, generates embeddings, detects duplicates.
        """
        src = Path(self.source_dir.get())
        do_emb = bool(self.enable_embeddings.get())
        do_export = bool(self.export_markdown.get())

        self.log("🚀 Pipeline gestartet", "INFO")
        self.log(f"📁 Quellordner: {src}", "INFO")
        self.log(f"💾 Datenbank: {self.db_path}", "INFO")
        self.log(f"🔧 Embeddings: {'aktiviert' if do_emb else 'deaktiviert'}", "INFO")
        self.log(f"📝 Markdown-Export: {'aktiviert' if do_export else 'deaktiviert'}", "INFO")

        try:
            # Initialize database
            db = Database(self.db_path)
            self.log("✅ Datenbank verbunden", "SUCCESS")

            # Initialize LLM provider (lazy)
            if self.llm_provider is None:
                self.log("🔑 Initialisiere LLM-Provider...", "INFO")
                self.llm_provider = MultiProvider()
                self.log("✅ LLM-Provider bereit", "SUCCESS")

            # Scan for files
            self.log("🔍 Scanne Dateien...", "INFO")
            files = list(iter_supported_files(src))

            if not files:
                self.log("⚠️ Keine unterstützten Dateien gefunden", "WARNING")
                self.msg_queue.put(("done",))
                return

            self.log(f"✅ {len(files)} Dateien gefunden", "SUCCESS")

            # Process each file
            processed = 0
            skipped = 0
            errors = 0
            duplicates_found = 0

            for i, filepath in enumerate(files, 1):
                try:
                    rel_path = safe_relpath(filepath, src)
                    self.log(f"[{i}/{len(files)}] 📄 {rel_path}", "INFO")

                    # Check if already in database
                    if db.document_exists(str(filepath)):
                        self.log(f"  ⏭️ Bereits in Datenbank", "INFO")
                        skipped += 1
                        continue

                    # Extract text
                    self.log(f"  📖 Extrahiere Text...", "INFO")
                    text = extract_text(filepath)

                    if not text or len(text.strip()) < 10:
                        self.log(f"  ⚠️ Kein verwertbarer Text", "WARNING")
                        skipped += 1
                        continue

                    word_count = len(text.split())
                    self.log(f"  📊 {word_count} Wörter extrahiert", "INFO")

                    # Analyze with LLM
                    self.log(f"  🤖 Analysiere Metadaten...", "INFO")
                    try:
                        ext = filepath.suffix.lower()
                        metadata, embedding = self.llm_provider.analyze_document(
                            text=text,
                            filename=filepath.name,
                            source_extension=ext,
                            source_type=infer_source_type(ext),
                            generate_embedding=do_emb
                        )
                        self.log(f"  ✅ Metadaten: {metadata.get('title', 'N/A')}", "SUCCESS")

                        # Check for duplicates if embedding available
                        if embedding and do_emb:
                            self.log(f"  ✅ Embedding generiert", "SUCCESS")
                            existing = db.get_all_embeddings()
                            if existing:
                                # Build seen list for duplicate detection
                                seen = [
                                    {"document_id": doc_id, "embedding": emb}
                                    for doc_id, emb in existing
                                ]
                                best_match = most_similar(embedding, seen)
                                if best_match and best_match['score'] >= SIM_THRESHOLD:
                                    self.log(f"  🔁 DUPLIKAT gefunden!", "WARNING")
                                    self.log(f"     Ähnlichkeit: {best_match['score']:.2%}", "WARNING")
                                    duplicates_found += 1

                    except (LLMProviderError, RateLimitError) as e:
                        self.log(f"  ⚠️ LLM-Fehler: {e}", "WARNING")
                        metadata = {
                            "title": filepath.name,
                            "summary": "",
                            "keywords": [],
                            "topics": [],
                            "sentiment": "neutral"
                        }
                        embedding = None

                    # Store in database
                    self.log(f"  💾 Speichere in Datenbank...", "INFO")

                    # Get file creation time
                    try:
                        created_at = datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
                    except Exception:
                        created_at = datetime.now().isoformat()

                    db.insert_document(
                        filename=filepath.name,
                        filepath=str(filepath),
                        source_extension=ext,
                        source_type=infer_source_type(ext),
                        original_text=text,
                        wordcount=word_count,
                        created_at=created_at,
                        metadata=metadata,
                        embedding=embedding,
                        embedding_model="gemini-embedding-001" if embedding else "none"
                    )
                    self.log(f"  ✅ Dokument gespeichert", "SUCCESS")

                    # Optional: Export to Markdown
                    if do_export:
                        self.log(f"  📝 Exportiere Markdown...", "INFO")
                        try:
                            write_markdown_with_metadata(filepath, metadata)
                            self.log(f"  ✅ Markdown exportiert", "SUCCESS")
                        except Exception as e:
                            self.log(f"  ⚠️ Export-Fehler: {e}", "WARNING")

                    processed += 1
                    self.log("", "INFO")  # Blank line

                except Exception as e:
                    self.log(f"  ❌ Fehler: {e}", "ERROR")
                    log_error(e, {"file": str(filepath)})
                    errors += 1
                    self.log("", "INFO")  # Blank line

            # Summary
            self.log("=" * 60, "INFO")
            self.log("📊 ZUSAMMENFASSUNG", "INFO")
            self.log("=" * 60, "INFO")
            self.log(f"✅ Verarbeitet: {processed}", "SUCCESS")
            self.log(f"⏭️ Übersprungen: {skipped}", "INFO")
            self.log(f"🔁 Duplikate: {duplicates_found}", "WARNING" if duplicates_found > 0 else "INFO")
            self.log(f"❌ Fehler: {errors}", "ERROR" if errors > 0 else "INFO")
            self.log(f"📁 Gesamt: {len(files)}", "INFO")
            self.log("=" * 60, "INFO")
            self.log("🎉 Pipeline abgeschlossen!", "SUCCESS")

        except DatabaseError as e:
            self.log(f"❌ Datenbankfehler: {e}", "ERROR")
            log_error(e, {"context": "pipeline"})
        except Exception as e:
            self.log(f"❌ Unerwarteter Fehler: {e}", "ERROR")
            log_error(e, {"context": "pipeline"})
        finally:
            self.msg_queue.put(("done",))


def main():
    """Application entry point with modern theme"""
    try:
        # Create main window with darkly theme
        root = ttk.Window(themename="darkly")
        app = App(root)
        root.mainloop()
    except Exception as e:
        print(f"❌ Kritischer Fehler beim Start: {e}")
        log_error(e, {"context": "startup"})

        # Fallback to standard Tkinter if ttkbootstrap fails
        print("⚠️ Fallback zu Standard-Tkinter...")
        from tkinter import Tk
        root = Tk()
        # Import and use original App class here if needed
        print("❌ Bitte ttkbootstrap installieren: pip install ttkbootstrap")


if __name__ == "__main__":
    main()
