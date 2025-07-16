#!/usr/bin/env python3
"""
Script de test manuel pour valider tous les composants
Placer à la racine du projet et exécuter: python test_manual.py
"""

import sys
import os

# Ajouter le répertoire courant au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test des imports de base"""
    print("\n=== Test Imports de Base ===")
    try:
        import fastapi
        print(f"✅ FastAPI version: {fastapi.__version__}")
    except ImportError as e:
        print(f"❌ FastAPI: {e}")
        return False
    
    try:
        import uvicorn
        print(f"✅ Uvicorn importé")
    except ImportError as e:
        print(f"❌ Uvicorn: {e}")
        return False
    
    try:
        from openai import OpenAI
        print("✅ OpenAI v1.x importé correctement")
    except ImportError as e:
        print(f"❌ OpenAI: {e}")
        return False
    
    try:
        import numpy
        import sklearn
        print("✅ NumPy et Scikit-learn OK")
    except ImportError as e:
        print(f"❌ ML libraries: {e}")
        return False
    
    try:
        import pytest
        print(f"✅ Pytest version: {pytest.__version__}")
    except ImportError as e:
        print(f"❌ Pytest: {e}")
        return False
    
    try:
        import locust
        print("✅ Locust importé")
    except ImportError as e:
        print(f"❌ Locust: {e}")
        return False
    
    return True

def test_sanitization():
    """Test du module sanitization"""
    print("\n=== Test Sanitization ===")
    try:
        from app.core.sanitization import Sanitizer
        
        # Test normal
        result = Sanitizer.sanitize_input("Hello world")
        print(f"✅ Sanitisation normale: '{result}'")
        
        # Test HTML
        result = Sanitizer.sanitize_input("<script>alert('test')</script>Hello")
        print(f"✅ Suppression HTML: '{result}'")
        
        # Test output sanitization
        result = Sanitizer.sanitize_output("Hello\x00World\x1F")
        print(f"✅ Sanitisation output: '{result}'")
        
        # Test longueur (devrait échouer)
        try:
            long_text = "a" * 1500
            Sanitizer.sanitize_input(long_text)
            print("❌ Validation longueur a échoué")
            return False
        except ValueError:
            print("✅ Validation longueur fonctionne")
        
        print("✅ Module sanitization fonctionne")
        return True
    except Exception as e:
        print(f"❌ Erreur sanitization: {e}")
        return False

