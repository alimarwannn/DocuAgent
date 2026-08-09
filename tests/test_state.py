from src.state import DocumentState

state: DocumentState = {
    "image_path": "samples/receipt_1.jpg",
    "scan_mode": "full",
}

assert state["image_path"] == "samples/receipt_1.jpg"
assert state["scan_mode"] == "full"

print("DocumentState test passed.")
print(state)