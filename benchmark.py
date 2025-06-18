#!/usr/bin/env python3
"""
Benchmark complet pour dataset QA avec toutes les métriques standard
Métriques : EM, ROUGE-1/2/L, BLEU-1/4, Perplexité, Diversité, Robustesse
"""

import json
import numpy as np
import math
from collections import Counter, defaultdict
import re
from typing import List, Dict, Tuple, Set
import hashlib
from difflib import SequenceMatcher
import time

ECHANTILLIONS = 175000

class CompleteBenchmark:
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.data = self.load_data()
        self.vocab = self.build_vocab()
        print(f"📊 Dataset chargé : {len(self.data)} échantillons")
    
    def load_data(self) -> List[Dict]:
        """Charge le dataset JSONL avec validation"""
        data = []
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                try:
                    item = json.loads(line.strip())
                    if "question" in item and "answer" in item:
                        data.append(item)
                    else:
                        print(f"⚠️  Ligne {i+1} : clés manquantes")
                except json.JSONDecodeError:
                    print(f"⚠️  Ligne {i+1} : JSON invalide")
        return data
    
    def build_vocab(self) -> Set[str]:
        """Construit le vocabulaire pour calcul de perplexité"""
        vocab = set()
        for item in self.data:
            vocab.update(self.tokenize(item["question"]))
            vocab.update(self.tokenize(item["answer"]))
        return vocab
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenisation robuste"""
        return re.findall(r'\w+', text.lower())
    
    def calculate_exact_match(self, reference: str, candidate: str) -> float:
        """Exact Match : 1.0 si identique, 0.0 sinon"""
        return 1.0 if reference.strip() == candidate.strip() else 0.0
    
    def calculate_bleu(self, reference: str, candidate: str, n: int = 4) -> Dict[str, float]:
        """BLEU-1 à BLEU-n avec optimisations"""
        ref_tokens = self.tokenize(reference)
        cand_tokens = self.tokenize(candidate)
        
        if len(cand_tokens) == 0:
            return {f"bleu_{i}": 0.0 for i in range(1, n+1)}
        
        # Brevity penalty
        bp = min(1.0, len(cand_tokens) / max(1, len(ref_tokens)))
        
        results = {}
        for i in range(1, n + 1):
            ref_ngrams = [tuple(ref_tokens[j:j+i]) for j in range(max(1, len(ref_tokens) - i + 1))]
            cand_ngrams = [tuple(cand_tokens[j:j+i]) for j in range(max(1, len(cand_tokens) - i + 1))]
            
            if len(cand_ngrams) == 0:
                results[f"bleu_{i}"] = 0.0
                continue
            
            ref_counter = Counter(ref_ngrams)
            cand_counter = Counter(cand_ngrams)
            
            matches = sum(min(ref_counter[ng], cand_counter[ng]) for ng in cand_counter)
            precision = matches / len(cand_ngrams)
            
            results[f"bleu_{i}"] = bp * precision if precision > 0 else 0.0
        
        return results
    
    def calculate_rouge_metrics(self, reference: str, candidate: str) -> Dict[str, Dict[str, float]]:
        """ROUGE-1, ROUGE-2, ROUGE-L en une fois"""
        ref_tokens = self.tokenize(reference)
        cand_tokens = self.tokenize(candidate)
        
        results = {}
        
        # ROUGE-1 (unigrammes)
        results["rouge_1"] = self._rouge_n(ref_tokens, cand_tokens, 1)
        
        # ROUGE-2 (bigrammes)
        results["rouge_2"] = self._rouge_n(ref_tokens, cand_tokens, 2)
        
        # ROUGE-L (LCS)
        results["rouge_l"] = self._rouge_lcs(ref_tokens, cand_tokens)
        
        return results
    
    def _rouge_n(self, ref_tokens: List[str], cand_tokens: List[str], n: int) -> Dict[str, float]:
        """ROUGE-N générique"""
        if len(ref_tokens) < n or len(cand_tokens) < n:
            return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
        
        ref_ngrams = Counter([tuple(ref_tokens[i:i+n]) for i in range(len(ref_tokens) - n + 1)])
        cand_ngrams = Counter([tuple(cand_tokens[i:i+n]) for i in range(len(cand_tokens) - n + 1)])
        
        matches = sum(min(ref_ngrams[ng], cand_ngrams[ng]) for ng in cand_ngrams)
        
        precision = matches / sum(cand_ngrams.values()) if sum(cand_ngrams.values()) > 0 else 0.0
        recall = matches / sum(ref_ngrams.values()) if sum(ref_ngrams.values()) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {"precision": precision, "recall": recall, "f1": f1}
    
    def _rouge_lcs(self, ref_tokens: List[str], cand_tokens: List[str]) -> Dict[str, float]:
        """ROUGE-L avec LCS optimisé"""
        if len(ref_tokens) == 0 or len(cand_tokens) == 0:
            return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
        
        # LCS avec matrice DP
        lcs_matrix = [[0] * (len(cand_tokens) + 1) for _ in range(len(ref_tokens) + 1)]
        
        for i in range(1, len(ref_tokens) + 1):
            for j in range(1, len(cand_tokens) + 1):
                if ref_tokens[i-1] == cand_tokens[j-1]:
                    lcs_matrix[i][j] = lcs_matrix[i-1][j-1] + 1
                else:
                    lcs_matrix[i][j] = max(lcs_matrix[i-1][j], lcs_matrix[i][j-1])
        
        lcs_length = lcs_matrix[len(ref_tokens)][len(cand_tokens)]
        
        precision = lcs_length / len(cand_tokens)
        recall = lcs_length / len(ref_tokens)
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {"precision": precision, "recall": recall, "f1": f1}
    
    def calculate_perplexity(self, text_list: List[str]) -> float:
        """Perplexité approximative basée sur fréquence des mots"""
        if not text_list:
            return float('inf')
        
        # Compte des mots dans le corpus
        word_counts = Counter()
        total_words = 0
        
        for text in text_list:
            tokens = self.tokenize(text)
            word_counts.update(tokens)
            total_words += len(tokens)
        
        if total_words == 0:
            return float('inf')
        
        # Calcul de la perplexité
        log_prob_sum = 0.0
        for text in text_list:
            tokens = self.tokenize(text)
            for token in tokens:
                prob = word_counts[token] / total_words
                log_prob_sum += math.log(prob) if prob > 0 else -10  # Lissage
        
        avg_log_prob = log_prob_sum / total_words
        return math.exp(-avg_log_prob)
    
    def analyze_diversity(self) -> Dict:
        """Analyse de diversité du dataset"""
        questions = [item["question"] for item in self.data]
        answers = [item["answer"] for item in self.data]
        
        # Longueurs
        q_lengths = [len(self.tokenize(q)) for q in questions]
        a_lengths = [len(self.tokenize(a)) for a in answers]
        
        # Vocabulaire unique
        q_vocab = set()
        a_vocab = set()
        for q, a in zip(questions, answers):
            q_vocab.update(self.tokenize(q))
            a_vocab.update(self.tokenize(a))
        
        # Domaines approximatifs (mots-clés)
        domain_keywords = {
            "science": ["science", "physique", "chimie", "biologie", "mathématiques"],
            "histoire": ["histoire", "guerre", "année", "siècle", "ancien"],
            "géographie": ["pays", "ville", "continent", "montagne", "rivière"],
            "culture": ["livre", "film", "musique", "art", "littérature"],
            "sport": ["sport", "football", "match", "équipe", "joueur"],
            "technologie": ["ordinateur", "internet", "logiciel", "données", "algorithme"]
        }
        
        domain_counts = defaultdict(int)
        for item in self.data:
            text = (item["question"] + " " + item["answer"]).lower()
            for domain, keywords in domain_keywords.items():
                if any(kw in text for kw in keywords):
                    domain_counts[domain] += 1
                    break
            else:
                domain_counts["autre"] += 1
        
        return {
            "total_samples": len(self.data),
            "avg_question_length": np.mean(q_lengths),
            "avg_answer_length": np.mean(a_lengths),
            "question_vocab_size": len(q_vocab),
            "answer_vocab_size": len(a_vocab),
            "total_vocab_size": len(q_vocab | a_vocab),
            "domain_distribution": dict(domain_counts)
        }
    
    def analyze_robustness(self) -> Dict:
        """Analyse de robustesse : doublons, ambiguïté"""
        questions = [item["question"] for item in self.data]
        answers = [item["answer"] for item in self.data]
        
        # Détection de doublons (hash MD5)
        q_hashes = [hashlib.md5(q.encode()).hexdigest() for q in questions]
        a_hashes = [hashlib.md5(a.encode()).hexdigest() for a in answers]
        
        duplicate_questions = len(q_hashes) - len(set(q_hashes))
        duplicate_answers = len(a_hashes) - len(set(a_hashes))
        
        # Réponses ambiguës
        ambiguous_words = ["peut-être", "dépend", "probablement", "possible", "incertain", "environ"]
        ambiguous_count = sum(1 for a in answers if any(word in a.lower() for word in ambiguous_words))
        
        # Similarité élevée (>90%)
        similar_pairs = 0
        sample_size = min(1000, len(questions))  # Échantillon pour performance
        for i in range(sample_size):
            for j in range(i+1, sample_size):
                similarity = SequenceMatcher(None, questions[i], questions[j]).ratio()
                if similarity > 0.9:
                    similar_pairs += 1
        
        return {
            "duplicate_questions": duplicate_questions,
            "duplicate_answers": duplicate_answers,
            "duplicate_rate": (duplicate_questions + duplicate_answers) / (2 * len(self.data)),
            "ambiguous_answers": ambiguous_count,
            "ambiguous_rate": ambiguous_count / len(self.data),
            "similar_pairs_sample": similar_pairs,
            "estimated_similarity_rate": similar_pairs / (sample_size * (sample_size-1) / 2)
        }
    
    def benchmark_model(self, model_answers: List[str], subset_size: int = None) -> Dict:
        """Benchmark complet avec toutes les métriques"""
        start_time = time.time()
        
        # Validation des données
        if subset_size:
            data_subset = self.data[:subset_size]
            if len(model_answers) != subset_size:
                raise ValueError(f"Taille incohérente : {len(model_answers)} réponses != {subset_size} échantillons")
        else:
            data_subset = self.data
            if len(model_answers) != len(self.data):
                raise ValueError(f"Taille incohérente : {len(model_answers)} réponses != {len(self.data)} échantillons")
        
        print(f"🔄 Benchmark en cours sur {len(data_subset)} échantillons...")
        
        # Initialisation des scores
        em_scores = []
        bleu_scores = defaultdict(list)
        rouge_scores = defaultdict(lambda: defaultdict(list))
        
        # Calcul des métriques
        for i, (item, pred_answer) in enumerate(zip(data_subset, model_answers)):
            if i % 10000 == 0 and i > 0:
                print(f"   Progression : {i}/{len(data_subset)} ({i/len(data_subset)*100:.1f}%)")
            
            true_answer = item["answer"]
            
            # Exact Match
            em_scores.append(self.calculate_exact_match(true_answer, pred_answer))
            
            # BLEU
            bleu_results = self.calculate_bleu(true_answer, pred_answer)
            for key, value in bleu_results.items():
                bleu_scores[key].append(value)
            
            # ROUGE
            rouge_results = self.calculate_rouge_metrics(true_answer, pred_answer)
            for rouge_type, metrics in rouge_results.items():
                for metric, value in metrics.items():
                    rouge_scores[rouge_type][metric].append(value)
        
        # Perplexité
        perplexity = self.calculate_perplexity(model_answers)
        
        # Moyennes finales
        final_results = {
            "exact_match": np.mean(em_scores),
            "bleu": {key: np.mean(scores) for key, scores in bleu_scores.items()},
            "rouge": {rouge_type: {metric: np.mean(scores) for metric, scores in metrics.items()} 
                     for rouge_type, metrics in rouge_scores.items()},
            "perplexity": perplexity,
            "total_samples": len(data_subset),
            "processing_time": time.time() - start_time
        }
        
        return final_results
    
    def print_results(self, results: Dict, diversity: Dict = None, robustness: Dict = None):
        """Affichage formaté des résultats"""
        print(f"\n🎯 RÉSULTATS BENCHMARK ({results['total_samples']} échantillons)")
        print("=" * 60)
        
        # Métriques principales
        print(f"📊 EXACT MATCH    : {results['exact_match']:.4f}")
        print(f"📊 PERPLEXITÉ     : {results['perplexity']:.2f}")
        
        # BLEU
        print(f"\n📈 BLEU SCORES:")
        for key, value in results['bleu'].items():
            print(f"   {key.upper()}: {value:.4f}")
        
        # ROUGE
        print(f"\n📈 ROUGE SCORES:")
        for rouge_type, metrics in results['rouge'].items():
            print(f"   {rouge_type.upper()}:")
            for metric, value in metrics.items():
                print(f"      {metric}: {value:.4f}")
        
        # Diversité
        if diversity:
            print(f"\n🌈 DIVERSITÉ:")
            print(f"   Questions moy: {diversity['avg_question_length']:.1f} mots")
            print(f"   Réponses moy : {diversity['avg_answer_length']:.1f} mots")
            print(f"   Vocabulaire  : {diversity['total_vocab_size']} mots uniques")
            print(f"   Domaines principaux:")
            for domain, count in sorted(diversity['domain_distribution'].items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"      {domain}: {count} ({count/diversity['total_samples']*100:.1f}%)")
        
        # Robustesse
        if robustness:
            print(f"\n🛡️  ROBUSTESSE:")
            print(f"   Doublons     : {robustness['duplicate_rate']*100:.2f}%")
            print(f"   Ambiguïté    : {robustness['ambiguous_rate']*100:.2f}%")
            print(f"   Similarité   : {robustness['estimated_similarity_rate']*100:.2f}%")
        
        print(f"\n⏱️  Temps de traitement : {results['processing_time']:.1f}s")
        print("=" * 60)

# Exemple d'utilisation
if __name__ == "__main__":
    # Initialisation
    benchmark = CompleteBenchmark("output/qa_dataset.jsonl")
    
    # Analyse préliminaire
    print("🔍 Analyse de diversité...")
    diversity = benchmark.analyze_diversity()
    
    print("🔍 Analyse de robustesse...")
    robustness = benchmark.analyze_robustness()
    
    # Test avec réponses parfaites (100 échantillons)
    print("\n🧪 Test avec réponses parfaites...")
    perfect_answers = [item["answer"] for item in benchmark.data[:ECHANTILLIONS]]
    results = benchmark.benchmark_model(perfect_answers, subset_size=ECHANTILLIONS)
    benchmark.print_results(results, diversity, robustness)
    
    # Test avec réponses modifiées
    print("\n🧪 Test avec réponses modifiées...")
    modified_answers = [item["answer"] + " (test)" for item in benchmark.data[:ECHANTILLIONS]]
    results2 = benchmark.benchmark_model(modified_answers, subset_size=ECHANTILLIONS)
    benchmark.print_results(results2)
    
    print("\n✅ Benchmark terminé !")