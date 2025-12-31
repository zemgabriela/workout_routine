import os
import json
import re

# ---------------- CONFIG ---------------- #
INPUT_DIR = "kettlebell_exercises"
OUTPUT_FILE = "exercises.json"


def clean_text(text):
    """Normalize whitespace and remove weird characters."""
    return re.sub(r"\s+", " ", text).strip()


def parse_exercise_file(filepath):
    """Parse a single exercise text file."""
    data = {
        "name": "",
        "description": "",
        "muscles": "",
        "image": ""
    }

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line.startswith("Name:"):
                data["name"] = clean_text(line.replace("Name:", "", 1))

            elif line.startswith("Description:"):
                data["description"] = clean_text(line.replace("Description:", "", 1))

            elif line.startswith("Muscle Group:"):
                data["muscles"] = clean_text(line.replace("Muscle Group:", "", 1))

            elif line.startswith("Image:"):
                img = clean_text(line.replace("Image:", "", 1))
                data["image"] = img.replace("\\", "/")

    return data


def main():
    exercises = []

    for file in sorted(os.listdir(INPUT_DIR)):
        if file.endswith(".txt"):
            path = os.path.join(INPUT_DIR, file)
            exercise = parse_exercise_file(path)

            # Skip empty entries
            if exercise["name"]:
                exercises.append(exercise)

    # Save JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(exercises, f, indent=4, ensure_ascii=False)

    print(f"✅ Created {OUTPUT_FILE} with {len(exercises)} exercises.")


if __name__ == "__main__":
    main()