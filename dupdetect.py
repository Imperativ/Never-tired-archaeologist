# -*- coding: utf-8 -*-
"""
Einfache Duplikaterkennung über Cosine-Similarity in NumPy.
"""
import math

def cosine_sim(a, b):
    if not a or not b:
        return 0.0
    # numerisch robust ohne numpy
    if len(a) != len(b):
        return 0.0
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))

def most_similar(embedding, seen_list):
    """
    embedding: Liste[float]
    seen_list: Liste[{"embedding":[...], "filename":..., "path":..., "exported_name":...}]
    Returns: (best_candidate_dict|None, best_score: float)
    """
    best = None
    best_score = 0.0
    for item in seen_list:
        sc = cosine_sim(embedding, item.get("embedding", []))
        if sc > best_score:
            best_score = sc
            best = item
    return best, best_score
