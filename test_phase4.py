import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.pipelines.adaptive_rag_pipeline import adaptive_retrieve


query = (
    "Explain the five building blocks that help maximise "
    "Customer Lifetime Value (CLV), and describe the role "
    "of each building block."
)

result = adaptive_retrieve(
    query=query,
    source="Module 4.pdf",
)

print("=" * 70)
print("PHASE 4 EVIDENCE INSPECTION")
print("=" * 70)

print("Adaptive status:", result["adaptive_status"])
print("Iterations:", result["iterations"])
print("Final sufficient:", result["validation"]["sufficient"])
print("Final coverage:", result["validation"]["coverage_score"])
print("Missing requirements:",
      result["validation"].get("missing_requirements", []))

print()
print("=" * 70)
print("DISCOVERED ITEMS")
print("=" * 70)

for item in result["validation"].get("discovered_items", []):
    print("-", item)

print()
print("=" * 70)
print("FINAL SELECTED EVIDENCE")
print("=" * 70)

for i, document in enumerate(result["evidence"], start=1):

    print()
    print("-" * 70)
    print(f"EVIDENCE {i}")
    print("-" * 70)

    print("Source:", document.meta.get("source"))
    print("Page:", document.meta.get("page_number"))
    print("Chunk:", document.meta.get("chunk_number"))
    print("Score:", document.score)

    print()
    print(document.content)