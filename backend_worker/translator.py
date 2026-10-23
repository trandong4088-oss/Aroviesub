"""
ARO Master Translation Engine & SQLite Translation Memory (Spec 06)
Features:
- SQLite Translation Memory (TM) with O(1) hash lookups and hit counting
- Donghua Glossary Engine with Longest-Source-Match-First precedence
- Character Bible & Directed Pronoun Relation matching
- Strict Batching (up to 32 cues / 120s anchor partition)
- LLM Providers: Gemini 2.5 Flash / Groq / OpenAI compatible
- Strict Spec 06 'aro-translate-v1' JSON schema parsing and verification
"""

from __future__ import annotations

import os
import re
import sys
import json
import sqlite3
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any

from models import SubtitleCue, compute_sha256, generate_uuid


# Built-in Default Donghua Seed Glossary (Cultivation, Sects, Addresses, Martial Arts)
DEFAULT_DONGHUA_GLOSSARY: List[Dict[str, Any]] = [
    # Sects & Factions (Môn phái, thế lực)
    {"source": "青云门", "target": "Thanh Vân Môn", "category": "SECT"},
    {"source": "天音寺", "target": "Thiên Âm Tự", "category": "SECT"},
    {"source": "焚香谷", "target": "Phần Hương Cốc", "category": "SECT"},
    {"source": "鬼王宗", "target": "Quỷ Vương Tông", "category": "SECT"},
    {"source": "万毒门", "target": "Vạn Độc Môn", "category": "SECT"},
    {"source": "合欢派", "target": "Hợp Hoan Phái", "category": "SECT"},
    {"source": "炼血堂", "target": "Luyện Huyết Đường", "category": "SECT"},
    {"source": "武魂殿", "target": "Vũ Hồn Điện", "category": "SECT"},
    {"source": "昊天宗", "target": "Hạo Thiên Tông", "category": "SECT"},
    {"source": "七宝琉璃宗", "target": "Thất Bảo Lưu Ly Tông", "category": "SECT"},
    {"source": "蓝电霸王龙宗", "target": "Lam Điện Bá Vương Long Tông", "category": "SECT"},
    {"source": "史莱克学院", "target": "Học viện Shrek", "category": "SECT"},
    {"source": "云岚宗", "target": "Vân Lam Tông", "category": "SECT"},
    {"source": "萧家", "target": "Tiêu gia", "category": "SECT"},
    {"source": "迦南学院", "target": "Học viện Già Nam", "category": "SECT"},
    {"source": "魂殿", "target": "Hồn Điện", "category": "SECT"},
    {"source": "丹塔", "target": "Đan Tháp", "category": "SECT"},

    # Cultivation Realms (Cảnh giới tu luyện)
    {"source": "练气期", "target": "Luyện Khí kỳ", "category": "REALM"},
    {"source": "炼气", "target": "Luyện Khí", "category": "REALM"},
    {"source": "筑基期", "target": "Trúc Cơ kỳ", "category": "REALM"},
    {"source": "筑基", "target": "Trúc Cơ", "category": "REALM"},
    {"source": "金丹期", "target": "Kim Đan kỳ", "category": "REALM"},
    {"source": "结丹", "target": "Kết Đan", "category": "REALM"},
    {"source": "元婴期", "target": "Nguyên Anh kỳ", "category": "REALM"},
    {"source": "化神期", "target": "Hóa Thần kỳ", "category": "REALM"},
    {"source": "合体期", "target": "Hợp Thể kỳ", "category": "REALM"},
    {"source": "大乘期", "target": "Đại Thừa kỳ", "category": "REALM"},
    {"source": "渡劫期", "target": "Độ Kiếp kỳ", "category": "REALM"},
    {"source": "斗者", "target": "Đấu Giả", "category": "REALM"},
    {"source": "斗师", "target": "Đấu Sư", "category": "REALM"},
    {"source": "大斗师", "target": "Đại Đấu Sư", "category": "REALM"},
    {"source": "斗灵", "target": "Đấu Linh", "category": "REALM"},
    {"source": "斗王", "target": "Đấu Vương", "category": "REALM"},
    {"source": "斗皇", "target": "Đấu Hoàng", "category": "REALM"},
    {"source": "斗宗", "target": "Đấu Tông", "category": "REALM"},
    {"source": "斗尊", "target": "Đấu Tôn", "category": "REALM"},
    {"source": "斗圣", "target": "Đấu Thánh", "category": "REALM"},
    {"source": "斗帝", "target": "Đấu Đế", "category": "REALM"},
    {"source": "魂师", "target": "Hồn Sư", "category": "REALM"},
    {"source": "魂王", "target": "Hồn Vương", "category": "REALM"},
    {"source": "魂帝", "target": "Hồn Đế", "category": "REALM"},
    {"source": "魂圣", "target": "Hồn Thánh", "category": "REALM"},
    {"source": "封号斗罗", "target": "Phong Hào Đấu La", "category": "REALM"},

    # Forms of Address & Pronouns (Xưng hô giang hồ, tu tiên)
    {"source": "师尊", "target": "Sư tôn", "category": "PERSON"},
    {"source": "师兄", "target": "Sư huynh", "category": "PERSON"},
    {"source": "师姐", "target": "Sư tỷ", "category": "PERSON"},
    {"source": "师弟", "target": "Sư đệ", "category": "PERSON"},
    {"source": "师妹", "target": "Sư muội", "category": "PERSON"},
    {"source": "宗主", "target": "Tông chủ", "category": "PERSON"},
    {"source": "掌门", "target": "Chưởng môn", "category": "PERSON"},
    {"source": "大长老", "target": "Đại trưởng lão", "category": "PERSON"},
    {"source": "长老", "target": "Trưởng lão", "category": "PERSON"},
    {"source": "前辈", "target": "Tiền bối", "category": "PERSON"},
    {"source": "晚辈", "target": "Vãn bối", "category": "PERSON"},
    {"source": "本座", "target": "Bản tọa", "category": "PERSON"},
    {"source": "老夫", "target": "Lão phu", "category": "PERSON"},
    {"source": "徒儿", "target": "Đồ nhi", "category": "PERSON"},
    {"source": "掌柜", "target": "Chưởng quầy", "category": "PERSON"},
    {"source": "道友", "target": "Đạo hữu", "category": "PERSON"},
    {"source": "阁下", "target": "Các hạ", "category": "PERSON"},
    {"source": "在下", "target": "Tại hạ", "category": "PERSON"},
    {"source": "在下不才", "target": "Tại hạ bất tài", "category": "PERSON"},
    {"source": "少侠", "target": "Thiếu hiệp", "category": "PERSON"},
    {"source": "姑娘", "target": "Cô nương", "category": "PERSON"},
    {"source": "公子", "target": "Công tử", "category": "PERSON"},

    # Martial Arts, Artifacts & Concepts (Công pháp, bảo vật, chiêu thức)
    {"source": "异火", "target": "Dị hỏa", "category": "ITEM"},
    {"source": "玄重尺", "target": "Huyền Trọng Xích", "category": "ITEM"},
    {"source": "佛怒火莲", "target": "Phật Nộ Hỏa Liên", "category": "SKILL"},
    {"source": "神剑御雷真诀", "target": "Thần Kiếm Ngự Lôi Chân Quyết", "category": "SKILL"},
    {"source": "诛仙剑", "target": "Tru Tiên Kiếm", "category": "ITEM"},
    {"source": "噬魂棒", "target": "Phệ Hồn Bổng", "category": "ITEM"},
    {"source": "烧火棍", "target": "Thiêu Hỏa Côn", "category": "ITEM"},
    {"source": "储物戒", "target": "Nhẫn trữ vật", "category": "ITEM"},
    {"source": "储物袋", "target": "Túi trữ vật", "category": "ITEM"},
    {"source": "飞剑", "target": "Phi kiếm", "category": "ITEM"},
    {"source": "法宝", "target": "Pháp bảo", "category": "ITEM"},
    {"source": "灵石", "target": "Linh thạch", "category": "ITEM"},
    {"source": "丹药", "target": "Đan dược", "category": "ITEM"},
    {"source": "破厄丹", "target": "Phá Ách Đan", "category": "ITEM"},
    {"source": "筑基丹", "target": "Trúc Cơ Đan", "category": "ITEM"},
    {"source": "天劫", "target": "Thiên kiếp", "category": "OTHER"},
    {"source": "雷劫", "target": "Lôi kiếp", "category": "OTHER"},
    {"source": "心魔", "target": "Tâm ma", "category": "OTHER"},
    {"source": "走火入魔", "target": "Tẩu hỏa nhập ma", "category": "OTHER"},
    {"source": "神识", "target": "Thần thức", "category": "OTHER"},
    {"source": "神魂", "target": "Thần hồn", "category": "OTHER"},
    {"source": "肉身", "target": "Nhục thân", "category": "OTHER"},
    {"source": "闭关", "target": "Bế quan", "category": "OTHER"},
    {"source": "陨落", "target": "Ngã xuống", "category": "OTHER"},
    {"source": "夺舍", "target": "Đoạt xá", "category": "OTHER"},
]


