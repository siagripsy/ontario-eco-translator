from pathlib import Path


KNOWLEDGE_DIR = Path("data/knowledge")
LEGACY_KNOWLEDGE_FILE = KNOWLEDGE_DIR / "ontario_electricity.txt"
COMMON_KNOWLEDGE_FILE = KNOWLEDGE_DIR / "common_ontario_electricity.txt"
PLAN_KNOWLEDGE_FILES = {
    "ULO": KNOWLEDGE_DIR / "plan_ulo.txt",
    "TOU": KNOWLEDGE_DIR / "plan_tou.txt",
    "Tiered": KNOWLEDGE_DIR / "plan_tiered.txt",
}


def _read_text_file(file_path: Path) -> str:
    try:
        return file_path.read_text(encoding="utf-8").strip()
    except Exception:
        return ""


def load_common_knowledge() -> str:
    common_knowledge = _read_text_file(COMMON_KNOWLEDGE_FILE)
    if common_knowledge:
        return common_knowledge
    return _read_text_file(LEGACY_KNOWLEDGE_FILE)


def load_plan_specific_knowledge(plan: str) -> str:
    file_path = PLAN_KNOWLEDGE_FILES.get(plan)
    if not file_path:
        return ""
    return _read_text_file(file_path)


def build_fallback_plan_knowledge() -> str:
    sections: list[str] = []
    for plan in ("TOU", "ULO", "Tiered"):
        plan_text = load_plan_specific_knowledge(plan)
        if plan_text:
            sections.append(f"{plan} plan summary:\n{plan_text}")
    return "\n\n".join(sections)
