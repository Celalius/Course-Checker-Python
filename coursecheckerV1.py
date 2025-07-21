
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def extract_courses():
    print(f"Yazdırılan excel dersleri:")
    ceng_courses = set()
    excel_path = "dersler.xlsx"


    df = pd.read_excel(excel_path)
    
    for index, row in df.iterrows():

        if 'CEC' in str(row['DERS']):#-----------------------------------------------!
            course_code = str(row['DERS']).strip()
            if(course_code[3] != " "):
                course_code = course_code[:3] + " " + course_code[3:]
            course_code = course_code.lower()
            print(course_code)

            if row['CENG'] == 'X': #-----------------------------------------------!
                ceng_courses.add(course_code)


    print("Bölümünüz için uygun dersler:")
    print(ceng_courses)
    
    return ceng_courses if ceng_courses else set()

def get_courses_from_web():
    url = "https://www.cankaya.edu.tr/dersler/"
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get(url)
    time.sleep(2)
    
    try:

        dropdown = driver.find_element(By.NAME, "DersCode")
        
        dropdown.send_keys("CEC") #-----------------------------------------------!
        
        dropdown.send_keys(Keys.RETURN)
        time.sleep(3)
        
        print(f"Yazdırılan Webdeki dersler")
        courses = set()
        table_rows = driver.find_elements(By.XPATH, "//tr[@role='row']")
        for row in table_rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            
            if cols and "CEC" in cols[0].text: #-----------------------------------------------!
                
                course_code = cols[0].text.replace("\u00a0", "").strip().lower()  # Özel boşluk karakterlerini düzelt ve normalleştir
                print(course_code)
                courses.add(course_code)
        
        driver.quit()
        return courses if courses else set()  # Boş set dönerek None hatasını önle
    except Exception as e:
        print(f"Web scraping sırasında hata oluştu: {e}")
        driver.quit()
        return set()

courses = extract_courses()
web_courses = get_courses_from_web()


if not courses:
    print("PDF'den hiç ders bulunamadı!")
if not web_courses:
    print("Webte hiç ders bulunamadı!")

common_courses = courses.intersection(web_courses)

print("\n Alabileceğin seçmeli dersleri:")
for course in common_courses:
    print(course)
