from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import webbrowser

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from time import sleep
import pulp
import itertools

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.get("https://www.google.com.br/maps")
sleep(5)
def esta_na_aba_de_rotas():
    xpath = '//button[@aria-label="Fechar rotas"]'
    botao_rotas = driver.find_elements(By.XPATH, xpath)
    return len(botao_rotas) > 0

def busca_endereco(endereco, num_caixa = 1):
    if not esta_na_aba_de_rotas():
        busca_vazia = driver.find_element(By.ID, 'searchboxinput')
        busca_vazia.clear()
        sleep(2)
        busca_vazia.send_keys(endereco)
        sleep(2)
        busca_vazia.send_keys(Keys.RETURN)
        sleep(2)
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
    rota = driver.find_element(By.XPATH, '/html/body/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[4]/div[1]/button').click()
    sleep(3)
    xpath = '//button[@aria-label="Fechar rotas"]'
    wait = WebDriverWait(driver, timeout=5)
    botao_rotas = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))


def adiciona_caixa_destino():
    xpath = '//span[text()="Adicionar destino"]'
    wait = WebDriverWait(driver,timeout=2)
    wait.until(EC.visibility_of_all_elements_located((By.XPATH,xpath)))

    adiciona_destino = driver.find_element(By.XPATH,xpath)

    adiciona_destino.click()

def seleciona_tipo_conducao(tipo_conducao="Carro"):
    xpath = f'//img[@aria-label="{tipo_conducao}"]'
    wait = WebDriverWait(driver,timeout=3)
    botao_conducao = wait.until(EC.presence_of_element_located((By.XPATH,xpath)))
    botao_conducao.click()


def retorna_tempo_total():
    xpath = '//div[@id="section-directions-trip-0"]//div[contains(text(),"min")]'
    wait = WebDriverWait(driver,timeout=3)
    elemento_tempo = wait.until(EC.presence_of_element_located((By.XPATH,xpath)))
    return int(elemento_tempo.text.replace(' min',''))

def retorna_km_total():
    xpath = '//div[@id="section-directions-trip-0"]//div[contains(text(),"km")]'
    wait = WebDriverWait(driver,timeout=3)
    elemento_tempo = wait.until(EC.presence_of_element_located((By.XPATH,xpath)))
    return float(elemento_tempo.text.replace(' km','').replace(',','.'))


#===================

def gera_pares_distancia(enderecos):
    distancia_pares = {}
    driver.get("https://www.google.com/maps")
    busca_endereco(enderecos[0], 1)
    define_rota()
    seleciona_tipo_conducao(tipo_conducao="Carro")

    for i, end1 in enumerate(enderecos):
        sleep(1)
        busca_endereco(end1, 1)
        sleep(1)
        for j, end2 in enumerate(enderecos):
            if i != j:
                sleep(1)
                busca_endereco(end2, 2)
                sleep(1)
                tempo_par = retorna_tempo_total()
                distancia_pares[f'{i}_{j}'] = tempo_par
    
    return distancia_pares
   

def gera_otimizacao(enderecos, distancia_pares):

    def distancia(end1, end2):
        return distancia_pares[f'{end1}_{end2}']
    
    prob = pulp.LpProblem('TSP', pulp.LpMinimize)

    x = pulp.LpVariable.dicts('x', [(i, j) for i in range(len(enderecos)) for j in range(len(enderecos)) if i != j], cat='Binary')

    prob += pulp.lpSum([distancia(i, j) * x[(i, j)] for i in range(len(enderecos)) for j in range(len(enderecos)) if i != j])

    for i in range(len(enderecos)):
        prob += pulp.lpSum([x[(i, j)] for j in range(len(enderecos)) if i != j]) == 1
        prob += pulp.lpSum([x[(j, i)] for j in range(len(enderecos)) if i != j]) == 1
 
    for k in range(len(enderecos)):
        for S in range(2, len(enderecos)):
            for subset in itertools.combinations([i for i in range(len(enderecos)) if i != k], S):
                prob += pulp.lpSum([x[(i, j)] for i in subset for j in subset if i != j]) <= len(subset) - 1
    
    prob.solve(pulp.PULP_CBC_CMD())

    solucao = []
    cidade_inicial = 0
    proxima_cidade = cidade_inicial
    while True:
        for j in range(len(enderecos)):
            if j != proxima_cidade and x[(proxima_cidade, j)].value() == 1:
               solucao.append((proxima_cidade, j))
               proxima_cidade = j
               break
        if proxima_cidade == cidade_inicial:
            break
    
    print('Rota:')
    for i in range(len(solucao)):
        print(solucao[i][0], ' ->> ', solucao[i][1])
    
    return solucao


def mostra_rota_otimizada(enderecos, rota):
    driver.get("https://www.google.com/maps")

    busca_endereco(enderecos[0], 1)
    define_rota()

    for i in range(len(rota)):
        busca_endereco(enderecos[rota[i][0]], i+1)
        adiciona_caixa_destino()
    
    busca_endereco(enderecos[0], len(enderecos) + 1)
    

if __name__ == "__main__":
    enderecos = [
                "ST Setor Terminal Norte, Lote J, S/N - Asa Norte, Brasília - DF, 70770-916", 
                "St Setor Terminal Norte, Lote J, S/N Asa Norte 512/513 - Asa Norte, Brasília - DF, 70297-400",  
                "Asa Norte Entrequadra Norte 504/505 Bloco A - Asa Norte, Brasília - DF, 70760-545", 
                "Shc/sul Eq, 402/403 - Asa Sul, Brasília - DF, 70236-400", 
                "Shc/sul EQ, 310 BL A - Asa Sul, Brasília - DF, 70364-400",
                "SCEE / Sul Lote B - Guará, Brasília - DF, 71215-300",
                "SHI/SUL QI 13 Bloco J - Lago Sul, Brasília - DF, 71635-013",
                "Shis QI, DF-025, Lote, G - Lago Sul, Brasília - DF, 71660-200",
                "R. Copaíba, S/N - Lote 01 Mezanino 1B Loja 1B Norte - Águas Claras, Brasília - DF, 70297-400"
    ]


    distancia_pares = gera_pares_distancia(enderecos)
    rota_correta = gera_otimizacao(enderecos,distancia_pares)

    mostra_rota_otimizada(enderecos,rota_correta)
    sleep(600)




