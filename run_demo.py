from processor import process_file


def main():
    test_bytes = b"supplier,product,price\nAcme,Widget,9.99"

    results = process_file(test_bytes)

    assert isinstance(results, list), "process_file did not return a list"
    assert results, "Expected at least one record"
    assert results[0]["title"] == "Acme", f"Expected Acme, got {results[0]['title']}"

    print("demo ok")
    print(results)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
