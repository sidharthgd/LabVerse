from indexer import scan_directory
from embedder import embed_metadata
from archive.search import search

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--query", help="Ask a question")
    parser.add_argument("--data", default="data", help="Path to data directory")
    args = parser.parse_args()

    print("🧠 Scanning directory...")
    metadata = scan_directory(args.data)

    print("📦 Embedding files...")
    embed_metadata(metadata)

    if args.query:
        print(f"\n🔍 Top results for: {args.query}\n")
        results = search(args.query)
        for r in results:
            print(f"- {r['file']}: {r['columns']}")
            print(f"  Sample: {r['sample'][:1]}")
            print()