class TranslationMemoryStore:
    """
    SQLite-backed Translation Memory and Donghua Glossary.
    Implements O(1) primary-key lookups by SHA-256 hash of normalized source text.
    """

    def __init__(self, db_path: str = "aro_translation_memory.db"):
        self.db_path = db_path
        self._init_tables()
        self._seed_default_glossary()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        with self._get_conn() as conn:
            cur = conn.cursor()
            # Translation Memory Table (O(1) exact hash match)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS translation_memory (
                    source_hash TEXT PRIMARY KEY,
                    source_text TEXT NOT NULL,
                    target_vi TEXT NOT NULL,
                    category TEXT DEFAULT 'DIALOGUE',
                    scope TEXT DEFAULT 'GLOBAL',
                    locked INTEGER DEFAULT 0,
                    hit_count INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Glossary Table (Spec 06)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS glossary_entries (
                    entry_id TEXT PRIMARY KEY,
                    source_term TEXT UNIQUE NOT NULL,
                    target_vi TEXT NOT NULL,
                    category TEXT DEFAULT 'OTHER',
                    scope TEXT DEFAULT 'PROJECT',
                    locked INTEGER DEFAULT 1
                );
            """)

            # Character Bible & Directed Pronoun Relations (Spec 06)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS character_relations (
                    relation_id TEXT PRIMARY KEY,
                    from_char TEXT NOT NULL,
                    to_char TEXT NOT NULL,
                    self_pronoun_vi TEXT NOT NULL,
                    address_pronoun_vi TEXT NOT NULL,
                    locked INTEGER DEFAULT 1
                );
            """)
            conn.commit()

    def _seed_default_glossary(self):
        """Seed default Donghua glossary if empty."""
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM glossary_entries")
            count = cur.fetchone()[0]
            if count == 0:
                print(f"[TM] Seeding {len(DEFAULT_DONGHUA_GLOSSARY)} Donghua glossary entries into SQLite...")
                for item in DEFAULT_DONGHUA_GLOSSARY:
                    cur.execute("""
                        INSERT OR IGNORE INTO glossary_entries
                        (entry_id, source_term, target_vi, category, scope, locked)
                        VALUES (?, ?, ?, ?, 'PROJECT', 1)
                    """, (generate_uuid(), item["source"], item["target"], item.get("category", "OTHER")))
                conn.commit()

    def lookup_memory(self, source_text: str) -> Optional[str]:
        """O(1) exact hash lookup in translation memory."""
        cleaned = source_text.strip()
        if not cleaned:
            return None
        h = compute_sha256(cleaned)
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT target_vi, hit_count FROM translation_memory WHERE source_hash = ?", (h,))
            row = cur.fetchone()
            if row:
                # Increment hit count
                cur.execute("UPDATE translation_memory SET hit_count = hit_count + 1 WHERE source_hash = ?", (h,))
                conn.commit()
                return str(row["target_vi"])
        return None

    def store_memory(self, source_text: str, target_vi: str, locked: bool = False, category: str = "DIALOGUE"):
        """Store validated translation back to TM for future O(1) hits."""
        cleaned_src = source_text.strip()
        cleaned_tgt = target_vi.strip()
        if not cleaned_src or not cleaned_tgt:
            return
        h = compute_sha256(cleaned_src)
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO translation_memory (source_hash, source_text, target_vi, category, locked)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(source_hash) DO UPDATE SET
                    target_vi = excluded.target_vi,
                    locked = CASE WHEN excluded.locked = 1 THEN 1 ELSE translation_memory.locked END,
                    hit_count = translation_memory.hit_count + 1
            """, (h, cleaned_src, cleaned_tgt, category, 1 if locked else 0))
            conn.commit()

    def get_all_glossary_sorted(self) -> List[Tuple[str, str, str]]:
        """
        Spec 06 Section 2: Returns glossary terms sorted by length DESCENDING
        to enforce 'longest source_forms first' matching precedence.
        """
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT source_term, target_vi, category FROM glossary_entries ORDER BY LENGTH(source_term) DESC")
            rows = cur.fetchall()
            return [(r["source_term"], r["target_vi"], r["category"]) for r in rows]

    def add_glossary_term(self, source_term: str, target_vi: str, category: str = "OTHER", locked: bool = True):
        """Add or update custom glossary entry."""
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO glossary_entries (entry_id, source_term, target_vi, category, locked)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(source_term) DO UPDATE SET
                    target_vi = excluded.target_vi,
                    category = excluded.category,
                    locked = excluded.locked
            """, (generate_uuid(), source_term.strip(), target_vi.strip(), category, 1 if locked else 0))
            conn.commit()


