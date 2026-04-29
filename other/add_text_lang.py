import json

while True:
    text_input = input("input text: ")

    #read data
    with open("lang/en.json", "r") as f:
        data = json.load(f)

    with open("lang/en.json", "w") as f:
        data[text_input] = text_input

        json.dump(data, f, indent=4)
