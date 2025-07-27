from agent_ruf import correct_with_ruf

if __name__ == "__main__":
    success, message = correct_with_ruf("/app/scripts/test_script.py")
    print("✅ Succès" if success else "❌ Échec")
    print("--- Résultat ---")
    print(message)