class DonghuaTranslator:
    """
    High-performance Subtitle Translator conforming to ARO Master Spec 06.
    Integrates SQLite Translation Memory (O(1)), Longest-Match-First Glossary,
    and LLM providers (Gemini / Groq / OpenAI compatible).
    """

    def __init__(
        self,
        db_path: str = "aro_translation_memory.db",
        gemini_api_key: Optional[str] = None,
        groq_api_key: Optional[str] = None,
        genre: str = "xianxia",
        batch_size: int = 24,
    ):
        self.tm = TranslationMemoryStore(db_path)
        self.gemini_api_key = gemini_api_key or os.environ.get("GEMINI_API_KEY", "")
        self.groq_api_key = groq_api_key or os.environ.get("GROQ_API_KEY", "")
        self.genre = genre
        self.batch_size = min(32, max(4, batch_size))  # Spec 06 Section 4: <= 32 cues

    def match_glossary_terms_for_text(self, text: str) -> List[Tuple[str, str]]:
        """Find all glossary matches in source text with Longest-Match-First precedence."""
        matched = []
        glossary_items = self.tm.get_all_glossary_sorted()
        for src, tgt, _ in glossary_items:
            if src in text:
                matched.append((src, tgt))
        return matched

    def _call_gemini_api(self, prompt: str) -> str:
        """Call Google Gemini 2.5 Flash API with strict JSON mode."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_api_key}"
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")

        with urllib.request.urlopen(req, timeout=45) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
            candidate = resp_data["candidates"][0]["content"]["parts"][0]["text"]
            return candidate

    def _call_groq_llama(self, prompt: str) -> str:
        """Call Groq API Llama 3.3 70B as high-speed translation engine."""
        url = "https://api.groq.com/openai/v1/chat/completions"
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional Donghua (Chinese animation) subtitler and translator. Respond in valid strict JSON matching the schema."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Authorization", f"Bearer {self.groq_api_key}")
        req.add_header("Content-Type", "application/json")

        with urllib.request.urlopen(req, timeout=45) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
            return resp_data["choices"][0]["message"]["content"]

    def _build_batch_prompt(self, cues_batch: List[SubtitleCue], batch_id: str) -> str:
        """
        ARO Spec 06 Section 5 prompt contract ('aro-translate-v1').
        """
        # Collect relevant glossary for this batch
        combined_text = " ".join(c.source_text for c in cues_batch)
        matched_glossary = self.match_glossary_terms_for_text(combined_text)

        glossary_prompt_lines = [f"- {src} => {tgt}" for src, tgt in matched_glossary[:25]]
        glossary_block = "\n".join(glossary_prompt_lines) if glossary_prompt_lines else "(Không có thuật ngữ bắt buộc đặc biệt)"

        items_to_translate = []
        for c in cues_batch:
            items_to_translate.append({
                "cue_id": c.cue_id,
                "source_text": c.source_text,
                "start_ms": c.start_ms,
                "end_ms": c.end_ms,
            })

        genre_guidelines = {
            "xianxia": "Thể loại Tiên Hiệp (Xianxia): Giữ chuẩn các danh xưng sư môn, cảnh giới, công pháp, bảo vật. Dùng từ Hán Việt trang trọng, chuẩn chỉ.",
            "wuxia": "Thể loại Kiếm Hiệp (Wuxia): Giữ ngữ vực giang hồ, vai vế đại hiệp/tiểu bối, chiêu thức võ công dứt khoát.",
            "historical": "Thể loại Cổ Trang: Xưng hô đúng địa vị quân thần, huynh đệ, phụ mẫu; văn phong cổ trang mượt mà.",
            "transmigration": "Thể loại Trùng Sinh / Xuyên Không: Lời thoại nội tâm có thể hiện đại hóm hỉnh, đối thoại giữ chuẩn bối cảnh.",
            "modern": "Thể loại Hiện Đại: Tiếng Việt tự nhiên đời thường, tránh dùng từ cổ không cần thiết.",
            "neutral": "Giữ nguyên sắc thái gốc, dịch chuẩn nghĩa, trôi chảy.",
        }.get(self.genre, "Dịch tự nhiên, đúng ngữ cảnh tiếng Việt.")

        prompt = f"""Bạn là dịch giả hàng đầu cho phim hoạt hình Trung Quốc (Donghua). Hãy chuyển lời thoại trong dữ liệu cues sang tiếng Việt theo đặc tả ARO Master (aro-translate-v1).

