import os
import re
from pathlib import Path

# Root directory for new subjects
root = Path("master_upsc_processing/Books/NCERT_Books")
subjects = ["economic", "sociology"]

for subject_folder in subjects:
    subject_path = root / subject_folder
    if not subject_path.exists():
        continue
    for class_dir in subject_path.iterdir():
        if not class_dir.is_dir() or class_dir.name.startswith('.'):
            continue
        class_num = class_dir.name
        for book_dir in class_dir.iterdir():
            if not book_dir.is_dir() or book_dir.name.startswith('.'):
                continue
            book_name = book_dir.name.replace(' ', '_').lower()
            for file in book_dir.iterdir():
                if not file.is_file() or not file.name.lower().endswith('.pdf'):
                    continue
                # Glossary
                if 'glossary' in file.name.lower():
                    new_name = f"{subject_folder.replace('economic', 'economics')}_class_{class_num}_book_{book_name}_glossary.pdf"
                else:
                    # Extract chapter number from filename (last two digits before .pdf)
                    match = re.search(r'(\d{2})\.pdf$', file.name)
                    if match:
                        chapter_number = int(match.group(1))
                        new_name = f"{subject_folder.replace('economic', 'economics')}_class_{class_num}_book_{book_name}_chapter_{chapter_number}.pdf"
                    else:
                        print(f"❓ Skipping (no chapter number found): {file}")
                        continue
                new_path = file.parent / new_name
                if file.name != new_name:
                    print(f"🔄 Renaming {file.name} -> {new_name}")
                    os.rename(file, new_path)
                else:
                    print(f"✅ Already correct: {file.name}")

# Also handle class 12 economics special folders
special_12_folders = [
    ("INTRODUCTORY MACROECONOMICS", "introductory_macroeconomics"),
    ("INTRODUCTORY MICROECONOMICS", "introductory_microeconomics")
]
class12_path = root / "economic" / "12"
for folder_name, book_name in special_12_folders:
    book_dir = class12_path / folder_name
    if not book_dir.exists():
        continue
    for file in book_dir.iterdir():
        if not file.is_file() or not file.name.lower().endswith('.pdf'):
            continue
        if 'glossary' in file.name.lower():
            new_name = f"economics_class_12_book_{book_name}_glossary.pdf"
        else:
            match = re.search(r'(\d{2})\.pdf$', file.name)
            if match:
                chapter_number = int(match.group(1))
                new_name = f"economics_class_12_book_{book_name}_chapter_{chapter_number}.pdf"
            else:
                print(f"❓ Skipping (no chapter number found): {file}")
                continue
        new_path = file.parent / new_name
        if file.name != new_name:
            print(f"🔄 Renaming {file.name} -> {new_name}")
            os.rename(file, new_path)
        else:
            print(f"✅ Already correct: {file.name}") 