def test_similarity():
    """Test du module similarity"""
    print("\n=== Test Similarity Calculator ===")
    try:
        from app.core.similarity import SimilarityCalculator
        
        calc = SimilarityCalculator()
        
        # Test cosine
        score = calc.cosine_sim("artificial intelligence", "machine learning")
        print(f"✅ Cosine similarity: {score:.4f}")
        if not (0 <= score <= 1):
            print("❌ Score cosine hors limite")
            return False
        
        # Test jaccard
        score = calc.jaccard_sim("hello world", "world hello")
        print(f"✅ Jaccard similarity: {score:.4f}")
        if not (0 <= score <= 1):
            print("❌ Score jaccard hors limite")
            return False
        
        # Test textes identiques
        score = calc.cosine_sim("test", "test")
        print(f"✅ Textes identiques: {score:.4f}")
        if score < 0.9:  # Devrait être proche de 1
            print("❌ Score textes identiques trop bas")
            return False
        
        # Test LLM fallback (sans clé API)
        score = calc.llm_based_sim("test", "test")
        print(f"✅ LLM-based similarity: {score:.4f}")
        
        print("✅ Module similarity fonctionne")
        return True
    except Exception as e:
        print(f"❌ Erreur similarity: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_llm_proxy():
    """Test du module LLM proxy"""
    print("\n=== Test LLM Proxy ===")
    try:
        from app.core.llm_proxy import LLMClient
        
        client = LLMClient()
        print(f"✅ LLM Client initialisé (model: {client.model})")
        
        # Test sans clé API (devrait donner un message d'erreur propre)
        response = client.generate("Hello")
        print(f"✅ Generate response: '{response[:50]}...'")
        
        # Vérifier que c'est soit une erreur propre soit une vraie réponse
        if "not configured" in response or "Error" in response or len(response) > 10:
            print("✅ Réponse LLM appropriée")
        else:
            print("❌ Réponse LLM inattendue")
            return False
        
        # Test similarity sans clé API
        score = client.similarity("test", "test")
        print(f"✅ LLM similarity: {score}")
        if not (0 <= score <= 1):
            print("❌ Score LLM hors limite")
            return False
        
        print("✅ Module LLM proxy fonctionne")
        return True
    except Exception as e:
        print(f"❌ Erreur LLM proxy: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config():
    """Test du module configuration"""
    print("\n=== Test Configuration ===")
    try:
        from app.config import Config
        
        print(f"✅ PORT: {Config.PORT}")
        print(f"✅ SIMILARITY_THRESHOLD: {Config.SIMILARITY_THRESHOLD}")
        print(f"✅ DEFAULT_METRIC: {Config.DEFAULT_METRIC}")
        print(f"✅ LLM_MODEL: {Config.LLM_MODEL}")
        print(f"✅ MAX_INPUT_LENGTH: {Config.MAX_INPUT_LENGTH}")
        
        # Test validation
        issues = Config.validate()
        if issues:
            print("⚠️  Configuration warnings:")
            for issue in issues:
                print(f"  - {issue}")
            # Les warnings sont OK, pas d'erreur bloquante
        else:
            print("✅ Configuration parfaite")
        
        # Vérifier les valeurs critiques
        if Config.SIMILARITY_THRESHOLD < 0 or Config.SIMILARITY_THRESHOLD > 1:
            print("❌ SIMILARITY_THRESHOLD invalide")
            return False
        
        if Config.MAX_INPUT_LENGTH <= 0:
            print("❌ MAX_INPUT_LENGTH invalide")
            return False
        
        print("✅ Module config fonctionne")
        return True
    except Exception as e:
        print(f"❌ Erreur config: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_imports():
    """Test des imports API"""
    print("\n=== Test API Imports ===")
    try:
        from app.api.endpoints import router
        print("✅ API endpoints importés")
        
        from app.main import app
        print("✅ FastAPI app importée")
        
        # Vérifier que l'app a les bonnes routes
        routes = [route.path for route in app.routes]
        print(f"✅ Routes disponibles: {routes}")
        
        if "/api/similarity-check" not in str(routes):
            print("❌ Route similarity-check manquante")
            return False
        
        print("✅ Module API fonctionne")
        return True
    except Exception as e:
        print(f"❌ Erreur API imports: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_structure():
    """Test de la structure des fichiers"""
    print("\n=== Test Structure Fichiers ===")
    required_files = [
        "app/__init__.py",
        "app/main.py", 
        "app/config.py",
        "app/core/__init__.py",
        "app/core/similarity.py",
        "app/core/sanitization.py", 
        "app/core/llm_proxy.py",
        "app/api/__init__.py",
        "app/api/endpoints.py",
        "tests/load_test/locustfile.py",
        "requirements.txt",
        "Dockerfile"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} manquant")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ {len(missing_files)} fichiers manquants")
        return False
    
    print("✅ Structure des fichiers OK")
    return True

def main():
    """Fonction principale"""
    print("🧪 DÉMARRAGE DES TESTS MANUELS")
    print("=" * 50)
    
    # Liste des tests à exécuter
    tests = [
        ("Structure fichiers", test_file_structure),
        ("Imports de base", test_imports),
        ("Configuration", test_config),
        ("Sanitization", test_sanitization),
        ("Similarity", test_similarity),
        ("LLM Proxy", test_llm_proxy),
        ("API Imports", test_api_imports)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Exécution: {test_name}")
        print("-" * 30)
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} RÉUSSI")
            else:
                print(f"❌ {test_name} ÉCHOUÉ")
        except Exception as e:
            print(f"❌ Erreur dans {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé final
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS DES TESTS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ RÉUSSI" if result else "❌ ÉCHOUÉ"
        print(f"{test_name:20} : {status}")
        if result:
            passed += 1
    
    print("-" * 50)
    print(f"Total: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 TOUS LES TESTS PASSENT !")
        print("✅ Le service est prêt à être démarré")
        print("\nProchaines étapes:")
        print("1. uvicorn app.main:app --port 8003")
        print("2. Tester l'API avec curl ou le navigateur")
        return True
    else:
        print("⚠️  CERTAINS TESTS ÉCHOUENT")
        print("❌ Corrigez les erreurs avant de continuer")
        print("\nActions recommandées:")
        if passed < total // 2:
            print("- Vérifiez que tous les fichiers sont présents")
            print("- Réinstallez les dépendances: pip install -r requirements.txt")
        else:
            print("- Vérifiez les modules qui échouent")
            print("- Consultez les messages d'erreur ci-dessus")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)