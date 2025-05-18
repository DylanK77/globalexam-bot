# 🤖 GlobalExam Bot – QCM Automatisé avec OpenAI

> **⚠️ Ce projet n’est pas conçu pour tricher ou contourner un système d’examen. Il s’agit d’un outil expérimental, à but strictement éducatif et personnel, visant à apprendre à utiliser Selenium et l’API OpenAI dans un environnement technique.**

---

## ⚠️ Utilisation à vos risques

> **L’auteur de ce projet, DylanK77, décline toute responsabilité quant à l’usage qui pourrait en être fait par des tiers.**  
> Ce code a été développé dans un cadre strictement personnel, expérimental et éducatif, **sans aucune visée commerciale, frauduleuse ou d’évaluation réelle**.

> En publiant ce projet, **l’auteur n’encourage, ne soutient, ni ne facilite la triche**, l’automatisation non autorisée de services tiers, ni toute activité pouvant contrevenir aux Conditions Générales d’Utilisation de plateformes telles que GlobalExam.  

> **Toute personne utilisant ce code en dehors d’un cadre local, personnel et non lucratif agit sous sa seule et entière responsabilité**, et s’engage à :
> - respecter les CGU des plateformes concernées,
> - ne pas utiliser ce code dans un cadre d’évaluation réelle,
> - ne pas exploiter ou redistribuer ce code dans un but commercial ou frauduleux.

> En utilisant ce code, l’utilisateur reconnaît expressément que :
> - **l’auteur ne peut être tenu responsable** des conséquences directes ou indirectes de l’utilisation de ce projet,
> - l’usage de ce code peut **contrevenir aux règles internes** de certaines plateformes, même à des fins personnelles.

> **Ce projet ne constitue en aucun cas une incitation à automatiser, scraper, ou contourner les mécanismes de protection mis en place par des services tiers.**

---

## 📘 Présentation

Projet d’automatisation de QCM sur [GlobalExam](https://www.global-exam.com/) à l’aide de **Selenium** et de l’**API OpenAI**.  
Ce script est un **prototype expérimental personnel** réalisé dans un but d’**apprentissage**.

Deux modules inclus :

- `auto_qcm_ecrit.py` : Pour les QCM écrits (1 question par page), avec support image ou texte.
- `auto_qcm_audio.py` : Pour les QCM audio (plusieurs questions par page), avec récupération de transcription automatique.
- 
> ℹ️ Le script `auto_qcm_audio.py` est volontairement conçu pour fonctionner **uniquement sur les exercices d'entraînement** de la plateforme GlobalExam, et **pas pendant les examens notés**.  
> Cette restriction a été intégrée **intentionnellement** afin de garantir un usage strictement éducatif, sans possibilité de triche ou de contournement des évaluations officielles.

> ⚠️ Le script `auto_qcm_ecrit.py` n’a pas été conçu spécifiquement pour détecter si l’utilisateur se trouve en **mode examen ou exercice**.  
> Son usage est donc **réservé uniquement aux sessions d’entraînement** dans un objectif personnel, éducatif et non évaluatif.  
> L’auteur **déconseille strictement** toute tentative d’utilisation en condition d’examen.

---

## 📦 Installation

### 1. Cloner le dépôt
```bash
git clone https://github.com/ton-user/globalexam-bot.git
cd globalexam-bot
```

### 2. Installer les dépendances Python
```bash
py -m pip install openai
```
**ou**
```bash
python -m pip install openai
```

Puis :
```bash
python -m pip install selenium
```

> Ou en une seule commande :
```bash
pip install openai selenium
```

### 3. Télécharger [ChromeDriver](https://chromedriver.chromium.org/downloads)  
Assure-toi que la version correspond à ton navigateur, puis adapte le chemin dans les scripts :
```python
chrome_path = r"C:\\Users\\TON_USER\\Documents\\globalexam-bot\\chromedriver.exe"
```

---

## 🔐 Configuration

Modifier dans les scripts (`auto_qcm_ecrit.py`, `auto_qcm_audio.py`) :

- `email` → ton identifiant GlobalExam  
- `password` → ton mot de passe  
- `api_key` → ta clé OpenAI

---

## 🚀 Utilisation

### Lancer un QCM écrit (1 question par page) :
```bash
python auto_qcm_ecrit.py
```

### Lancer un QCM audio (plusieurs questions par page) :
```bash
python auto_qcm_audio.py
```

---

## ⌨️ Contrôles en direct

Pendant l’exécution dans le terminal :

- `p` → Pause  
- `r` → Reprendre  
- `exit` → Quitter

---

## ⚙️ Fonctionnement

- Lance Chrome automatiquement  
- Se connecte à ton compte GlobalExam  
- Attend que tu démarres un quiz  
- Analyse les questions, récupère les choix  
- Utilise GPT (OpenAI) pour déterminer la bonne réponse  
- Coche la réponse automatiquement, passe à la suite  
- Répète jusqu’à la fin du test

---

## ⚠️ Avertissement & Responsabilité

> Ce projet est fourni à des fins **éducatives et expérimentales uniquement**.  
> Il a été développé pour me familiariser avec **l’API OpenAI** dans un contexte technique personnel.  
> Il ne doit **en aucun cas être utilisé dans un cadre de triche, d’examen ou d’évaluation réelle**.  
> L’usage automatisé de plateformes comme GlobalExam peut **violer leurs Conditions Générales d’Utilisation (CGU)**.  
> **L’auteur ne pourra être tenu responsable** des usages abusifs ou détournés du script par des tiers.

---

## 📄 Licence

Ce projet est distribué sous licence **MIT modifiée** avec clause de non-responsabilité.  
[LIRE LA LICENCE](./LICENSE)

---

## 🧠 Auteur

Alias : **DylanK77**  
