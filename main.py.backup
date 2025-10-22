#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Archaeologist v2 — GUI-Tool mit Duplikaterkennung
- Scannt Ordner rekursiv
- Extrahiert Text
- GPT-Metadatenanalyse
- Optional: Embeddings
- Duplikaterkennung via Cosine-Similarity über Embeddings
- Export als Markdown mit YAML-Header
"""
import os
import threading
import queue
from datetime import datetime
from tkinter import Tk, Button, Label, Text, END, DISABLED, NORMAL, filedialog, Scrollbar, RIGHT, Y, LEFT, BOTH, X, StringVar, Checkbutton, IntVar
from pathlib import Path

from text_extractor import extract_text, readable_extension, infer_source_type
from file_scanner import iter_supported_files
from exporter import write_markdown_with_metadata
from analyzer import analyze_text, load_api_key_safe, embed_text
from utils import ensure_processed_dir, log_error, safe_relpath

APP_TITLE = "Archaeologist — Dokument-Analysator"
VERSION = "2.0.0"

# Duplikat-Konfiguration
SIM_THRESHOLD = 0.95   # ab diesem Wert wird es als Duplikat markiert

class App:
    def __init__(self, master):
        self.master = master
        master.title(f"{APP_TITLE} v{VERSION}")
        master.geometry("860x560")

        self.source_dir = StringVar(value="(kein Ordner gewählt)")
        self.enable_embeddings = IntVar(value=1)  # für Duplikaterkennung sinnvoll: ON

        Label(master, text="Quellordner:").pack(anchor="w", padx=10, pady=(10, 0))
        self.lbl_dir = Label(master, textvariable=self.source_dir, fg="#06c")
        self.lbl_dir.pack(fill=X, padx=10)

        self.btn_choose = Button(master, text="Ordner auswählen …", command=self.choose_folder)
        self.btn_choose.pack(padx=10, pady=6, anchor="w")

        self.chk_emb = Checkbutton(master, text="Embeddings erzeugen (für Duplikaterkennung empfohlen)", variable=self.enable_embeddings)
        self.chk_emb.pack(padx=10, anchor="w")

        self.btn_run = Button(master, text="Scannen & Exportieren", command=self.run_pipeline, state=DISABLED)
        self.btn_run.pack(padx=10, pady=10, anchor="w")

        self.lbl_status = Label(master, text="Bereit.", fg="#080")
        self.lbl_status.pack(anchor="w", padx=10)

        self.txt = Text(master, wrap="word")
        scr = Scrollbar(master, command=self.txt.yview)
        self.txt.configure(yscrollcommand=scr.set)
        self.txt.pack(side=LEFT, fill=BOTH, expand=True, padx=(10,0), pady=(5,10))
        scr.pack(side=RIGHT, fill=Y, pady=(5,10))

        self.msg_queue = queue.Queue()
        self.master.after(100, self.drain_queue)

    def log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.txt.insert(END, f"[{ts}] {msg}\n")
        self.txt.see(END)

    def set_status(self, msg, ok=True):
        self.lbl_status.config(text=msg, fg=("#080" if ok else "#a00"))

    def choose_folder(self):
        d = filedialog.askdirectory()
        if d:
            self.source_dir.set(d)
            self.btn_run.config(state=NORMAL)
            self.set_status("Ordner gewählt. Bereit zum Start.", ok=True)

    def run_pipeline(self):
        self.btn_run.config(state=DISABLED)
        self.set_status("Läuft …", ok=True)
        t = threading.Thread(target=self._worker, daemon=True)
        t.start()

    def drain_queue(self):
        try:
            while True:
                fn = self.msg_queue.get_nowait()
                fn()
        except queue.Empty:
            pass
        self.master.after(100, self.drain_queue)

    def _worker(self):
        src = Path(self.source_dir.get())
        if not src.exists():
            self.msg_queue.put(lambda: self.set_status("Ordner existiert nicht.", ok=False))
            return

        processed_dir = ensure_processed_dir(src)
        error_log_path = processed_dir / "error_log.txt"
        total = 0
        ok_count = 0
        api_key = load_api_key_safe()
        use_embeddings = bool(self.enable_embeddings.get())

        # Speicher für Duplikatvergleich
        seen = []   # Liste von dicts: {"filename":..., "path":..., "embedding":[...]}

        for file_path in iter_supported_files(src):
            total += 1
            rel = safe_relpath(file_path, src)
            self.msg_queue.put(lambda rel=rel: self.log(f"Verarbeite: {rel}"))

            try:
                ext = file_path.suffix.lower()
                if not readable_extension(ext):
                    self.msg_queue.put(lambda rel=rel: self.log(f"Übersprungen (nicht unterstützt): {rel}"))
                    continue

                text = extract_text(file_path)
                if not text or not text.strip():
                    self.msg_queue.put(lambda rel=rel: self.log(f"Keine lesbaren Inhalte: {rel}"))
                    continue

                # Analyse + evtl. Embedding
                metadata = analyze_text(
                    text=text,
                    filename=file_path.name,
                    filepath=str(file_path),
                    source_extension=ext,
                    source_type=infer_source_type(ext),
                    enable_embeddings=use_embeddings,
                    api_key=api_key,
                )

                # Duplikaterkennung
                duplicate_of = ""
                similarity_score = 0.0
                if use_embeddings and metadata.get("embedding"):
                    from dupdetect import most_similar
                    candidate, score = most_similar(metadata["embedding"], seen)
                    if candidate and score >= SIM_THRESHOLD:
                        duplicate_of = candidate.get("exported_name", candidate.get("filename", ""))
                        similarity_score = float(score)
                        self.msg_queue.put(lambda rel=rel, sc=similarity_score: self.log(f"⚠ Duplikat erkannt (Score {sc:.3f}): {rel}"))

                # im YAML ergänzen
                metadata["duplicate_of"] = duplicate_of
                metadata["similarity_score"] = similarity_score

                out_file = write_markdown_with_metadata(
                    base_dir=processed_dir,
                    original_path=file_path,
                    text=text,
                    metadata=metadata,
                )
                ok_count += 1
                self.msg_queue.put(lambda rel=str(out_file): self.log(f"Exportiert: {rel}"))

                # Gesehene Liste aktualisieren
                if use_embeddings and metadata.get("embedding"):
                    seen.append({
                        "filename": file_path.name,
                        "path": str(file_path),
                        "embedding": metadata["embedding"],
                        "exported_name": out_file.name,
                    })

            except Exception as e:
                log_error(error_log_path, f"{rel}: {repr(e)}")
                self.msg_queue.put(lambda rel=rel: self.log(f"Fehler → geloggt: {rel}"))

        self.msg_queue.put(lambda: self.set_status(f"Fertig. {ok_count}/{total} Dateien verarbeitet.", ok=True))
        self.msg_queue.put(lambda: self.btn_run.config(state=NORMAL))

def main():
    root = Tk()
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
