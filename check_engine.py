from src.api.services.engine import search_engine
print(f"Has batch_search: {hasattr(search_engine, 'batch_search')}")
try:
    search_engine.batch_search(["Putin"])
    print("batch_search called successfully")
except Exception as e:
    print(f"batch_search failed: {e}")
