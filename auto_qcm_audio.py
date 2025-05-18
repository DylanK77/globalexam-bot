from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from openai import OpenAI
import time
import threading
import re

# ✅ Étapes du patch :
# On détecte les questions où les réponses sont vides
# On extrait les questions + choix directement depuis la transcription
# On aligne par index (Question 11 ↔ bloc 11 de la transcription)
# On génère un prompt basé sur ce contenu au lieu de parser le HTML

# ✅ OpenAI client avec ta clé
client = OpenAI(api_key="OPEN AI API") #Clé API OpenAI -> https://platform.openai.com/usage | https://platform.openai.com/settings/organization/general
                                       #CLÉ API : https://platform.openai.com/settings/organization/api-keys
                                       
# ✅ Chemin vers ChromeDriver
chrome_path = r"C:\\Users\\TON_USER\\Documents\\globalexam-bot\\chromedriver.exe"

# ✅ Identifiants
email = "" #Email Global Exam
password = "" #Password Global Exam

# ✅ Contrôle terminal
paused = False
stop_script = False

def control_thread():
    global paused, stop_script
    while True:
        cmd = input().strip().lower()
        if cmd == "p": paused = True; print("⏸ Pause.")
        elif cmd == "r": paused = False; print("▶️ Reprise.")
        elif cmd == "exit": stop_script = True; print("⛔ Arrêt."); break

options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(chrome_path), options=options)

# Connexion
driver.get("https://auth.global-exam.com/login")
time.sleep(1)
driver.find_element(By.NAME, "email").send_keys(email)
driver.find_element(By.NAME, "password").send_keys(password)
driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
print("🔐 Connecté.")

input("👉 Lance un quiz, puis appuie sur Entrée...")
threading.Thread(target=control_thread, daemon=True).start()

try:
    while not stop_script:
        if paused:
            time.sleep(1)
            continue

        # Récup transcription
        try:
            trans_btn = driver.find_element(By.XPATH, "//button[.//span[contains(text(), 'Transcription') or contains(text(), 'Voir la transcription')]]")
            trans_btn.click()
            time.sleep(1)
            popup_elem = driver.find_element(By.CSS_SELECTOR, "p.wysiwyg.wysiwyg-spacing")
            transcription_text = popup_elem.text.strip()
            print("✅ Transcription récupérée.")
            try:
                close_btn = driver.find_element(By.CSS_SELECTOR, "button.absolute.top-0.right-0")
                close_btn.click()
                time.sleep(1)
                print("🛑 Pop-up transcription fermée.")
            except:
                print("⚠️ Impossible de fermer la pop-up transcription.")
        except:
            transcription_text = ""
            print("⚠️ Aucune transcription disponible.")

        questions = driver.find_elements(By.CSS_SELECTOR, "p.text-neutral-80.leading-tight.mb-8 > p")
        if not questions:
            questions = driver.find_elements(By.CSS_SELECTOR, "p.text-neutral-80.leading-tight.mb-8")

        for q_elem in questions:
            try:
                question_text = q_elem.text.strip()
                parent = q_elem.find_element(By.XPATH, "./../../..")
                labels = parent.find_elements(By.CSS_SELECTOR, "label.flex.items-center.justify-between")
                choices = []
                for label in labels:
                    spans = label.find_elements(By.CSS_SELECTOR, "span.text-neutral-80 > span")
                    text_parts = [s.text.strip() for s in spans if s.get_attribute("class") != "mr-1" and s.text.strip()]
                    text = " ".join(text_parts).strip()
                    if text:
                        choices.append((label, text))

                if not choices:
                    print("⚠️ Réponses vides : utilisation de la transcription")
                    match = re.search(r"Question\s*(\d+)", question_text, re.IGNORECASE)
                    if not match:
                        print("❌ Impossible d’aligner la question avec la transcription.")
                        continue
                    q_index = int(match.group(1))

                    # 🔁 Patch regex amélioré avec \r et \n multiples
                    cleaned_transcript = transcription_text.replace("\r", "")
                    q_blocks = re.findall(
                        r"(\d+)\.\s*(.*?)\s*A\.\s*(.*?)\s*B\.\s*(.*?)\s*C\.\s*(.*?)(?:\n{2,}|\Z)",
                        cleaned_transcript,
                        re.DOTALL
                    )
                    found = False
                    for num, qtext, a, b, c in q_blocks:
                        if int(num) == q_index:
                            found = True
                            choices_text = [a.strip(), b.strip(), c.strip()]
                            prompt = f"QUESTION :\n{qtext.strip()}\n\nCHOIX :\n{choices_text}\n\nRépond uniquement par le texte exact du bon choix."
                            response = client.chat.completions.create(
                                model="gpt-4.1-mini-2025-04-14",
                                messages=[{"role": "user", "content": prompt}]
                            )
                            answer = response.choices[0].message.content.strip()
                            for i, (label, _) in enumerate(zip(labels, ["A", "B", "C"])):
                                if answer.lower() in choices_text[i].lower():
                                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", label)
                                    time.sleep(1)
                                    try: label.click()
                                    except: driver.execute_script("arguments[0].click();", label)
                                    print(f"✔️ Q{num} -> {choices_text[i]}")
                                    break
                            break
                    if not found:
                        print(f"❌ Q{q_index} introuvable dans la transcription.")
                    continue

                prompt = f"TRANSCRIPTION :\n{transcription_text}\n\nQUESTION :\n{question_text}\n\nCHOIX :\n{[text for _, text in choices]}\n\nRépond uniquement par le texte exact du bon choix."
                response = client.chat.completions.create(
                    model="gpt-4.1-mini-2025-04-14",
                    messages=[{"role": "user", "content": prompt}]
                )
                answer = response.choices[0].message.content.strip()

                clicked = False
                for label, text in choices:
                    if answer.lower() in text.lower() or text.lower() in answer.lower():
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", label)
                        time.sleep(1)
                        try: label.click()
                        except: driver.execute_script("arguments[0].click();", label)
                        print(f"✔️ {question_text} -> {text}")
                        clicked = True
                        break
                if not clicked:
                    print("⚠️ Réponse IA non cochée pour :", question_text)

            except Exception as e:
                print("❌ Erreur sur une question :", e)

        try:
            buttons = driver.find_elements(By.CSS_SELECTOR, "button.button-outline-primary-large, button.button-solid-primary-large")
            for btn in buttons:
                text = btn.text.strip().lower()
                if any(k in text for k in ["valider", "passer", "suivant", "terminer"]):
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", btn)
                    time.sleep(1)
                    btn.click()
                    print(f"🟢 Bouton '{text}' cliqué.")
                    break
        except Exception as btn_err:
            print("❌ Erreur bouton :", btn_err)

        time.sleep(1)

except Exception as crash:
    print(f"\n💥 Crash général : {crash}")

driver.quit()
print("🚪 Fermeture.")
