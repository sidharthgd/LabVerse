from qa_agent import setup_qa

if __name__ == "__main__":
    process_query = setup_qa()

    while True:
        query = input("\nAsk LabVerse something (or type 'exit'): ")
        if query.lower() == 'exit':
            break
        answer = process_query(query)
        print(f"\nAnswer: {answer}")