# 🚀 InfiniGPT - Dataset Q&A Français Premium

[![License: CC BY 4.0](https://img.shields.io/badge/Licenses-CC_BY_4.0-yellow)
[![Dataset Size](https://img.shields.io/badge/Size-40k%2B%20Q%26A-blue.svg)](https://github.com/RDTvlokip/InfiniGPT)
[![Language](https://img.shields.io/badge/Language-Français-red.svg)](https://github.com/RDTvlokip/InfiniGPT)
[![Status](https://img.shields.io/badge/Status-En%20développement-orange.svg)](https://github.com/RDTvlokip/InfiniGPT)

> **Le plus grand dataset Q&A français créé par un étudiant indépendant** 🇫🇷

---

## 📖 Description

**InfiniGPT** est un dataset de questions-réponses en français natif, conçu pour le fine-tuning de modèles de langage. Contrairement aux datasets existants basés sur l'extraction ou la traduction, InfiniGPT propose des **Q&A directes et factuelles** validées manuellement.

### ✨ Caractéristiques principales

- 🎯 **40 000+ Q&A** (objectif : 400k+)
- 🇫🇷 **Français natif** (pas de traduction)
- 💎 **Qualité premium** - Validation manuelle intégrale
- 📚 **Ultra-diversifié** - Histoire, sciences, culture générale
- 🔍 **Sources documentées** - Traçabilité complète
- ⚡ **Format optimisé** - JSON/TSV compatible ML

---

## 🏆 Comparaison avec l'écosystème existant

| Dataset | Taille | Type | Langue | Qualité |
|---------|--------|------|--------|---------|
| **InfiniGPT** | **40k+** → **400k+** | **Q&R directes** | **🇫🇷 Natif** | **✅ Premium** |
| FQuAD 2.0 | 80k | Extractive | 🇫🇷 Natif | ✅ Bon |
| SQuAD_fr | 87k | Extractive | ❌ Traduit | ⚠️ Moyen |
| PIAF | 3.8k | Extractive | 🇫🇷 Natif | ✅ Bon |
| AlloproF | 29k | Textuelle | 🇫🇷 Natif | ✅ Éducatif |

---

## 📊 Exemples de données

```json
{
  "question": "En quelle année le siège d'Itami a-t-il débuté ?",
  "answer": "1578",
  "source": "Araki_Murashige.txt"
}

{
  "question": "Quel est l'objectif de spécifier 'Arachnactidae' ?",
  "answer": "pour indiquer la famille de l'espèce",
  "source": "Arachnactis_panikkari.txt"
}

{
  "question": "Qui a accusé Araki Murashige de trahison ?",
  "answer": "Akechi Mitsuhide",
  "source": "Araki_Murashige.txt"
}
```

### 🎯 Qualité des données

- **Questions ultra-spécifiques** : dates, noms, faits précis
- **Réponses concises** : factuelle, sans blabla
- **Sources documentées** : fichier source pour chaque Q&A
- **Domaines variés** : histoire, biologie, géographie, culture

---

## 🚀 Utilisation

### Installation rapide

```bash
# Cloner le repository
git clone [https://github.com/RDTvlokip/InfiniGPT](https://github.com/RDTvlokip/InfiniQA).git
cd InfiniQA

# Charger le dataset
import json

with open('qa_dataset.jsonl', 'r', encoding='utf-8') as f:
    dataset = [json.loads(line) for line in f]

print(f"Dataset chargé : {len(dataset)} Q&A")
```

### Format des données

**JSON** (recommandé pour ML) :
```json
[
  {
    "question": "Question ici ?",
    "answer": "Réponse précise",
    "source": "fichier_source.txt",
    "domain": "Histoire", 
    "difficulty": "Medium"
  }
]
```

**TSV** (compatible tableurs) :
```
question	answer	source	domain
En quelle année...	1578	Araki_Murashige.txt	Histoire
```

---

## 🛠️ Applications

### Fine-tuning de modèles
- **GPT-2/GPT-3** français
- **BERT/CamemBERT** pour Q&A
- **T5** français
- **LLaMA** français

### Use cases
- 🤖 **Chatbots** francophones
- 📚 **Assistants éducatifs**
- 🔍 **Moteurs de Q&A**
- 📊 **Systèmes de recommandation**

---

## 🎯 Roadmap

### Version actuelle (v1.0)
- ✅ **40 000+ Q&A** validées
- ✅ Format JSON/TSV
- ✅ Sources documentées
- ✅ Métadonnées enrichies

### Versions futures
- 🔄 **v2.0** : 100k Q&A (Q3 2025)
- 🔄 **v3.0** : 200k Q&A (Q4 2025)
- 🎯 **v4.0** : 400k Q&A (2026)
- ⚡ **Features** : Multimodal, Audio, Difficulté adaptative

---

## 📈 Métriques et Benchmarks

### Statistiques actuelles
- **Questions moyennes** : 12 mots
- **Réponses moyennes** : 3 mots
- **Domaines couverts** : 50+
- **Sources uniques** : 200+
- **Langues** : Français (99.9%)

### Benchmarks (à venir)
- **BLEU Score** vs autres datasets FR
- **Rouge Score** pour cohérence
- **Perplexité** sur modèles fine-tunés
- **Human evaluation** sur échantillon

---

## 🤝 Contribution

### Comment contribuer
1. **Fork** le projet
2. **Créer** une branche (`git checkout -b feature/nouvelle-source`)
3. **Commit** vos changements (`git commit -m 'Ajout source XYZ'`)
4. **Push** la branche (`git push origin feature/nouvelle-source`)
5. **Pull Request**

### Guidelines qualité
- ✅ Questions **spécifiques** et factuelles
- ✅ Réponses **concises** (1-5 mots idéalement)
- ✅ Sources **documentées** et vérifiables
- ❌ Pas de questions d'opinion
- ❌ Pas de réponses génériques

---

## 🏗️ Architecture technique

### Pipeline de création
```
Sources texte → Extraction Q&A → Tokenisation GPT-2 → 
Validation humaine → Métadonnées → Export JSON/TSV
```

### Technologies utilisées
- **Python 3.9+**
- **Tokenizer GPT-2** (français optimisé)
- **Pandas** pour manipulation
- **JSON/TSV** pour export
- **Git LFS** pour gros fichiers

---

## 📄 Licence

Ce projet est sous licence **CC BY 4.0** - voir le fichier [LICENSE](LICENSE.md) pour plus de détails.

```
# 📜 InfiniGPT Dataset License

## **Creative Commons Attribution 4.0 International (CC BY 4.0)**

---

### **🎯 Vous êtes libre de :**...
```

---

## 👨‍💻 Auteur

**Théo** (alias **RDTvlokip**)
- 🎓 Étudiant TSSR (Technicien Supérieur Systèmes et Réseaux) 
- 🔗 Collaboration avec LMC sur tokenizer GPT-2
- 📧 Contact : [Créer une issue](https://github.com/RDTvlokip/InfiniQA/issues)

---

## 🌟 Citations

Si vous utilisez InfiniGPT dans vos recherches, merci de citer :

```bibtex
@dataset{infinigpt2025,
  title={InfiniGPT: Large-Scale French Q&A Dataset},
  author={Théo (RDTvlokip)},
  year={2025},
  url={[URL du dataset]},
  license={CC BY 4.0}
}
```

---

## 🙏 Remerciements

- **LMC** pour la collaboration sur le tokenizer GPT-2
- **Nepsod** pour le soutien à l'innovation étudiante
- **Communauté open source** française pour l'inspiration

---

## 📊 Stats du projet

![GitHub stars](https://img.shields.io/github/stars/RDTvlokip/InfiniQA?style=social)
![GitHub forks](https://img.shields.io/github/forks/RDTvlokip/InfiniQA?style=social)
![GitHub issues](https://img.shields.io/github/issues/RDTvlokip/InfiniQA)
![GitHub last commit](https://img.shields.io/github/last-commit/RDTvlokip/InfiniQA)

---

**🚀 InfiniGPT - Révolutionner l'IA française, une Q&A à la fois !**

*Créé avec ❤️ par un étudiant passionné*
