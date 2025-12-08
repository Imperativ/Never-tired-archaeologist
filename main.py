#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Archaeologist v3 — Semantische Dokumentenanalyse mit Multi-Provider LLMs
- Scannt Ordner rekursiv
- Extrahiert Text aus 7 Formaten
- Claude Haiku 4.5: Metadaten-Analyse
- Gemini Embedding-001: Vektorisierung
- SQLite + FTS5: Persistente Speicherung & Volltextsuche
- Duplikaterkennung via Cosine-Similarity
- Optional: Markdown-Export
"""
import os
import threading
import queue
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from tkinter import (
    Tk, Button, Label, Text, END, DISABLED, NORMAL,
    filedialog, Scrollbar, RIGHT, Y, LEFT, BOTH, X,
    StringVar, Checkbutton, IntVar, Frame
)
from pathlib import Path

from text_extractor import extract_text, readable_extension, infer_source_type
from file_scanner import iter_supported_files
from exporter import write_markdown_with_metadata
from utils import log_error, safe_relpath
from database import Database, DatabaseError
from llm_providers import MultiProvider, LLMProviderError, RateLimitError
from dupdetect import most_similar

APP_TITLE = "Archaeologist — Dokument-Analysator"
VERSION = "3.0.0"
SIM_THRESHOLD = 0.95  # Duplikat-Schwellwert


class App:
    def __init__(self, master):
        self.master = master
        master.title(f"{APP_TITLE} v{VERSION}")
        master.geometry("900x650")

        # Configuration
        self.source_dir = StringVar(value="(kein Ordner gewählt)")
        self.search_query = StringVar(value="")
        # Central database in app directory (single DB for all scanned folders)
        self.db_path = Path(__file__).parent / "archaeologist.db"
        self.enable_embeddings = IntVar(value=1)
        self.export_markdown = IntVar(value=0)  # Optional, da DB primär

        # LLM Provider (lazy init)
        self.llm_provider = None

        # GUI Setup
        self._build_gui()

        # Message queue for thread-safe GUI updates
        self.msg_queue = queue.Queue()
        self.master.after(100, self.drain_queue)

    def _build_gui(self):
        """Build the GUI layout"""
        # Source directory selection
        frame_source = Frame(self.master)
        frame_source.pack(fill=X, padx=10, pady=(10, 0))

        Label(frame_source, text="Quellordner:").pack(anchor="w")
        self.lbl_dir = Label(frame_source, textvariable=self.source_dir, fg="#06c")
        self.lbl_dir.pack(fill=X, pady=(2, 5))

        self.btn_choose = Button(
            frame_source,
            text="Ordner auswählen …",
            command=self.choose_folder
        )
        self.btn_choose.pack(anchor="w")

        # Options
        frame_options = Frame(self.master)
        frame_options.pack(fill=X, padx=10, pady=(10, 0))

        self.chk_emb = Checkbutton(
            frame_options,
            text="Embeddings erzeugen (empfohlen für Duplikaterkennung)",
            variable=self.enable_embeddings
        )
        self.chk_emb.pack(anchor="w")

        self.chk_export = Checkbutton(
            frame_options,
            text="Zusätzlich Markdown-Dateien exportieren (optional)",
            variable=self.export_markdown
        )
        self.chk_export.pack(anchor="w")

        # Search
        frame_search = Frame(self.master)
        frame_search.pack(fill=X, padx=10, pady=(10, 0))

        Label(frame_search, text="Suche in Datenbank:", font=("Arial", 9)).pack(anchor="w")

        search_input_frame = Frame(frame_search)
        search_input_frame.pack(fill=X, pady=(2, 5))

        from tkinter import Entry
        self.entry_search = Entry(
            search_input_frame,
            textvariable=self.search_query,
            font=("Arial", 10)
        )
        self.entry_search.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        self.entry_search.bind('<Return>', lambda e: self.search_documents())

        self.btn_search = Button(
            search_input_frame,
            text="🔍 Suchen",
            command=self.search_documents,
            state=DISABLED
        )
        self.btn_search.pack(side=LEFT)

        # Actions
        frame_actions = Frame(self.master)
        frame_actions.pack(fill=X, padx=10, pady=(10, 0))

        self.btn_run = Button(
            frame_actions,
            text="Scannen & Analysieren",
            command=self.run_pipeline,
            state=DISABLED,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.btn_run.pack(side=LEFT, padx=(0, 5))

        self.btn_stats = Button(
            frame_actions,
            text="Statistiken anzeigen",
            command=self.show_statistics,
            state=DISABLED
        )
        self.btn_stats.pack(side=LEFT, padx=(0, 5))

        self.btn_clear = Button(
            frame_actions,
            text="Log leeren",
            command=self.clear_log
        )
        self.btn_clear.pack(side=LEFT)

        # Status
        self.lbl_status = Label(self.master, text="Bereit.", fg="#080", font=("Arial", 9))
        self.lbl_status.pack(anchor="w", padx=10, pady=(5, 0))

        # Log output
        frame_log = Frame(self.master)
        frame_log.pack(fill=BOTH, expand=True, padx=10, pady=(5, 10))

        Label(frame_log, text="Protokoll:", font=("Arial", 9)).pack(anchor="w")

        self.txt = Text(frame_log, wrap="word", font=("Consolas", 9))
        scr = Scrollbar(frame_log, command=self.txt.yview)
        self.txt.configure(yscrollcommand=scr.set)
        self.txt.pack(side=LEFT, fill=BOTH, expand=True)
        scr.pack(side=RIGHT, fill=Y)

    def log(self, msg, level="INFO"):
        """Thread-safe logging to GUI"""
        ts = datetime.now().strftime("%H:%M:%S")
        color_map = {"INFO": "black", "WARN": "orange", "ERROR": "red", "SUCCESS": "green"}
        color = color_map.get(level, "black")

        def update():
            self.txt.insert(END, f"[{ts}] {msg}\n")
            # Color last line
            last_line = self.txt.index("end-1c linestart")
            self.txt.tag_add(level, last_line, "end-1c")
            self.txt.tag_config(level, foreground=color)
            self.txt.see(END)

        self.msg_queue.put(update)

    def set_status(self, msg, ok=True):
        """Update status label"""
        def update():
            self.lbl_status.config(text=msg, fg=("#080" if ok else "#a00"))
        self.msg_queue.put(update)

    def choose_folder(self):
        """Choose source directory"""
        d = filedialog.askdirectory(title="Quellordner auswählen")
        if d:
            src_path = Path(d)
            self.source_dir.set(str(src_path))

            # Database path is already set in __init__ (central DB)
            # No need to change it per folder

            self.btn_run.config(state=NORMAL)
            self.btn_stats.config(state=NORMAL)
            self.btn_search.config(state=NORMAL)
            self.set_status(f"Ordner gewählt: {src_path.name}", ok=True)
            self.log(f"Quellordner: {src_path}", "INFO")
            self.log(f"Zentrale Datenbank: {self.db_path}", "INFO")
            self.log(f"Dokumente werden in bestehende DB eingefügt (filepath als Key)", "INFO")

    def clear_log(self):
        """Clear the log output"""
        self.txt.delete(1.0, END)
        self.log("Log geleert.", "INFO")

    def search_documents(self):
        """Search documents in database using full-text search"""
        query = self.search_query.get().strip()

        if not query:
            self.log("Bitte geben Sie einen Suchbegriff ein.", "WARN")
            return

        if not self.db_path or not self.db_path.exists():
            self.log("Keine Datenbank gefunden. Scannen Sie zuerst Dokumente.", "WARN")
            return

        try:
            db = Database(self.db_path)
            results = db.search_fulltext(query, limit=50)

            if not results:
                self.log(f"Keine Ergebnisse für '{query}'", "WARN")
                return

            self.log("=" * 60, "INFO")
            self.log(f"SUCHERGEBNISSE für '{query}' ({len(results)} Treffer)", "SUCCESS")
            self.log("=" * 60, "INFO")

            for i, doc in enumerate(results, 1):
                self.log(f"\n[{i}] {doc['filename']}", "SUCCESS")
                self.log(f"    Pfad: {doc['filepath']}", "INFO")

                if doc.get('topic'):
                    self.log(f"    Topic: {doc['topic']}", "INFO")

                if doc.get('language'):
                    self.log(f"    Sprache: {doc['language']}", "INFO")

                if doc.get('keywords'):
                    keywords_str = ', '.join(doc['keywords'][:5])  # First 5 keywords
                    if len(doc['keywords']) > 5:
                        keywords_str += f" (+{len(doc['keywords']) - 5} weitere)"
                    self.log(f"    Keywords: {keywords_str}", "INFO")

                if doc.get('summary'):
                    # Truncate long summaries
                    summary = doc['summary']
                    if len(summary) > 150:
                        summary = summary[:147] + "..."
                    self.log(f"    Summary: {summary}", "INFO")

                if doc.get('wordcount'):
                    self.log(f"    Wörter: {doc['wordcount']}", "INFO")

            self.log("=" * 60, "INFO")
            self.set_status(f"Suche abgeschlossen: {len(results)} Treffer für '{query}'", ok=True)

        except DatabaseError as e:
            self.log(f"Datenbankfehler: {e}", "ERROR")
            self.set_status("Suchfehler", ok=False)

        except Exception as e:
            self.log(f"Suchfehler: {e}", "ERROR")
            self.set_status("Suchfehler", ok=False)

    def show_statistics(self):
        """Show database statistics"""
        # Database is created automatically, but might be empty
        if not self.db_path:
            self.log("Datenbankpfad nicht gesetzt.", "ERROR")
            return

        try:
            db = Database(self.db_path)
            stats = db.get_statistics()

            self.log("=" * 60, "INFO")
            self.log("ZENTRALE DATENBANK-STATISTIKEN", "SUCCESS")
            self.log("=" * 60, "INFO")
            self.log(f"Datenbank: {self.db_path.name}", "INFO")
            self.log(f"Dokumente gesamt: {stats['total_documents']}", "INFO")
            self.log(f"Embeddings: {stats['total_embeddings']}", "INFO")
            self.log(f"Duplikate: {stats['total_duplicates']}", "INFO")

            if stats['total_documents'] == 0:
                self.log("\n⚠ Datenbank ist leer! Scanne einen Ordner um Dokumente hinzuzufügen.", "WARN")

            if stats['languages']:
                self.log("\nSprachen:", "INFO")
                for lang, count in sorted(stats['languages'].items(), key=lambda x: x[1], reverse=True):
                    self.log(f"  {lang}: {count}", "INFO")

            if stats['file_types']:
                self.log("\nDateitypen:", "INFO")
                for ftype, count in sorted(stats['file_types'].items(), key=lambda x: x[1], reverse=True):
                    self.log(f"  {ftype}: {count}", "INFO")

            self.log("=" * 60, "INFO")

        except Exception as e:
            self.log(f"Fehler beim Abrufen der Statistiken: {e}", "ERROR")

    def run_pipeline(self):
        """Start document processing pipeline"""
        self.btn_run.config(state=DISABLED)
        self.btn_stats.config(state=DISABLED)
        self.set_status("Läuft …", ok=True)
        self.txt.delete(1.0, END)  # Clear log

        t = threading.Thread(target=self._worker, daemon=True)
        t.start()

    def drain_queue(self):
        """Process GUI update queue"""
        try:
            while True:
                fn = self.msg_queue.get_nowait()
                fn()
        except queue.Empty:
            pass
        self.master.after(100, self.drain_queue)

    def _worker(self):
        """Worker thread for document processing"""
        src = Path(self.source_dir.get())
        if not src.exists():
            self.set_status("Ordner existiert nicht.", ok=False)
            self.log("Fehler: Quellordner nicht gefunden", "ERROR")
            self.msg_queue.put(lambda: self.btn_run.config(state=NORMAL))
            self.msg_queue.put(lambda: self.btn_stats.config(state=NORMAL))
            return

        # Initialize database
        try:
            db = Database(self.db_path)
            self.log(f"Datenbank initialisiert: {self.db_path.name}", "SUCCESS")
        except DatabaseError as e:
            self.set_status("Datenbankfehler", ok=False)
            self.log(f"Fehler beim Initialisieren der Datenbank: {e}", "ERROR")
            self.msg_queue.put(lambda: self.btn_run.config(state=NORMAL))
            self.msg_queue.put(lambda: self.btn_stats.config(state=NORMAL))
            return

        # Initialize LLM provider
        try:
            if not self.llm_provider:
                self.log("Initialisiere LLM-Provider (Claude + Gemini)...", "INFO")
                self.llm_provider = MultiProvider()
                self.log("✓ LLM-Provider bereit", "SUCCESS")
        except LLMProviderError as e:
            self.set_status("LLM-Fehler", ok=False)
            self.log(f"Fehler beim Initialisieren der LLM-Provider: {e}", "ERROR")
            self.log("Prüfe API-Keys: ANTHROPIC_API_KEY, GOOGLE_API_KEY", "WARN")
            self.msg_queue.put(lambda: self.btn_run.config(state=NORMAL))
            self.msg_queue.put(lambda: self.btn_stats.config(state=NORMAL))
            return

        # Process files
        total = 0
        processed = 0
        skipped = 0
        errors = 0
        use_embeddings = bool(self.enable_embeddings.get())
        export_md = bool(self.export_markdown.get())

        # Optional: Markdown export directory
        export_dir = None
        if export_md:
            export_dir = src / "_processed"
            export_dir.mkdir(exist_ok=True)

        error_log_path = src / "error_log.txt"

        self.log(f"Scanne Ordner: {src}", "INFO")
        self.log(f"Embeddings: {'Ja' if use_embeddings else 'Nein'}", "INFO")
        self.log(f"Markdown-Export: {'Ja' if export_md else 'Nein'}", "INFO")
        self.log("-" * 60, "INFO")

        for file_path in iter_supported_files(src):
            total += 1
            rel = safe_relpath(file_path, src)

            # Skip if already in database
            if db.document_exists(str(file_path)):
                self.log(f"⊘ Bereits verarbeitet: {rel}", "INFO")
                skipped += 1
                continue

            self.log(f"Verarbeite: {rel}", "INFO")

            try:
                # Extract text
                ext = file_path.suffix.lower()
                text = extract_text(file_path)

                if not text or not text.strip():
                    self.log(f"  → Keine lesbaren Inhalte", "WARN")
                    skipped += 1
                    continue

                wordcount = len(text.split())

                # Get file creation time
                try:
                    created_at = datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                except Exception:
                    created_at = datetime.now().isoformat()

                # Analyze with LLM
                self.log(f"  → Analysiere mit Claude Haiku 4.5...", "INFO")
                metadata, embedding = self.llm_provider.analyze_document(
                    text=text,
                    filename=file_path.name,
                    source_extension=ext,
                    source_type=infer_source_type(ext),
                    generate_embedding=use_embeddings
                )

                self.log(f"  → Sprache: {metadata.get('language', 'N/A')}, Topic: {metadata.get('topic', 'N/A')}", "INFO")

                # Check for duplicates if embedding available
                duplicate_of_id = None
                similarity_score = 0.0

                if embedding:
                    all_embeddings = db.get_all_embeddings()
                    if all_embeddings:
                        # Build seen list for duplicate detection
                        seen = [
                            {"document_id": doc_id, "embedding": emb}
                            for doc_id, emb in all_embeddings
                        ]

                        candidate, score = most_similar(embedding, seen)
                        if candidate and score >= SIM_THRESHOLD:
                            duplicate_of_id = candidate.get("document_id")
                            similarity_score = float(score)
                            self.log(f"  ⚠ Duplikat erkannt (Score: {score:.3f})", "WARN")

                # Insert into database
                doc_id = db.insert_document(
                    filename=file_path.name,
                    filepath=str(file_path),
                    source_extension=ext,
                    source_type=infer_source_type(ext),
                    original_text=text,
                    wordcount=wordcount,
                    created_at=created_at,
                    metadata=metadata,
                    embedding=embedding,
                    embedding_model="gemini-embedding-001" if embedding else "none"
                )

                # Mark as duplicate if detected
                if duplicate_of_id:
                    db.mark_as_duplicate(doc_id, duplicate_of_id, similarity_score)

                self.log(f"  ✓ In Datenbank gespeichert (ID: {doc_id})", "SUCCESS")

                # Optional: Export to Markdown
                if export_md:
                    metadata_with_dup = metadata.copy()
                    metadata_with_dup['duplicate_of'] = duplicate_of_id or ""
                    metadata_with_dup['similarity_score'] = similarity_score
                    metadata_with_dup['embedding'] = embedding or []

                    out_file = write_markdown_with_metadata(
                        base_dir=export_dir,
                        original_path=file_path,
                        text=text,
                        metadata=metadata_with_dup
                    )
                    self.log(f"  ✓ Markdown exportiert: {out_file.name}", "INFO")

                processed += 1

            except RateLimitError as e:
                self.log(f"  ⚠ Rate-Limit erreicht: {e}", "WARN")
                self.log(f"  → Dokument wird später verarbeitet", "WARN")
                errors += 1

            except LLMProviderError as e:
                self.log(f"  ✗ LLM-Fehler: {e}", "ERROR")
                log_error(error_log_path, f"{rel}: LLM-Fehler: {repr(e)}")
                errors += 1

            except Exception as e:
                self.log(f"  ✗ Fehler: {e}", "ERROR")
                log_error(error_log_path, f"{rel}: {repr(e)}")
                errors += 1

        # Summary
        self.log("-" * 60, "INFO")
        self.log("ZUSAMMENFASSUNG", "SUCCESS")
        self.log(f"Dateien gefunden: {total}", "INFO")
        self.log(f"Verarbeitet: {processed}", "SUCCESS")
        self.log(f"Übersprungen: {skipped}", "INFO")
        self.log(f"Fehler: {errors}", "ERROR" if errors > 0 else "INFO")

        # Show statistics
        try:
            stats = db.get_statistics()
            self.log(f"\nDatenbank enthält jetzt {stats['total_documents']} Dokumente", "INFO")
            self.log(f"Embeddings: {stats['total_embeddings']}", "INFO")
            self.log(f"Duplikate: {stats['total_duplicates']}", "INFO")
        except Exception:
            pass

        self.set_status(f"Fertig. {processed}/{total} verarbeitet.", ok=True)
        self.msg_queue.put(lambda: self.btn_run.config(state=NORMAL))
        self.msg_queue.put(lambda: self.btn_stats.config(state=NORMAL))


def main():
    """Main entry point"""
    root = Tk()

    # Check for required environment variables
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("WARNUNG: ANTHROPIC_API_KEY nicht gesetzt!")
        print("Setze die Umgebungsvariable oder erstelle eine .env Datei.")

    if not os.environ.get("GOOGLE_API_KEY") and not os.environ.get("GEMINI_API_KEY"):
        print("WARNUNG: GOOGLE_API_KEY oder GEMINI_API_KEY nicht gesetzt!")
        print("Setze die Umgebungsvariable oder erstelle eine .env Datei.")

    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
