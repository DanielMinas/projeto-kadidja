from selenium import webdriver
from selenium.webdriver.chrome.service import Service
#from webdriver_manager.chrome import ChromeDriverManager
#from webdriver_manager.firefox import GeckoDriverManager
import webbrowser

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from time import sleep


#service = Service(ChromeDriverManager().install())
#driver = webdriver.Chrome(service=service)
gecko_path = r'geckodriver.exe'
driver = webdriver.Firefox(executable_path=gecko_path)
driver.get("https://www.google.com.br/maps")
#webbrowser.open("https://www.google.com.br/maps")
sleep(5)
def esta_na_aba_de_rotas():
    xpath = '//button[@aria-label="Fechar rotas"]'
    botao_rotas = driver.find_elements(By.XPATH, xpath)
    return len(botao_rotas) > 0

def busca_endereco(endereco, num_caixa = 1):
    if not esta_na_aba_de_rotas():
        busca_vazia = driver.find_element(By.ID, 'searchboxinput')
        busca_vazia.clear()
        sleep(1)
        busca_vazia.send_keys(endereco)
        sleep(1)
        busca_vazia.send_keys(Keys.RETURN)
        sleep(1)
    else:
        caixas = driver.find_elements(By.XPATH, '//div[contains(@id, "directions-searchbox")]//input')
        caixas = [c for c in caixas if c.is_displayed()]
        if len(caixas) >= num_caixa:
            caixa_endereço = caixas[num_caixa-1]
            caixa_endereço.send_keys(Keys.CONTROL + 'a')
            caixa_endereço.send_keys(Keys.DELETE)
            caixa_endereço.send_keys(endereco)
            caixa_endereço.send_keys(Keys.RETURN)
        else:
            print(f'Não conseguimos adicionar o endereço {len (caixas)}|{num_caixa}')

def define_rota():
    #xpath = '//button[@aria-label="Fechar rotas"]'
    #botao_rotas = driver.find_element(By.XPATH, xpath)
    #botao_rotas.click()
    sleep(3)
    rota = driver.find_element(By.XPATH, '/html/body/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[4]/div[1]/button').click()
    sleep(3)

    #Este codigo é feito para que a automação continue depois dele ter clicado no botão rotas
    xpath = '//button[@aria-label="Fechar rotas"]'
    wait = WebDriverWait(driver, timeout=5)
    botao_rotas = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    #wait = WebDriverWait(driver, timeout=5)
    #rota = wait.until(EC.presence_of_element_located(By.XPATH, '/html/body/div[3]/div[8]/div[3]/div[1]/div[2]/div/div[2]/div/button'))

if __name__ == "__main__":
    enderecos = [
                "Av. José Bonifácio, 245 - Farroupilha, Porto Alegre - RS, 90040-130",  #Redenção
                "Av. Borges de Medeiros, 2035 - Menino Deus, Porto Alegre - RS, 90110-150",  #Marinha
                "Av. Guaíba, 544 - Ipanema, Porto Alegre - RS, 91760-740", #Orla Ipanema
                "Av. Padre Cacique, 2000 - Praia de Belas, Porto Alegre - RS, 90810-180", # Iberê
                ]
    busca_endereco(enderecos[0], 1)
    define_rota()

    busca_endereco(enderecos[0], 1)
    busca_endereco(enderecos[1], 2)