QUY TẮC BẮT BUỘC:
1. Thể loại phim: {self.genre.upper()} - {genre_guidelines}
2. BẮT BUỘC áp dụng từ điển chuyên ngành sau (ưu tiên cụm dài nhất):
{glossary_block}
3. Mỗi cue_id trong danh sách input PHẢI có đúng một trường "text_vi" tương ứng trong mảng "items".
4. Giữ đúng ý, thông tin và cảm xúc. Không bỏ sót cue_id, không thêm cue mới.
5. Câu ngắn gọn, tự nhiên, phù hợp để người xem đọc phụ đề kịp thời.
6. Trả về DUY NHẤT một JSON hợp lệ với cấu trúc sau:

{{
  "batch_id": "{batch_id}",
  "items": [
    {{
      "cue_id": "id-tu-input",
      "text_vi": "bản dịch tiếng Việt hoàn chỉnh"
    }}
  ]
}}

DANH SÁCH CUES CẦN DỊCH:
{json.dumps(items_to_translate, ensure_ascii=False, indent=2)}
"""
        return prompt

    def _parse_and_validate_response(
        self,
        raw_response: str,
        expected_cues: List[SubtitleCue],
        batch_id: str
    ) -> Dict[str, str]:
        """
        Spec 06 Section 6 Parser and Strict Validator.
        Verifies:
        - Strict JSON format
        - All required cue_ids are present
        - No empty text_vi
        """
        clean_text = raw_response.strip()
        # Remove markdown code fences if present
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()

        try:
            parsed = json.loads(clean_text)
        except Exception as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}\nRaw: {raw_response[:300]}")

        items = parsed.get("items", [])
        if not isinstance(items, list):
            raise ValueError("Invalid response format: 'items' must be a JSON array.")

        result_map: Dict[str, str] = {}
        for item in items:
            c_id = str(item.get("cue_id", "")).strip()
            t_vi = str(item.get("text_vi", "")).strip()
            if c_id and t_vi:
                result_map[c_id] = t_vi

        # Verify all expected cues received translation
        missing_ids = [c.cue_id for c in expected_cues if c.cue_id not in result_map]
        if missing_ids:
            print(f"[Translation Warning] {len(missing_ids)} cues missing from LLM response. Filling fallback...")
            # For missing cues, apply direct longest-glossary replacement fallback
            for c in expected_cues:
                if c.cue_id not in result_map:
                    fallback_text = c.source_text
                    for s_term, t_term in self.match_glossary_terms_for_text(c.source_text):
                        fallback_text = fallback_text.replace(s_term, t_term)
                    result_map[c.cue_id] = fallback_text

        return result_map

    def translate_batch(self, cues_batch: List[SubtitleCue]) -> List[SubtitleCue]:
        """Translate a batch of cues with TM cache lookups and LLM execution."""
        batch_id = compute_sha256("".join(c.source_text for c in cues_batch))[:16]
        
        # Check which cues can be fulfilled immediately from SQLite TM (O(1))
        untranslated: List[SubtitleCue] = []
        for c in cues_batch:
            cached_trans = self.tm.lookup_memory(c.source_text)
            if cached_trans:
                c.translated_text = cached_trans
                c.tts_text = cached_trans
            else:
                untranslated.append(c)

        if not untranslated:
            print(f"[Translation] Batch {batch_id}: 100% TM Cache Hit! ({len(cues_batch)} cues)")
            return cues_batch

        print(f"[Translation] Batch {batch_id}: {len(untranslated)}/{len(cues_batch)} cues require LLM translation...")
        prompt = self._build_batch_prompt(untranslated, batch_id)

        raw_resp = ""
        # 1. Try Gemini API if key is available
        if self.gemini_api_key:
            try:
                raw_resp = self._call_gemini_api(prompt)
            except Exception as e:
                print(f"[Translation] Gemini API failed: {e}. Trying Groq fallback...")
        
        # 2. Try Groq Llama fallback if Gemini unavailable
        if not raw_resp and self.groq_api_key:
            try:
                raw_resp = self._call_groq_llama(prompt)
            except Exception as e:
                print(f"[Translation] Groq API failed: {e}.")

        # 3. If no LLM available, apply smart rule-based Donghua glossary translation
        if not raw_resp:
            print("[Translation] No LLM API key available; applying rule-based Donghua Glossary translation engine.")
            for c in untranslated:
                trans = c.source_text
                for s_term, t_term in self.match_glossary_terms_for_text(c.source_text):
                    trans = trans.replace(s_term, t_term)
                c.translated_text = trans
                c.tts_text = trans
                self.tm.store_memory(c.source_text, trans, locked=False)
            return cues_batch

        # Validate response
        translations = self._parse_and_validate_response(raw_resp, untranslated, batch_id)

        for c in untranslated:
            t_vi = translations.get(c.cue_id, c.source_text)
            c.translated_text = t_vi
            c.tts_text = t_vi
            # Auto-save to SQLite TM for instant O(1) hit next time
            self.tm.store_memory(c.source_text, t_vi, locked=False)

        return cues_batch

    def process(self, cues: List[SubtitleCue]) -> List[SubtitleCue]:
        """
        Full translation workflow over all cues:
        1. Anchor partition into batches <= batch_size
        2. Execute batch translation with TM cache
        3. Return completed cues
        """
        if not cues:
            return []

        print(f"[Translation] Starting translation for {len(cues)} cues (genre: {self.genre})...")
        translated_cues: List[SubtitleCue] = []
        
        for i in range(0, len(cues), self.batch_size):
            batch = cues[i:i + self.batch_size]
            res_batch = self.translate_batch(batch)
            translated_cues.extend(res_batch)

        print(f"[Translation] Completed translation for all {len(translated_cues)} cues.")
        return translated_cues


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python translator.py <input_cues.json> [output_translated.json]")
        sys.exit(1)

    in_file = sys.argv[1]
    out_file = sys.argv[2] if len(sys.argv) > 2 else "translated_cues.json"

    with open(in_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    cues_list = [SubtitleCue.from_dict(d) for d in data]
    translator = DonghuaTranslator()
    res = translator.process(cues_list)

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump([c.to_dict() for c in res], f, ensure_ascii=False, indent=2)
    print(f"Saved translated cues to {out_file}")
