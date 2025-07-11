            # Count existing questions
            cursor.execute("SELECT COUNT(*) FROM questions WHERE year = 2024")
            result = cursor.fetchone()
            existing_count = result[0] if result else 0
            print(f"Found {existing_count} existing 2024 questions")