from agent_gemini import correct_with_gemini

if __name__ == "__main__":
    success, message = correct_with_gemini("/app/scripts/test_script.py")
    print("✅ Succès" if success else "❌ Échec")
    print("--- Résultat ---")
    print(message)
