from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from openai import OpenAI
import time
import threading
import re
import requests
import base64
from io import BytesIO

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
        if cmd == "p":
            paused = True
            print("⏸ Pause.")
        elif cmd == "r":
            paused = False
            print("▶️ Reprise.")
        elif cmd == "exit":
            stop_script = True
            print("⛔ Arrêt.")
            break

# ✅ Setup navigateur
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(chrome_path), options=options)

# ✅ Connexion à GlobalExam
driver.get("https://auth.global-exam.com/login")
time.sleep(2)
driver.find_element(By.NAME, "email").send_keys(email)
driver.find_element(By.NAME, "password").send_keys(password)
driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
print("🔐 Connecté.")

input("👉 Lance un quiz, puis appuie sur Entrée...")

threading.Thread(target=control_thread, daemon=True).start()

try:
    while not stop_script:
        if paused:
            time.sleep(5)
            continue

        time.sleep(5)

        image_block = driver.find_elements(By.CSS_SELECTOR, "div[data-support-id] img")
        image_base64 = None
        if image_block:
            try:
                img_url = image_block[0].get_attribute("src")
                response = requests.get(img_url)
                image_base64 = base64.b64encode(response.content).decode()
                print("🖼️ Image téléchargée et encodée.")
            except:
                print("⚠️ Erreur de téléchargement ou d'encodage de l'image.")
                image_base64 = None

        wysiwyg_text = ""
        try:
            wysiwyg_elem = driver.find_element(By.CSS_SELECTOR, "div.wysiwyg")
            wysiwyg_text = wysiwyg_elem.text.strip()
            print("📚 Texte wysiwyg détecté.")
        except:
            pass

        question_blocks = driver.find_elements(By.CSS_SELECTOR, "div.card.mb-4")
        if not question_blocks:
            question_blocks = driver.find_elements(By.CSS_SELECTOR, "div.w-full")

        if question_blocks:
            print(f"🔍 {len(question_blocks)} blocs de questions détectés.")
            for block in question_blocks:
                if paused or stop_script:
                    break

                try:
                    try:
                        question_elem = block.find_element(By.CSS_SELECTOR, "p.text-neutral-80.leading-tight.mb-8")
                        inner_p = question_elem.find_elements(By.TAG_NAME, "p")
                        if inner_p:
                            question_text = inner_p[0].text.strip()
                        else:
                            question_text = question_elem.text.strip()
                    except:
                        question_text = ""

                    if question_text:
                        print(f"\n📌 Question : {question_text}")
                    else:
                        print("❌ Question non trouvée.")
                        continue
                except:
                    print("❌ Question non trouvée.")
                    continue

                choices = []
                labels = block.find_elements(By.CSS_SELECTOR, "label.flex.items-center.justify-between")
                for label in labels:
                    try:
                        span_elements = label.find_elements(By.CSS_SELECTOR, "span.text-neutral-80 > span")
                        for span in span_elements:
                            if span.get_attribute("class") != "mr-1":
                                text = span.text.strip()
                                if text:
                                    choices.append((label, text))
                                    break
                    except:
                        continue

                if not choices:
                    print("❌ Aucune réponse trouvée.")
                    continue

                print(f"👉 Choix : {[text for _, text in choices]}")

                try:
                    if image_base64:
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "user", "content": [
                                    {"type": "text", "text": f"Regarde cette image et réponds à la question suivante : {question_text}\nChoix : {[text for _, text in choices]}\nRéponds uniquement par le texte exact du bon choix."},
                                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                                ]}
                            ]
                        )
                        answer = response.choices[0].message.content.strip()
                    elif wysiwyg_text:
                        prompt = f"Voici un texte :\n\n{wysiwyg_text}\n\nQuestion : {question_text}\nChoix : {[text for _, text in choices]}\nRéponds uniquement par le texte exact du bon choix."
                        response = client.chat.completions.create(
                            model="gpt-4.1-mini-2025-04-14",
                            messages=[{"role": "user", "content": prompt}]
                        )
                        answer = response.choices[0].message.content.strip()
                    else:
                        prompt = f"Complète la phrase suivante avec le bon mot parmi les choix :\nPhrase : {question_text}\nChoix : {[text for _, text in choices]}\nDonne uniquement le mot exact choisi, sans rien ajouter."
                        response = client.chat.completions.create(
                            model="gpt-4.1-mini-2025-04-14",
                            messages=[{"role": "user", "content": prompt}]
                        )
                        answer = response.choices[0].message.content.strip()
                except Exception as e:
                    print("❌ Erreur GPT :", e)
                    answer = None

                if not answer:
                    print("⚠️ Aucune réponse générée. ⏸ Mise en pause.")
                    paused = True
                    break

                clicked = False
                for label, text in choices:
                    if answer.lower() in text.lower() or text.lower() in answer.lower():
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", label)
                        time.sleep(2)
                        label.click()
                        print(f"✔️ Réponse cochée : {text}")
                        clicked = True
                        break

                if not clicked:
                    print(f"⚠️ Réponse IA non trouvée : {answer}")
                    paused = True
                    break

        else:
            try:
                full_text_elem = driver.find_element(By.CSS_SELECTOR, "div[data-support-id] .wysiwyg")
                full_text = full_text_elem.text.strip()
                print("📜 Texte de référence détecté.")
            except:
                full_text = ""
                print("⚠️ Aucun texte de référence détecté.")

            try:
                question_elem = driver.find_element(By.CSS_SELECTOR, "p.text-neutral-80.leading-tight.mb-8 > p")
                question_text = question_elem.text.strip()
                print(f"\n📌 Question : {question_text}")
            except:
                print("❌ Question non trouvée.")
                continue

            match = re.search(r'\((\d+)\)', question_text)
            if match:
                question_number = match.group(1)
                print(f"🔢 Question n°{question_number}")
            else:
                question_number = "?"
                print("❓ Numéro de question non détecté.")

            labels = driver.find_elements(By.CSS_SELECTOR, "label.flex.items-center.justify-between")
            choices = []
            for label in labels:
                try:
                    span_elements = label.find_elements(By.CSS_SELECTOR, "span.text-neutral-80 > span")
                    for span in span_elements:
                        if span.get_attribute("class") != "mr-1":
                            text = span.text.strip()
                            if text:
                                choices.append((label, text))
                                break
                except:
                    continue

            if not choices:
                print("❌ Aucune réponse trouvée.")
                continue

            print(f"👉 Choix : {[text for _, text in choices]}")

            if full_text:
                prompt = f"Voici un texte avec des blancs à compléter :\nTexte :\n\"\"\"{full_text}\"\"\"\n\nQuestion : {question_text}\nChoix : {[text for _, text in choices]}\nDonne uniquement le texte exact correspondant au bon choix parmi les propositions."
            else:
                prompt = f"Complète la phrase suivante avec le bon mot parmi les choix :\nPhrase : {question_text}\nChoix : {[text for _, text in choices]}\nDonne uniquement le mot exact choisi, sans rien ajouter."

            try:
                response = client.chat.completions.create(
                    model="gpt-4.1-mini-2025-04-14",
                    messages=[{"role": "user", "content": prompt}]
                )
                answer = response.choices[0].message.content.strip()
            except Exception as e:
                print("❌ Erreur GPT :", e)
                answer = None

            if not answer:
                print("⚠️ Aucune réponse générée. ⏸ Mise en pause.")
                paused = True
                continue

            clicked = False
            for label, text in choices:
                if answer.lower() in text.lower() or text.lower() in answer.lower():
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", label)
                    time.sleep(2)
                    label.click()
                    print(f"✔️ Réponse cochée (Q{question_number}) : {text}")
                    clicked = True
                    break

            if not clicked:
                print(f"⚠️ Réponse IA non trouvée : {answer}")
                paused = True
                continue

        try:
            buttons = driver.find_elements(By.CSS_SELECTOR,
                "button.button-outline-primary-large, button.button-solid-primary-large")
            clicked = False
            for btn in buttons:
                text = btn.text.strip().lower()
                if any(keyword in text for keyword in ["valider", "suivant"]):
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", btn)
                    time.sleep(2)
                    btn.click()
                    print(f"🟢 Bouton '{text}' cliqué.")
                    clicked = True
                    break
                elif "terminer" in text:
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", btn)
                    time.sleep(2)
                    btn.click()
                    print(f"✅ Quiz terminé. ⏸ Mise en pause.")
                    paused = True
                    clicked = True
                    break
            if not clicked:
                print("⚠️ Aucun bouton attendu trouvé.")
        except Exception as btn_err:
            print("❌ Erreur bouton :", btn_err)

except Exception as crash:
    print(f"\n💥 Crash : {crash}")

driver.quit()
print("🚪 Fermeture.")
